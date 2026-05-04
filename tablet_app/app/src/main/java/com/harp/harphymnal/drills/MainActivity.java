package com.harp.harphymnal.drills;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentUris;
import android.content.ContentValues;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebSettings;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.PermissionRequest;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Rect;
import android.graphics.pdf.PdfDocument;
import android.util.Base64;

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

        // ─────────────────────────────────────────────────────────────────
        // Documents/HarpHymnal/ shared folder. The composer Save/Open path
        // talks to the public Documents tree via MediaStore (API 29+) so
        // files land somewhere the user can browse with any file manager.
        // Pre-API 29 falls back to direct File I/O.
        // ─────────────────────────────────────────────────────────────────

        private static final String REL_DIR = "Documents/HarpHymnal/";

        /** Save (or overwrite) a UTF-8 text file under Documents/HarpHymnal/.
         *  Returns "OK" on success, "ERR: <reason>" on failure. */
        @JavascriptInterface
        public String saveAbc(String filename, String content) {
            if (filename == null || filename.isEmpty()) return "ERR: empty filename";
            if (content == null) content = "";
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    return saveViaMediaStore(filename, content);
                } else {
                    return saveViaFile(filename, content);
                }
            } catch (Exception e) {
                return "ERR: " + e.getClass().getSimpleName() + ": " + e.getMessage();
            }
        }

        private String saveViaMediaStore(String filename, String content) throws Exception {
            ContentResolver resolver = getContentResolver();
            Uri collection = MediaStore.Files.getContentUri("external");

            // If a file with the same display_name already exists in our
            // RELATIVE_PATH, overwrite it; otherwise insert a new row.
            Uri existing = findExisting(resolver, filename);
            Uri target;
            if (existing != null) {
                target = existing;
            } else {
                ContentValues values = new ContentValues();
                values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename);
                // Use a non-text MIME so MediaStore doesn't auto-append ".txt"
                // when the display_name's extension (.abc) isn't a known
                // text-family suffix on Android.
                values.put(MediaStore.MediaColumns.MIME_TYPE, "application/octet-stream");
                values.put(MediaStore.MediaColumns.RELATIVE_PATH, REL_DIR);
                target = resolver.insert(collection, values);
            }
            if (target == null) return "ERR: insert returned null";

            try (OutputStream os = resolver.openOutputStream(target, "wt")) {
                if (os == null) return "ERR: openOutputStream null";
                os.write(content.getBytes(StandardCharsets.UTF_8));
            }
            return "OK";
        }

        private Uri findExisting(ContentResolver resolver, String filename) {
            try {
                Uri queryUri = MediaStore.Files.getContentUri("external");
                String[] proj = { MediaStore.MediaColumns._ID };
                String sel = MediaStore.MediaColumns.RELATIVE_PATH + " LIKE ? AND "
                          + MediaStore.MediaColumns.DISPLAY_NAME + "=?";
                String[] args = { REL_DIR + "%", filename };
                try (Cursor c = resolver.query(queryUri, proj, sel, args, null)) {
                    if (c != null && c.moveToFirst()) {
                        long id = c.getLong(0);
                        return ContentUris.withAppendedId(queryUri, id);
                    }
                }
            } catch (Exception e) {
                // fall through to insert path
            }
            return null;
        }

        private String saveViaFile(String filename, String content) throws Exception {
            File dir = new File(Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOCUMENTS), "HarpHymnal");
            if (!dir.exists()) dir.mkdirs();
            File f = new File(dir, filename);
            try (FileOutputStream fos = new FileOutputStream(f)) {
                fos.write(content.getBytes(StandardCharsets.UTF_8));
            }
            return "OK";
        }

        /** Save a binary blob (MIDI, PDF, etc.) under Documents/HarpHymnal/.
         *  `b64` is base64-encoded raw bytes (no data: URI prefix).
         *  Returns "OK" or "ERR: ...". */
        @JavascriptInterface
        public String saveAbcBase64(String filename, String b64) {
            if (filename == null || filename.isEmpty()) return "ERR: empty filename";
            if (b64 == null) b64 = "";
            try {
                byte[] bytes = Base64.decode(b64, Base64.DEFAULT);
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    return saveBytesViaMediaStore(filename, bytes);
                } else {
                    return saveBytesViaFile(filename, bytes);
                }
            } catch (Exception e) {
                return "ERR: " + e.getClass().getSimpleName() + ": " + e.getMessage();
            }
        }

        /** Wrap a base64-PNG in a single-page US-Letter PDF and save under
         *  Documents/HarpHymnal/. Used by the composer's Save All button to
         *  emit a `.pdf` snapshot of the active render view (score or
         *  stripchart). Returns "OK" or "ERR: ...". */
        @JavascriptInterface
        public String saveAbcPdfFromPng(String filename, String pngB64) {
            if (filename == null || filename.isEmpty()) return "ERR: empty filename";
            if (pngB64 == null || pngB64.isEmpty()) return "ERR: empty png";
            try {
                byte[] pngBytes = Base64.decode(pngB64, Base64.DEFAULT);
                Bitmap bmp = BitmapFactory.decodeByteArray(pngBytes, 0, pngBytes.length);
                if (bmp == null) return "ERR: bitmap decode null";
                // US Letter @ 72dpi = 612 x 792 points. 36-pt margins.
                final int pageW = 612, pageH = 792, margin = 36;
                final int boxW = pageW - margin * 2;
                final int boxH = pageH - margin * 2;
                float scale = Math.min(
                    (float) boxW / bmp.getWidth(),
                    (float) boxH / bmp.getHeight());
                int drawW = Math.max(1, (int) (bmp.getWidth() * scale));
                int drawH = Math.max(1, (int) (bmp.getHeight() * scale));
                int drawX = margin + (boxW - drawW) / 2;
                int drawY = margin;
                PdfDocument pdf = new PdfDocument();
                PdfDocument.PageInfo info =
                    new PdfDocument.PageInfo.Builder(pageW, pageH, 1).create();
                PdfDocument.Page page = pdf.startPage(info);
                Canvas c = page.getCanvas();
                c.drawColor(Color.WHITE);
                c.drawBitmap(bmp, null,
                    new Rect(drawX, drawY, drawX + drawW, drawY + drawH), null);
                pdf.finishPage(page);
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                pdf.writeTo(baos);
                pdf.close();
                bmp.recycle();
                byte[] pdfBytes = baos.toByteArray();
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    return saveBytesViaMediaStore(filename, pdfBytes);
                } else {
                    return saveBytesViaFile(filename, pdfBytes);
                }
            } catch (Exception e) {
                return "ERR: " + e.getClass().getSimpleName() + ": " + e.getMessage();
            }
        }

        private String saveBytesViaMediaStore(String filename, byte[] bytes) throws Exception {
            ContentResolver resolver = getContentResolver();
            Uri collection = MediaStore.Files.getContentUri("external");
            Uri existing = findExisting(resolver, filename);
            Uri target;
            if (existing != null) {
                target = existing;
            } else {
                ContentValues values = new ContentValues();
                values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename);
                values.put(MediaStore.MediaColumns.MIME_TYPE, "application/octet-stream");
                values.put(MediaStore.MediaColumns.RELATIVE_PATH, REL_DIR);
                target = resolver.insert(collection, values);
            }
            if (target == null) return "ERR: insert returned null";
            try (OutputStream os = resolver.openOutputStream(target, "wt")) {
                if (os == null) return "ERR: openOutputStream null";
                os.write(bytes);
            }
            return "OK";
        }

        private String saveBytesViaFile(String filename, byte[] bytes) throws Exception {
            File dir = new File(Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOCUMENTS), "HarpHymnal");
            if (!dir.exists()) dir.mkdirs();
            File f = new File(dir, filename);
            try (FileOutputStream fos = new FileOutputStream(f)) {
                fos.write(bytes);
            }
            return "OK";
        }

        /** Returns a JSON array of {"name": "...", "id": <long>} for every
         *  file under Documents/HarpHymnal/ that this app can see. Files
         *  written by saveAbc above are app-owned and always visible; files
         *  put there by other apps may not appear. */
        @JavascriptInterface
        public String listAbc() {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    return listViaMediaStore();
                } else {
                    return listViaFile();
                }
            } catch (Exception e) {
                return "[]";
            }
        }

        private String listViaMediaStore() {
            ContentResolver resolver = getContentResolver();
            Uri queryUri = MediaStore.Files.getContentUri("external");
            String[] proj = {
                MediaStore.MediaColumns._ID,
                MediaStore.MediaColumns.DISPLAY_NAME,
            };
            String sel = MediaStore.MediaColumns.RELATIVE_PATH + " LIKE ?";
            String[] args = { REL_DIR + "%" };
            String order = MediaStore.MediaColumns.DISPLAY_NAME + " ASC";

            StringBuilder sb = new StringBuilder("[");
            boolean first = true;
            try (Cursor c = resolver.query(queryUri, proj, sel, args, order)) {
                while (c != null && c.moveToNext()) {
                    long id = c.getLong(0);
                    String name = c.getString(1);
                    if (!first) sb.append(",");
                    first = false;
                    sb.append("{\"name\":\"").append(jsonEsc(name))
                      .append("\",\"id\":").append(id).append("}");
                }
            }
            sb.append("]");
            return sb.toString();
        }

        private String listViaFile() {
            File dir = new File(Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOCUMENTS), "HarpHymnal");
            StringBuilder sb = new StringBuilder("[");
            if (dir.isDirectory()) {
                File[] files = dir.listFiles();
                if (files != null) {
                    boolean first = true;
                    for (File f : files) {
                        if (!f.isFile()) continue;
                        if (!first) sb.append(",");
                        first = false;
                        sb.append("{\"name\":\"").append(jsonEsc(f.getName()))
                          .append("\",\"id\":-1}");
                    }
                }
            }
            sb.append("]");
            return sb.toString();
        }

        /** Read the UTF-8 contents of a file by its MediaStore row id (or
         *  by name when running on pre-API-29). Returns "" on failure. */
        @JavascriptInterface
        public String readAbcById(long id) {
            try {
                Uri uri = ContentUris.withAppendedId(
                    MediaStore.Files.getContentUri("external"), id);
                try (InputStream is = getContentResolver().openInputStream(uri)) {
                    if (is == null) return "";
                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    byte[] buf = new byte[4096];
                    int n;
                    while ((n = is.read(buf)) > 0) baos.write(buf, 0, n);
                    return baos.toString("UTF-8");
                }
            } catch (Exception e) {
                return "";
            }
        }

        @JavascriptInterface
        public String readAbcByName(String filename) {
            try {
                File f = new File(Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOCUMENTS), "HarpHymnal/" + filename);
                if (!f.isFile()) return "";
                try (InputStream is = new java.io.FileInputStream(f)) {
                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    byte[] buf = new byte[4096];
                    int n;
                    while ((n = is.read(buf)) > 0) baos.write(buf, 0, n);
                    return baos.toString("UTF-8");
                }
            } catch (Exception e) {
                return "";
            }
        }

        private String jsonEsc(String s) {
            if (s == null) return "";
            StringBuilder out = new StringBuilder();
            for (int i = 0; i < s.length(); i++) {
                char c = s.charAt(i);
                switch (c) {
                    case '\\': out.append("\\\\"); break;
                    case '"':  out.append("\\\""); break;
                    case '\n': out.append("\\n"); break;
                    case '\r': out.append("\\r"); break;
                    case '\t': out.append("\\t"); break;
                    default:
                        if (c < 0x20) out.append(String.format("\\u%04x", (int) c));
                        else out.append(c);
                }
            }
            return out.toString();
        }
    }
}
