// SOLO PER LA PROVA nel tablet simulato: un finto Fully, per vedere che SofiOS lo apre.
// Non fa parte dell'app SofiOS e non va mai pubblicato.
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "de.ozerov.fully"
    compileSdk = 34
    defaultConfig {
        applicationId = "de.ozerov.fully"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "finto"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
