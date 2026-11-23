// SofiOS: Dock fluttuante in basso (solo icone) + barra sottile in alto con menu, rete, volume e orologio
desktops().forEach(function (d) {
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/SofiOSArgento");
    // la mascotte (un widget: ha la sua X per toglierla), in basso a destra sopra il dock
    var gs = {width: 1280, height: 800};
    try { gs = screenGeometry(d.screen); } catch (e) {}
    d.addWidget("org.sofios.mascotte", Math.max(0, gs.width - 180 - 50), Math.max(0, gs.height - 284 - 110), 180, 284);
});

// --- Barra in alto ---
var alto = new Panel();
alto.location = "top";
alto.height = 30;
alto.floating = false;
alto.opacity = "translucent";
alto.hiding = "none";
var menu = alto.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "sofios-logo");
// Preferiti del menu: i programmi di SofiOS (quelli predefiniti di KDE includevano Discover e Kontact)
menu.writeConfig("favorites", ["preferred://browser", "org.kde.dolphin.desktop", "libreoffice-writer.desktop", "sofios-store.desktop", "sofios-note.desktop", "systemsettings.desktop"]);
menu.writeConfig("favoritesPortedToKAstats", false);
alto.addWidget("org.kde.plasma.panelspacer");
alto.addWidget("org.kde.plasma.systemtray");
alto.addWidget("org.kde.plasma.digitalclock");

// --- Dock in basso ---
var dock = new Panel();
dock.location = "bottom";
dock.height = 64;
dock.floating = true;
dock.opacity = "translucent";
dock.lengthMode = "fit";
dock.alignment = "center";
dock.hiding = "none";
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
  "applications:firefox-esr.desktop",
  "applications:org.kde.dolphin.desktop",
  "applications:libreoffice-writer.desktop",
  "applications:sofios-store.desktop",
  "applications:systemsettings.desktop"
]);
