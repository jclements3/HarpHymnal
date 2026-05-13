package com.harp.harphymnal.drills;

/**
 * Java side of the native Oboe-backed synth. Loads libharphymnal_synth.so
 * once and exposes the JNI surface as static methods. Concurrency-safe:
 * the C++ side uses a lock-free SPSC queue, so MIDI events from any
 * thread land in the audio callback without locks.
 */
public final class OboeSynth {
    static {
        System.loadLibrary("harphymnal_synth");
    }

    private OboeSynth() {}

    public static native boolean nativeStart();
    public static native void    nativeStop();
    public static native void    nativeNoteOn(int note, int velocity);
    public static native void    nativeNoteOff(int note);
    public static native void    nativeAllNotesOff();
    public static native int     nativeNoteOnCount();
    public static native double  nativeLatencyMs();
}
