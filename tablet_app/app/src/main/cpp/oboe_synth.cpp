// Native MIDI → audio synthesizer for HarpHymnal.
//
// Replaces the Java AudioTrack synth (MidiPlaythrough.java) with a
// C++/Oboe pipeline so we can:
//   1. Hit sub-10 ms end-to-end latency (Oboe → AAudio Exclusive mode on
//      API 26+, OpenSL ES fallback elsewhere).
//   2. Render audio on a thread that's immune to Java GC pauses.
//   3. Use a lock-free SPSC event queue between the MIDI (JNI) thread and
//      the audio callback — eliminates the stuck-tone race where the Java
//      synth's audio thread could overwrite the MIDI thread's RELEASE
//      with a stale local snapshot at end-of-block.
//
// Voice model: 16-voice polyphony, triangle wave, linear A/R envelope
// (5 ms attack, 250 ms release). Same audible character as the Java
// version, just routed through a tighter audio pipe.
//
// JNI surface (called by OboeSynth.java):
//   nativeStart()          — start Oboe stream
//   nativeStop()           — stop + close
//   nativeNoteOn(n,v)      — queue note-on event
//   nativeNoteOff(n)       — queue note-off event
//   nativeAllNotesOff()    — kill every active voice
//   nativeGetLatencyMs()   — Oboe-reported end-to-end latency, for the
//                            home-grid banner.

#include <atomic>
#include <array>
#include <cmath>
#include <cstdint>
#include <jni.h>
#include <android/log.h>
#include <oboe/Oboe.h>

#define TAG "OboeSynth"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN,  TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

namespace {

constexpr int   kPolyphony   = 16;
constexpr float kMasterGain  = 0.18f;   // headroom for 16 voices
constexpr float kAttackSec   = 0.005f;
constexpr float kReleaseSec  = 0.25f;
constexpr int   kQueueSize   = 256;     // must be power of two

enum class Stage : uint8_t { Idle, Attack, Sustain, Release };

struct Voice {
    Stage stage = Stage::Idle;
    int   note  = -1;
    float freq  = 0.0f;
    float phase = 0.0f;
    float env   = 0.0f;
    float amp   = 0.0f;
};

enum class EvKind : uint8_t { NoteOn, NoteOff, AllOff };
struct Event {
    EvKind kind;
    uint8_t note;
    uint8_t vel;
};

// Lock-free single-producer (JNI/MIDI thread) single-consumer (audio
// callback) ring buffer. Sized as a power of two so we can use a cheap
// bitmask instead of modulus.
class EventQueue {
public:
    bool push(const Event& e) {
        size_t w = w_.load(std::memory_order_relaxed);
        size_t r = r_.load(std::memory_order_acquire);
        if (((w + 1) & (kQueueSize - 1)) == (r & (kQueueSize - 1))) {
            return false;  // full
        }
        buf_[w & (kQueueSize - 1)] = e;
        w_.store(w + 1, std::memory_order_release);
        return true;
    }
    bool pop(Event& out) {
        size_t r = r_.load(std::memory_order_relaxed);
        size_t w = w_.load(std::memory_order_acquire);
        if ((r & (kQueueSize - 1)) == (w & (kQueueSize - 1))) {
            return false;  // empty
        }
        out = buf_[r & (kQueueSize - 1)];
        r_.store(r + 1, std::memory_order_release);
        return true;
    }
private:
    std::array<Event, kQueueSize> buf_{};
    std::atomic<size_t> w_{0};
    std::atomic<size_t> r_{0};
};

class Synth : public oboe::AudioStreamDataCallback {
public:
    bool start() {
        if (stream_) return true;
        oboe::AudioStreamBuilder b;
        b.setDirection(oboe::Direction::Output);
        b.setPerformanceMode(oboe::PerformanceMode::LowLatency);
        b.setSharingMode(oboe::SharingMode::Exclusive);   // fall through to Shared if denied
        b.setFormat(oboe::AudioFormat::Float);
        b.setChannelCount(oboe::ChannelCount::Mono);
        b.setUsage(oboe::Usage::Media);
        b.setContentType(oboe::ContentType::Music);
        b.setDataCallback(this);

        oboe::Result r = b.openStream(stream_);
        if (r != oboe::Result::OK) {
            LOGE("openStream: %s", oboe::convertToText(r));
            stream_.reset();
            return false;
        }
        sampleRate_   = stream_->getSampleRate();
        invSampleRate_ = 1.0f / float(sampleRate_);
        attackPerFrame_  = 1.0f / (kAttackSec  * float(sampleRate_));
        releasePerFrame_ = 1.0f / (kReleaseSec * float(sampleRate_));

        LOGI("Oboe stream: sr=%d, frames/burst=%d, sharing=%s, perf=%s",
             sampleRate_, stream_->getFramesPerBurst(),
             oboe::convertToText(stream_->getSharingMode()),
             oboe::convertToText(stream_->getPerformanceMode()));

        // Buffer size: 2 bursts → typical 10 ms total at 240 Hz framerate.
        stream_->setBufferSizeInFrames(stream_->getFramesPerBurst() * 2);

        r = stream_->requestStart();
        if (r != oboe::Result::OK) {
            LOGE("requestStart: %s", oboe::convertToText(r));
            stream_->close();
            stream_.reset();
            return false;
        }
        return true;
    }

    void stop() {
        if (!stream_) return;
        // Drain voices so the last buffer isn't a tone holding open.
        for (auto& v : voices_) v.stage = Stage::Idle;
        stream_->stop();
        stream_->close();
        stream_.reset();
    }

