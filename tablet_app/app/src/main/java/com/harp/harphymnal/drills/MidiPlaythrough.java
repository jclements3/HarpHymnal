package com.harp.harphymnal.drills;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.media.midi.MidiDevice;
import android.media.midi.MidiDeviceInfo;
import android.media.midi.MidiInputPort;
import android.media.midi.MidiManager;
import android.media.midi.MidiOutputPort;
import android.media.midi.MidiReceiver;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * USB-MIDI keyboard → built-in polyphonic synth → AudioTrack speakers/headphones.
 *
 * Designed for low-latency playthrough on the P90: when a class-compliant
 * MIDI keyboard (e.g. SMK-37 PRO) is plugged into the tablet's USB-C port
 * in host mode, every note-on/off arrives in ~5-15 ms at the speaker.
 *
 * Synth voice = triangle wave with linear attack / linear release envelope.
 * Polyphony 16. Sounds like a synth pad, not a piano — sufficient to
 * confirm the cable path works and to play scales/chords audibly. Swap to
 * a SoundFont engine (FluidSynth-JNI) later if a real piano timbre matters.
 *
 * Lifecycle: instantiate in Activity.onCreate, call start(), and stop()
 * from onDestroy. All public methods are main-thread safe; the synth
 * runs on its own audio thread.
 */
public class MidiPlaythrough {
    private static final String TAG = "MidiPlaythrough";

    // ─── Audio config ─────────────────────────────────────────────────────
    private static final int SAMPLE_RATE = 44_100;
    private static final int CHANNELS = AudioFormat.CHANNEL_OUT_MONO;
    private static final int ENCODING = AudioFormat.ENCODING_PCM_16BIT;
    private static final int POLYPHONY = 16;
    private static final float MASTER_GAIN = 0.18f;     // headroom for 16 voices
    private static final float ATTACK_SEC  = 0.005f;    // 5 ms
    private static final float RELEASE_SEC = 0.25f;     // 250 ms

    // ─── State ────────────────────────────────────────────────────────────
    private final Context ctx;
    private MidiManager midi;
    private AudioTrack track;
    private Thread audioThread;
    private volatile boolean running = false;
    private final Voice[] voices = new Voice[POLYPHONY];
    private final List<MidiDevice> openDevices = new ArrayList<>();

    public MidiPlaythrough(Context ctx) {
        this.ctx = ctx.getApplicationContext();
        for (int i = 0; i < POLYPHONY; i++) voices[i] = new Voice();
    }

    // ─── Lifecycle ────────────────────────────────────────────────────────
    public void start() {
        if (running) return;
        midi = (MidiManager) ctx.getSystemService(Context.MIDI_SERVICE);
        if (midi == null) {
            Log.w(TAG, "MidiManager unavailable on this device");
            return;
        }

        int minBuf = AudioTrack.getMinBufferSize(SAMPLE_RATE, CHANNELS, ENCODING);
        int bufBytes = Math.max(minBuf, 2048);
        track = new AudioTrack.Builder()
            .setAudioAttributes(new AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                .build())
            .setAudioFormat(new AudioFormat.Builder()
                .setSampleRate(SAMPLE_RATE)
                .setEncoding(ENCODING)
                .setChannelMask(CHANNELS)
                .build())
            .setBufferSizeInBytes(bufBytes)
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build();

        track.play();
        running = true;
        audioThread = new Thread(this::audioLoop, "MidiSynth-audio");
        audioThread.setPriority(Thread.MAX_PRIORITY);
        audioThread.start();

        // Open every currently-connected MIDI device and listen for new ones.
        rescanDevices();
        midi.registerDeviceCallback(deviceCallback, new Handler(Looper.getMainLooper()));
    }

    public void stop() {
        running = false;
        if (midi != null) midi.unregisterDeviceCallback(deviceCallback);
        for (MidiDevice d : openDevices) {
            try { d.close(); } catch (IOException ignored) {}
        }
        openDevices.clear();
        try {
            if (audioThread != null) audioThread.join(500);
        } catch (InterruptedException ignored) {}
        if (track != null) {
            try { track.stop(); track.release(); } catch (Exception ignored) {}
            track = null;
        }
    }

    // ─── Device discovery ─────────────────────────────────────────────────
    private final MidiManager.DeviceCallback deviceCallback =
        new MidiManager.DeviceCallback() {
            @Override public void onDeviceAdded(MidiDeviceInfo info)   { openOne(info); }
            @Override public void onDeviceRemoved(MidiDeviceInfo info) { /* no-op */ }
        };

    private void rescanDevices() {
        MidiDeviceInfo[] infos = midi.getDevices();
        for (MidiDeviceInfo info : infos) openOne(info);
    }

    private void openOne(MidiDeviceInfo info) {
        // We only consume devices that have at least one OUTPUT port
        // (sender of notes — i.e. a keyboard sending events to us).
        if (info.getOutputPortCount() == 0) return;
        midi.openDevice(info, dev -> {
            if (dev == null) { Log.w(TAG, "openDevice returned null for " + info); return; }
            openDevices.add(dev);
            MidiOutputPort port = dev.openOutputPort(0);
            if (port == null) { Log.w(TAG, "openOutputPort failed for " + info); return; }
            port.connect(new SynthReceiver());
            Log.i(TAG, "MIDI device connected: " + info.getProperties().getString(
                MidiDeviceInfo.PROPERTY_NAME));
        }, new Handler(Looper.getMainLooper()));
    }

