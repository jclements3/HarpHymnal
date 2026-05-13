package com.harp.harphymnal.drills;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.media.midi.MidiDevice;
import android.media.midi.MidiDeviceInfo;
import android.media.midi.MidiManager;
import android.media.midi.MidiOutputPort;
import android.media.midi.MidiReceiver;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Foreground service that owns the native Oboe synth and the MidiManager
 * device callback. Runs independent of MainActivity / the WebView — plug
 * the keyboard in, hear sound, even if HarpHymnal's UI is closed.
 *
 * Lifecycle:
 *   - Started by MainActivity on app open, OR by UsbMidiAttachActivity
 *     when Android delivers a USB_DEVICE_ATTACHED intent.
 *   - Promotes itself to a foreground service with a persistent
 *     notification + a Stop action.
 *   - Stays alive until the user taps Stop or the system kills it.
 *
 * Why a service and not just MainActivity: USB MIDI hardware is shared
 * across the device — the user expects "plug in → play" regardless of
 * which app happens to be in the foreground.
 */
public class MidiSynthService extends Service {
    private static final String TAG = "MidiSynthService";
    private static final String CHANNEL_ID = "harphymnal.midi";
    private static final int NOTIF_ID = 4711;

    public static final String ACTION_START = "com.harp.harphymnal.drills.MIDI_START";
    public static final String ACTION_STOP  = "com.harp.harphymnal.drills.MIDI_STOP";

    private MidiManager midi;
    private final List<MidiDevice> openDevices = new ArrayList<>();
    private boolean synthRunning = false;

    @Override
    public void onCreate() {
        super.onCreate();
        ensureChannel();
        startForeground(NOTIF_ID, buildNotification("starting…"));
        if (OboeSynth.nativeStart()) {
            synthRunning = true;
            Log.i(TAG, "Oboe synth started");
            pushStatus("synth started");
        } else {
            Log.e(TAG, "OboeSynth.nativeStart() returned false");
            pushStatus("synth start failed");
        }
        midi = (MidiManager) getSystemService(Context.MIDI_SERVICE);
        if (midi != null) {
            rescan();
            midi.registerDeviceCallback(deviceCallback,
                new Handler(Looper.getMainLooper()));
            if (openDevices.isEmpty()) pushStatus("no device");
        } else {
            pushStatus("no MidiManager");
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            stopSelf();
            return START_NOT_STICKY;
        }
        // Refresh device scan in case we were started by a USB-attach
        // intent right after a device appeared.
        if (midi != null) rescan();
        updateNotification(currentSummary());
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        if (midi != null) {
            try { midi.unregisterDeviceCallback(deviceCallback); } catch (Throwable ignored) {}
        }
        for (MidiDevice d : openDevices) {
            try { d.close(); } catch (IOException ignored) {}
        }
        openDevices.clear();
        if (synthRunning) {
            OboeSynth.nativeAllNotesOff();
            OboeSynth.nativeStop();
            synthRunning = false;
        }
        pushStatus("stopped");
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }

    // ─── Device callback ────────────────────────────────────────────────────
    private final MidiManager.DeviceCallback deviceCallback =
        new MidiManager.DeviceCallback() {
            @Override public void onDeviceAdded(MidiDeviceInfo info)   { openOne(info); }
            @Override public void onDeviceRemoved(MidiDeviceInfo info) {
                // Cable yanked mid-note → no note-off arrives. Native synth
                // kills every voice via its lock-free queue, no race with
                // the audio callback this time.
                if (synthRunning) OboeSynth.nativeAllNotesOff();
                String name = info.getProperties()
                    .getString(MidiDeviceInfo.PROPERTY_NAME);
                pushStatus("disconnected (" + (name != null ? name : "?") + ")");
                updateNotification("disconnected");
            }
        };

    private void rescan() {
        for (MidiDeviceInfo info : midi.getDevices()) openOne(info);
    }

