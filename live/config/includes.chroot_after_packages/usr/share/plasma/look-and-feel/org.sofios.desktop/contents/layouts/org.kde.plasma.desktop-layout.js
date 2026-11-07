// SofiOS: Dock fluttuante in basso (solo icone) + barra sottile in alto con menu, rete, volume e orologio
desktops().forEach(function (d) {
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/SofiOS");
});

// --- Barra in alto ---
var alto = new Panel();
alto.location = "top";
alto.height = 30;
alto.floating = false;
alto.hiding = "none";
var menu = alto.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "sofios-logo");
alto.addWidget("org.kde.plasma.panelspacer");
alto.addWidget("org.kde.plasma.systemtray");
alto.addWidget("org.kde.plasma.digitalclock");

// --- Dock in basso ---
var dock = new Panel();
dock.location = "bottom";
dock.height = 64;
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment = "center";
dock.hiding = "none";
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
  "applications:firefox-esr.desktop",
  "applications:org.kde.dolphin.desktop",
  "applications:libreoffice-writer.desktop",
  "applications:org.kde.discover.desktop",
  "applications:systemsettings.desktop"
]);