    void noteOn(uint8_t note, uint8_t vel) {
        queue_.push({EvKind::NoteOn, note, vel});
        noteOnCount_.fetch_add(1, std::memory_order_relaxed);
    }
    void noteOff(uint8_t note) { queue_.push({EvKind::NoteOff, note, 0}); }
    void allNotesOff()         { queue_.push({EvKind::AllOff, 0, 0}); }

    int noteOnCount() const { return noteOnCount_.load(std::memory_order_relaxed); }

    double latencyMs() {
        if (!stream_) return 0.0;
        auto res = stream_->calculateLatencyMillis();
        return res ? res.value() : 0.0;
    }

    oboe::DataCallbackResult onAudioReady(oboe::AudioStream* /*s*/,
                                          void* audioData,
                                          int32_t numFrames) override {
        // Drain queue at start of block (audio thread side of the SPSC).
        Event e;
        while (queue_.pop(e)) {
            switch (e.kind) {
                case EvKind::NoteOn:  handleNoteOn(e.note, e.vel); break;
                case EvKind::NoteOff: handleNoteOff(e.note);       break;
                case EvKind::AllOff:  handleAllOff();               break;
            }
        }

        float* out = static_cast<float*>(audioData);
        for (int i = 0; i < numFrames; i++) out[i] = 0.0f;

        for (auto& v : voices_) {
            if (v.stage == Stage::Idle) continue;
            float phase = v.phase;
            float phaseInc = v.freq * invSampleRate_;
            float env = v.env;
            Stage st = v.stage;
            for (int i = 0; i < numFrames; i++) {
                if (st == Stage::Attack) {
                    env += attackPerFrame_;
                    if (env >= 1.0f) { env = 1.0f; st = Stage::Sustain; }
                } else if (st == Stage::Release) {
                    env -= releasePerFrame_;
                    if (env <= 0.0f) { env = 0.0f; st = Stage::Idle; break; }
                }
                float tri = 4.0f * std::fabs(phase - std::floor(phase + 0.5f)) - 1.0f;
                out[i] += tri * env * v.amp;
                phase += phaseInc;
                if (phase >= 1.0f) phase -= 1.0f;
            }
            v.phase = phase;
            v.env = env;
            v.stage = st;
        }

        // Soft clip + master gain.
        for (int i = 0; i < numFrames; i++) {
            float s = out[i] * kMasterGain;
            if (s >  1.0f) s =  1.0f;
            if (s < -1.0f) s = -1.0f;
            s = 1.5f * s - 0.5f * s * s * s;   // Chebyshev soft clip
            out[i] = s;
        }
        return oboe::DataCallbackResult::Continue;
    }

private:
    void handleNoteOn(uint8_t note, uint8_t vel) {
        Voice* target = nullptr;
        for (auto& v : voices_) if (v.stage == Stage::Idle) { target = &v; break; }
        if (!target) for (auto& v : voices_) if (v.stage == Stage::Release) { target = &v; break; }
        if (!target) target = &voices_[0];

        target->note  = note;
        target->freq  = 440.0f * std::pow(2.0f, (float(note) - 69.0f) / 12.0f);
        target->phase = 0.0f;
        target->amp   = float(vel) / 127.0f;
        target->env   = 0.0f;
        target->stage = Stage::Attack;
    }
    void handleNoteOff(uint8_t note) {
        for (auto& v : voices_) {
            if (v.note == note && v.stage != Stage::Idle && v.stage != Stage::Release) {
                v.stage = Stage::Release;
            }
        }
    }
    void handleAllOff() {
        for (auto& v : voices_) if (v.stage != Stage::Idle) v.stage = Stage::Release;
    }

    std::shared_ptr<oboe::AudioStream> stream_;
    int   sampleRate_ = 48000;
    float invSampleRate_ = 1.0f / 48000.0f;
    float attackPerFrame_ = 0.0f;
    float releasePerFrame_ = 0.0f;

    EventQueue queue_;
    std::array<Voice, kPolyphony> voices_{};
    std::atomic<int> noteOnCount_{0};
};

Synth g_synth;

}  // namespace

extern "C" {

JNIEXPORT jboolean JNICALL
Java_com_harp_harphymnal_drills_OboeSynth_nativeStart(JNIEnv*, jclass) {
    return g_synth.start() ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT void JNICALL
Java_com_harp_harphymnal_drills_OboeSynth_nativeStop(JNIEnv*, jclass) {
    g_synth.stop();
}

JNIEXPORT void JNICALL
Java_com_harp_harphymnal_drills_OboeSynth_nativeNoteOn(JNIEnv*, jclass,
                                                      jint note, jint vel) {
    g_synth.noteOn((uint8_t)(note & 0x7F), (uint8_t)(vel & 0x7F));
}

JNIEXPORT void JNICALL
Java_com_harp_harphymnal_drills_OboeSynth_nativeNoteOff(JNIEnv*, jclass,
                                                       jint note) {
    g_synth.noteOff((uint8_t)(note & 0x7F));
}

JNIEXPORT void JNICALL
Java_com_harp_harphymnal_drills_OboeSynth_nativeAllNotesOff(JNIEnv*, jclass) {
    g_synth.allNotesOff();
}

JNIEXPORT jint JNICALL
Java_com_harp_harphymnal_drills_OboeSynth_nativeNoteOnCount(JNIEnv*, jclass) {
    return (jint) g_synth.noteOnCount();
}

JNIEXPORT jdouble JNICALL
Java_com_harp_harphymnal_drills_OboeSynth_nativeLatencyMs(JNIEnv*, jclass) {
    return (jdouble) g_synth.latencyMs();
}

}  // extern "C"
