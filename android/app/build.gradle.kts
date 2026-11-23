plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "it.sofilabs.sofios"
    compileSdk = 34

    defaultConfig {
        applicationId = "it.sofilabs.sofios"
        minSdk = 26          // Android 8.0 in su
        targetSdk = 34
        versionCode = 1
        versionName = "0.1"
    }
    buildTypes {
        release { isMinifyEnabled = true }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
// Nessuna libreria esterna: app leggera e veloce.
