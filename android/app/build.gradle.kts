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
    // Chiave di PROVA, uguale a ogni costruzione, così gli aggiornamenti si installano uno sopra l'altro.
    // Non è la chiave per il Play Store: quella sarà separata e non entrerà mai nel repository.
    signingConfigs {
        getByName("debug") {
            storeFile = file("prova.keystore")
            storePassword = "sofios-prova"
            keyAlias = "prova"
            keyPassword = "sofios-prova"
        }
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
