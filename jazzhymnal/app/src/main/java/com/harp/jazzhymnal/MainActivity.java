package com.harp.jazzhymnal;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Context;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Music stand use: keep the screen on.
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        WebView webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setMediaPlaybackRequiresUserGesture(false);

        WebView.setWebContentsDebuggingEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                request.grant(request.getResources());
            }
        });

        // Survey export: the page calls window.Android.saveScores(...) to persist
        // its scores payload to the public Downloads/ dir on the tablet.
        webView.addJavascriptInterface(new Bridge(this), "Android");

        webView.loadUrl("file:///android_asset/jazz/index.html");
    }

    private static class Bridge {
        private final Context ctx;

        Bridge(Context ctx) { this.ctx = ctx; }

        @JavascriptInterface
        public String saveScores(String filename, String content) {
            if (filename == null || filename.isEmpty()) filename = "scores.json";
            if (content == null) content = "";
            byte[] bytes = content.getBytes(StandardCharsets.UTF_8);
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    return saveViaMediaStore(filename, bytes);
                }
                return saveDirectly(filename, bytes);
            } catch (Exception e) {
                return "Export failed: " + e.getMessage();
            }
        }

        private String saveViaMediaStore(String filename, byte[] bytes) throws Exception {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME, filename);
            values.put(MediaStore.Downloads.MIME_TYPE, "application/json");
            values.put(MediaStore.Downloads.RELATIVE_PATH,
                    Environment.DIRECTORY_DOWNLOADS + "/JazzHymnal");
            Uri uri = ctx.getContentResolver().insert(
                    MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) throw new Exception("MediaStore insert returned null");
            try (OutputStream os = ctx.getContentResolver().openOutputStream(uri)) {
                if (os == null) throw new Exception("openOutputStream returned null");
                os.write(bytes);
            }
            return "Saved to Downloads/JazzHymnal/" + filename;
        }

        private String saveDirectly(String filename, byte[] bytes) throws Exception {
            File dir = new File(
                    Environment.getExternalStoragePublicDirectory(
                            Environment.DIRECTORY_DOWNLOADS),
                    "JazzHymnal");
            if (!dir.exists() && !dir.mkdirs()) {
                throw new Exception("Could not create " + dir.getAbsolutePath());
            }
            File out = new File(dir, filename);
            try (FileOutputStream fos = new FileOutputStream(out)) {
                fos.write(bytes);
            }
            return "Saved to " + out.getAbsolutePath();
        }
    }
}