    private void openOne(MidiDeviceInfo info) {
        // Filter to external USB peripherals only — skip the tablet's own
        // "Android USB Peripheral Port" loopback, virtual MIDI devices,
        // and Bluetooth (lag).
        if (info.getType() != MidiDeviceInfo.TYPE_USB) return;
        if (info.getOutputPortCount() == 0) return;
        String name = info.getProperties().getString(MidiDeviceInfo.PROPERTY_NAME);
        if (name != null && name.toLowerCase().contains("peripheral")) {
            Log.i(TAG, "skipping " + name);
            return;
        }
        midi.openDevice(info, dev -> {
            if (dev == null) {
                pushStatus("openDevice null (" + name + ")");
                return;
            }
            openDevices.add(dev);
            int total = info.getOutputPortCount();
            int opened = 0;
            for (int p = 0; p < total; p++) {
                MidiOutputPort port = dev.openOutputPort(p);
                if (port != null) {
                    port.connect(new SynthReceiver());
                    opened++;
                }
            }
            Log.i(TAG, "connected " + name + " " + opened + "/" + total);
            pushStatus("connected: " + name + " · " + opened + "/" + total + " ports");
            double lat = OboeSynth.nativeLatencyMs();
            updateNotification(name + " · " + String.format("%.1f ms", lat));
        }, new Handler(Looper.getMainLooper()));
    }

    // ─── MIDI receiver — parses bytes, forwards to native ───────────────────
    private class SynthReceiver extends MidiReceiver {
        @Override
        public void onSend(byte[] msg, int offset, int count, long timestamp) {
            int i = offset, end = offset + count;
            while (i < end) {
                int status = msg[i] & 0xFF;
                int type = status & 0xF0;
                if (type == 0x90 || type == 0x80) {
                    if (i + 2 >= end) break;
                    int note = msg[i + 1] & 0x7F;
                    int vel  = msg[i + 2] & 0x7F;
                    if (type == 0x90 && vel > 0) OboeSynth.nativeNoteOn(note, vel);
                    else                          OboeSynth.nativeNoteOff(note);
                    i += 3;
                } else if (type == 0xB0) {
                    if (i + 2 >= end) break;
                    int cc = msg[i + 1] & 0x7F;
                    if (cc == 120 || cc == 123) OboeSynth.nativeAllNotesOff();
                    i += 3;
                } else if (type == 0xC0 || type == 0xD0) {
                    i += 2;
                } else if (type == 0xE0) {
                    i += 3;
                } else {
                    i += 1;
                }
            }
        }
    }

    // ─── Notification glue ─────────────────────────────────────────────────
    private void ensureChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm == null) return;
        NotificationChannel ch = new NotificationChannel(CHANNEL_ID,
            "HarpHymnal MIDI synth", NotificationManager.IMPORTANCE_LOW);
        ch.setShowBadge(false);
        nm.createNotificationChannel(ch);
    }

    private Notification buildNotification(String summary) {
        Intent open = new Intent(this, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent openPi = PendingIntent.getActivity(this, 0, open,
            PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Intent stop = new Intent(this, MidiSynthService.class);
        stop.setAction(ACTION_STOP);
        PendingIntent stopPi = PendingIntent.getService(this, 0, stop,
            PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Notification.Builder b = (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
            ? new Notification.Builder(this, CHANNEL_ID)
            : new Notification.Builder(this);
        return b
            .setContentTitle("HarpHymnal MIDI synth")
            .setContentText(summary)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setOngoing(true)
            .setContentIntent(openPi)
            .addAction(android.R.drawable.ic_media_pause, "Stop", stopPi)
            .build();
    }

    private void updateNotification(String summary) {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm == null) return;
        nm.notify(NOTIF_ID, buildNotification(summary));
    }

    private String currentSummary() {
        int connected = openDevices.size();
        if (connected == 0) return "no device";
        return connected + " device" + (connected == 1 ? "" : "s") + " connected";
    }

    // ─── WebView status banner (same wire as before) ───────────────────────
    private void pushStatus(String msg) {
        String esc = msg == null ? "" :
            msg.replace("\\", "\\\\").replace("'", "\\'");
        MainActivity.runJsInActiveWebView(
            "if (window.onMidiStatus) window.onMidiStatus('" + esc + "');");
    }
}