    // ─── MIDI receiver ────────────────────────────────────────────────────
    private class SynthReceiver extends MidiReceiver {
        @Override
        public void onSend(byte[] msg, int offset, int count, long timestamp) {
            // Iterate the buffer in case multiple MIDI messages were batched.
            int i = offset;
            int end = offset + count;
            while (i < end) {
                int status = msg[i] & 0xFF;
                int type = status & 0xF0;
                if (type == 0x90 || type == 0x80) {
                    if (i + 2 >= end) break;
                    int note = msg[i + 1] & 0x7F;
                    int vel  = msg[i + 2] & 0x7F;
                    if (type == 0x90 && vel > 0) noteOn(note, vel);
                    else                          noteOff(note);
                    i += 3;
                } else if (type == 0xB0) {
                    if (i + 2 >= end) break;
                    int cc = msg[i + 1] & 0x7F;
                    if (cc == 120 || cc == 123) allNotesOff();
                    i += 3;
                } else if (type == 0xC0 || type == 0xD0) {
                    i += 2;
                } else if (type == 0xE0) {
                    i += 3;
                } else {
                    i += 1;  // System / unknown — skip one byte and resync.
                }
            }
        }
    }

    // ─── Voice allocation ─────────────────────────────────────────────────
    private void noteOn(int note, int vel) {
        // Prefer an idle voice; otherwise steal the oldest-released one;
        // otherwise just overwrite the first slot.
        Voice target = null;
        for (Voice v : voices) {
            if (v.stage == VoiceStage.IDLE) { target = v; break; }
        }
        if (target == null) {
            long oldest = Long.MAX_VALUE;
            for (Voice v : voices) {
                if (v.stage == VoiceStage.RELEASE && v.startedFrame < oldest) {
                    oldest = v.startedFrame;
                    target = v;
                }
            }
        }
        if (target == null) target = voices[0];

        target.note = note;
        target.freq = 440f * (float) Math.pow(2.0, (note - 69) / 12.0);
        target.phase = 0f;
        target.amp = vel / 127f;
        target.env = 0f;
        target.stage = VoiceStage.ATTACK;
        target.startedFrame = frame;
    }

    private void noteOff(int note) {
        for (Voice v : voices) {
            if (v.note == note && v.stage != VoiceStage.IDLE && v.stage != VoiceStage.RELEASE) {
                v.stage = VoiceStage.RELEASE;
            }
        }
    }

    private void allNotesOff() {
        for (Voice v : voices) {
            if (v.stage != VoiceStage.IDLE) v.stage = VoiceStage.RELEASE;
        }
    }

    // ─── Audio rendering ──────────────────────────────────────────────────
    private long frame = 0;
    private static final int BLOCK_FRAMES = 256;
    private final float[] mix = new float[BLOCK_FRAMES];
    private final short[] pcm = new short[BLOCK_FRAMES];

    private void audioLoop() {
        float invSr = 1f / SAMPLE_RATE;
        float attackPerFrame  = 1f / (ATTACK_SEC  * SAMPLE_RATE);
        float releasePerFrame = 1f / (RELEASE_SEC * SAMPLE_RATE);
        while (running) {
            for (int i = 0; i < BLOCK_FRAMES; i++) mix[i] = 0f;

            for (Voice v : voices) {
                if (v.stage == VoiceStage.IDLE) continue;
                float phase = v.phase;
                float phaseInc = v.freq * invSr;
                float env = v.env;
                VoiceStage st = v.stage;
                for (int i = 0; i < BLOCK_FRAMES; i++) {
                    // Envelope step
                    if (st == VoiceStage.ATTACK) {
                        env += attackPerFrame;
                        if (env >= 1f) { env = 1f; st = VoiceStage.SUSTAIN; }
                    } else if (st == VoiceStage.RELEASE) {
                        env -= releasePerFrame;
                        if (env <= 0f) { env = 0f; st = VoiceStage.IDLE; break; }
                    }
                    // Triangle wave: 4|x-floor(x+0.5)| - 1, where x = phase
                    float tri = 4f * Math.abs(phase - (float) Math.floor(phase + 0.5f)) - 1f;
                    mix[i] += tri * env * v.amp;
                    phase += phaseInc;
                    if (phase >= 1f) phase -= 1f;
                }
                v.phase = phase;
                v.env = env;
                v.stage = st;
            }

            // Soft clip + convert to int16.
            for (int i = 0; i < BLOCK_FRAMES; i++) {
                float s = mix[i] * MASTER_GAIN;
                if (s >  1f) s =  1f;
                if (s < -1f) s = -1f;
                // Cheap tanh-ish soft clip via 1.5x - 0.5x^3 (Chebyshev).
                s = 1.5f * s - 0.5f * s * s * s;
                pcm[i] = (short) (s * 32767f);
            }
            frame += BLOCK_FRAMES;
            try {
                if (track != null) track.write(pcm, 0, BLOCK_FRAMES);
            } catch (Exception e) {
                Log.w(TAG, "AudioTrack.write failed", e);
                break;
            }
        }
    }

    private enum VoiceStage { IDLE, ATTACK, SUSTAIN, RELEASE }

    private static final class Voice {
        VoiceStage stage = VoiceStage.IDLE;
        int note = -1;
        float freq = 0f;
        float phase = 0f;
        float env = 0f;
        float amp = 0f;
        long startedFrame = 0L;
    }
}
