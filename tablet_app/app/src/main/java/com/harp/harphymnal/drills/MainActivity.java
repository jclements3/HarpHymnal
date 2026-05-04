package com.harp.harphymnal.drills;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebSettings;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.PermissionRequest;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final String TREFOIL_PACKAGE = "com.harp.trefoil";
    private static final int FILE_CHOOSER_RC = 1001;

    private ValueCallback<Uri[]> pendingFileChooser = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Keep the screen on during practice — tablet sits on the music stand.
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

            // <input type="file"> in the WebView (the composer's Open button)
            // is silently ignored unless we override this. Launch the system
            // document picker and feed the resulting URI back to the WebView.
            @Override
            public boolean onShowFileChooser(WebView view,
                                             ValueCallback<Uri[]> filePathCallback,
                                             FileChooserParams fileChooserParams) {
                if (pendingFileChooser != null) {
                    pendingFileChooser.onReceiveValue(null);
                }
                pendingFileChooser = filePathCallback;

                Intent picker;
                try {
                    picker = fileChooserParams.createIntent();
                } catch (Exception e) {
                    picker = new Intent(Intent.ACTION_GET_CONTENT);
                    picker.addCategory(Intent.CATEGORY_OPENABLE);
                    picker.setType("*/*");
                }
                try {
                    startActivityForResult(
                        Intent.createChooser(picker, "Open ABC file"),
                        FILE_CHOOSER_RC);
                    return true;
                } catch (Exception e) {
                    pendingFileChooser = null;
                    Toast.makeText(MainActivity.this,
                        "No file picker available",
                        Toast.LENGTH_SHORT).show();
                    return false;
                }
            }
        });

        // JS-side bridge so the Hymns tile can launch the sibling Trefoil app.
        webView.addJavascriptInterface(new Bridge(), "Bridge");

        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_RC) {
            if (pendingFileChooser != null) {
                Uri[] result = null;
                if (resultCode == RESULT_OK && data != null) {
                    Uri uri = data.getData();
                    if (uri != null) result = new Uri[] { uri };
                }
                pendingFileChooser.onReceiveValue(result);
                pendingFileChooser = null;
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    private class Bridge {
        @JavascriptInterface
        public void launchHymns() {
            Intent launch = getPackageManager().getLaunchIntentForPackage(TREFOIL_PACKAGE);
            if (launch != null) {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(launch);
            } else {
                // Trefoil not installed — notify the user on the UI thread.
                runOnUiThread(() -> Toast.makeText(
                    MainActivity.this,
                    "Trefoil Hymnal app not installed",
                    Toast.LENGTH_SHORT).show());
            }
        }
    }
}
