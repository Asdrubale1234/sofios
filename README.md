# SofiOS

Sistema operativo di Luca, costruito su una base Debian 13 con ambiente KDE Plasma e grafica SofiOS.

## Come si costruisce la ISO
Dal sito GitHub: **Actions → "Costruisci ISO SofiOS" → Run workflow**.
A fine lavoro la ISO compare in **Releases**, divisa in parti da meno di 2 GB con le istruzioni per riunirle.
Se qualcosa non va, il registro completo è nel ramo `logs`.

## Cartelle
- `.github/workflows/` — l'automazione che costruisce la ISO
- `build/` — script di costruzione
- `live/` — configurazione del sistema (programmi, grafica, installatore)
- `docs/` — anteprima grafica di riferimento
