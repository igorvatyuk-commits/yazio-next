package com.yazionext.app

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null

    companion object {
        const val APP_URL = "https://yazio-next.onrender.com/app"
    }

    private val fileChooserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val intent = result.data
            val uris = WebChromeClient.FileChooserParams.parseResult(result.resultCode, intent)
            fileUploadCallback?.onReceiveValue(uris)
        } else {
            fileUploadCallback?.onReceiveValue(null)
        }
        fileUploadCallback = null
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Dark container layout
        val rootLayout = FrameLayout(this).apply {
            setBackgroundColor(0xFF020617.toInt())
        }

        swipeRefresh = SwipeRefreshLayout(this).apply {
            setColorSchemeColors(0xFF10B981.toInt())
            setProgressBackgroundColorSchemeColor(0xFF0F172A.toInt())
        }

        webView = WebView(this).apply {
            setBackgroundColor(0xFF020617.toInt())
            setLayerType(View.LAYER_TYPE_HARDWARE, null)
        }

        configureWebSettings(webView.settings)
        setupWebClients()

        // Expose Native Google Hardware ML Kit Barcode Scanner to web app JavaScript
        webView.addJavascriptInterface(AndroidNativeBridge(), "AndroidBridge")

        swipeRefresh.addView(
            webView,
            FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        )
        rootLayout.addView(
            swipeRefresh,
            FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        )
        setContentView(rootLayout)

        swipeRefresh.setOnRefreshListener {
            webView.reload()
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })

        webView.loadUrl(APP_URL)
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun configureWebSettings(settings: WebSettings) {
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        settings.userAgentString = settings.userAgentString + " YazioNextAndroid/1.0.0"
    }

    private fun setupWebClients() {
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                swipeRefresh.isRefreshing = false
                // Notify the web interface that native Google ML Kit scanner is active!
                webView.evaluateJavascript(
                    "window.__NATIVE_ANDROID_APP__ = true; if (window.onNativeAndroidReady) window.onNativeAndroidReady();",
                    null
                )
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = filePathCallback
                val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    type = "image/*"
                }
                try {
                    fileChooserLauncher.launch(intent)
                } catch (e: Exception) {
                    fileUploadCallback?.onReceiveValue(null)
                    fileUploadCallback = null
                    return false
                }
                return true
            }
        }
    }

    inner class AndroidNativeBridge {

        @JavascriptInterface
        fun isNative(): Boolean = true

        @JavascriptInterface
        fun openNativeScanner() {
            Handler(Looper.getMainLooper()).post {
                launchGoogleHardwareCodeScanner()
            }
        }
    }

    /**
     * Official Google Play Services Hardware Code Scanner (ML Kit).
     * Provides 0.05s detection, optical auto-zoom, continuous autofocus, and flashlight!
     */
    private fun launchGoogleHardwareCodeScanner() {
        val options = GmsBarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                Barcode.FORMAT_EAN_13,
                Barcode.FORMAT_EAN_8,
                Barcode.FORMAT_UPC_A,
                Barcode.FORMAT_UPC_E
            )
            .enableAutoZoom()
            .build()

        val scanner = GmsBarcodeScanning.getClient(this, options)

        scanner.startScan()
            .addOnSuccessListener { barcode ->
                val raw = barcode.rawValue ?: barcode.displayValue ?: ""
                if (raw.isNotEmpty()) {
                    Handler(Looper.getMainLooper()).post {
                        webView.evaluateJavascript("lookupBarcode('$raw', false);", null)
                        Toast.makeText(this, "✅ $raw", Toast.LENGTH_SHORT).show()
                    }
                }
            }
            .addOnCanceledListener {
                // User pressed back or closed scanner
            }
            .addOnFailureListener { e ->
                Toast.makeText(this, "Сканер: ${e.localizedMessage}", Toast.LENGTH_LONG).show()
            }
    }
}
