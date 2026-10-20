# YAZIO-Next ProGuard Configuration
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keep class com.google.android.gms.vision.** { *; }
-keep class com.google.mlkit.vision.** { *; }
