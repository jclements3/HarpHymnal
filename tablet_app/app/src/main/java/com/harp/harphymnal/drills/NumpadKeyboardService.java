package com.harp.harphymnal.drills;

import android.content.res.Resources;
import android.inputmethodservice.InputMethodService;
import android.util.TypedValue;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.widget.Button;

/**
 * Minimal soft keyboard for the lab tablet -- 5x12 QWERTY block on the
 * left, 5x4 numpad on the right. Buttons in keyboard_view.xml each carry
 * an android:tag identifying the action; this service walks the view
 * tree once and hooks click handlers based on those tags.
 *
 * Modifier keys (Shift, Ctrl, Alt) are sticky-once: tap a modifier, the
 * next character is sent with that modifier and the modifier clears.
 *
 * Special tags:
 *   BKSP  ENTER  TAB  ESC  SPACE
 *   LEFT  RIGHT  UP  DOWN
 *   SHIFT  CTRL  ALT
 *
 * Anything else is treated as a literal character to commit.
 */
public class NumpadKeyboardService extends InputMethodService {

    private boolean shifted = false;
    private boolean ctrl    = false;
    private boolean alt     = false;
    private View keyboardView;

    @Override
    public View onCreateInputView() {
        keyboardView = getLayoutInflater().inflate(R.layout.keyboard_view, null);
        // Force the keyboard view to exactly KEYBOARD_HEIGHT_DP regardless
        // of how the IME framework would otherwise size it. Without this
        // the system stretches the keyboard to fill the screen in landscape.
        int px = (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, KEYBOARD_HEIGHT_DP,
                Resources.getSystem().getDisplayMetrics());
        ViewGroup.LayoutParams lp = keyboardView.getLayoutParams();
        if (lp == null) {
            lp = new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, px);
        } else {
            lp.height = px;
        }
        keyboardView.setLayoutParams(lp);
        keyboardView.setMinimumHeight(px);
        wireKeys(keyboardView);
        return keyboardView;
    }

    /** Target keyboard height in dp. */
    private static final int KEYBOARD_HEIGHT_DP = 240;

    /**
     * In landscape Android defaults to fullscreen-extract IME mode, which
     * floats a full-screen text editor above the host app and stretches the
     * keyboard to fill the rest. We don't want that -- the keyboard should
     * sit at its declared height and leave the host app visible.
     */
    @Override
    public boolean onEvaluateFullscreenMode() {
        return false;
    }

    @Override
    public void onStartInput(EditorInfo info, boolean restarting) {
        super.onStartInput(info, restarting);
        // Belt + braces: tell the framework not to extract for landscape.
        if (info != null) {
            info.imeOptions |= EditorInfo.IME_FLAG_NO_EXTRACT_UI
                            |  EditorInfo.IME_FLAG_NO_FULLSCREEN;
        }
    }

    private void wireKeys(View root) {
        if (root instanceof ViewGroup) {
            ViewGroup vg = (ViewGroup) root;
            for (int i = 0; i < vg.getChildCount(); i++) wireKeys(vg.getChildAt(i));
        }
        if (root instanceof Button) {
            Button b = (Button) root;
            Object tag = b.getTag();
            if (tag instanceof String) {
                b.setOnClickListener(v -> handleKey((String) tag));
            }
        }
    }

    private void handleKey(String tag) {
        InputConnection ic = getCurrentInputConnection();
        if (ic == null) return;

        switch (tag) {
            case "BKSP":  sendKey(KeyEvent.KEYCODE_DEL); return;
            case "ENTER": sendKey(KeyEvent.KEYCODE_ENTER); return;
            case "TAB":   sendKey(KeyEvent.KEYCODE_TAB); return;
            case "ESC":   sendKey(KeyEvent.KEYCODE_ESCAPE); return;
            case "SPACE": ic.commitText(" ", 1); return;
            case "LEFT":  sendKey(KeyEvent.KEYCODE_DPAD_LEFT); return;
            case "RIGHT": sendKey(KeyEvent.KEYCODE_DPAD_RIGHT); return;
            case "UP":    sendKey(KeyEvent.KEYCODE_DPAD_UP); return;
            case "DOWN":  sendKey(KeyEvent.KEYCODE_DPAD_DOWN); return;
            case "SHIFT": shifted = !shifted; updateLabels(); return;
            case "CTRL":  ctrl = !ctrl; return;
            case "ALT":   alt = !alt; return;
            default:
                String text = tag;
                if (shifted) {
                    text = shiftMap(text);
                    shifted = false;
                    updateLabels();
                }
                if (ctrl || alt) {
                    int kc = keyCodeFor(text);
                    if (kc != 0) {
                        sendKeyWithMods(kc);
                        ctrl = alt = false;
                        return;
                    }
                }
                ic.commitText(text, 1);
        }
    }

    private void sendKey(int keycode) {
        InputConnection ic = getCurrentInputConnection();
        if (ic == null) return;
        ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN, keycode));
        ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP, keycode));
    }

    private void sendKeyWithMods(int kc) {
        InputConnection ic = getCurrentInputConnection();
        if (ic == null) return;
        int meta = 0;
        if (ctrl) meta |= KeyEvent.META_CTRL_ON | KeyEvent.META_CTRL_LEFT_ON;
        if (alt)  meta |= KeyEvent.META_ALT_ON  | KeyEvent.META_ALT_LEFT_ON;
        long now = System.currentTimeMillis();
        ic.sendKeyEvent(new KeyEvent(now, now, KeyEvent.ACTION_DOWN, kc, 0, meta));
        ic.sendKeyEvent(new KeyEvent(now, now, KeyEvent.ACTION_UP,   kc, 0, meta));
    }

    private int keyCodeFor(String text) {
        if (text.length() != 1) return 0;
        char c = text.charAt(0);
        if (c >= 'a' && c <= 'z') return KeyEvent.KEYCODE_A + (c - 'a');
        if (c >= 'A' && c <= 'Z') return KeyEvent.KEYCODE_A + (c - 'A');
        if (c >= '0' && c <= '9') return KeyEvent.KEYCODE_0 + (c - '0');
        return 0;
    }

    private String shiftMap(String s) {
        if (s.length() != 1) return s.toUpperCase();
        char c = s.charAt(0);
        if (c >= 'a' && c <= 'z') return String.valueOf((char)(c - 32));
        switch (c) {
            case '1': return "!";  case '2': return "@";  case '3': return "#";
            case '4': return "$";  case '5': return "%";  case '6': return "^";
            case '7': return "&";  case '8': return "*";  case '9': return "(";
            case '0': return ")";  case '-': return "_";  case '=': return "+";
            case '[': return "{";  case ']': return "}";  case ';': return ":";
            case '\'': return "\"";
            case ',': return "<";  case '.': return ">";  case '/': return "?";
            case '`': return "~";  case '\\': return "|";
        }
        return s;
    }

    private void updateLabels() {
        if (keyboardView != null) updateLabelsRec(keyboardView);
    }

    private void updateLabelsRec(View v) {
        if (v instanceof ViewGroup) {
            ViewGroup vg = (ViewGroup) v;
            for (int i = 0; i < vg.getChildCount(); i++) updateLabelsRec(vg.getChildAt(i));
        }
        if (v instanceof Button) {
            Button b = (Button) v;
            Object tag = b.getTag();
            if (!(tag instanceof String)) return;
            String t = (String) tag;
            if (t.length() == 1 && Character.isLetter(t.charAt(0))) {
                b.setText(shifted ? t.toUpperCase() : t.toLowerCase());
            }
        }
    }
}
