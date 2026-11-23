package de.ozerov.fully

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.TextView

/** Finto Fully per la prova: schermata verde con una scritta che dice che è finto. */
class FintoFully : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(TextView(this).apply {
            text = "FINTO FULLY (solo per la prova)\nQui ci sarà il pannello Casa"
            textSize = 28f
            gravity = Gravity.CENTER
            setTextColor(Color.WHITE)
            setBackgroundColor(0xFF1B5E20.toInt())
        })
    }
}
