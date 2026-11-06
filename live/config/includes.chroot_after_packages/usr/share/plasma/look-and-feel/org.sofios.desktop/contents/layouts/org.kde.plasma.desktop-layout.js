// Barra SofiOS: pannello fluttuante in basso al centro, come nell'anteprima
desktopsArray().forEach(function (d) {
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/SofiOS");
});
var panel = new Panel();
panel.location = "bottom";
panel.height = 56;
panel.floating = true;
panel.lengthMode = "fit";
panel.alignment = "center";
panel.hiding = "none";
var menu = panel.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "sofios-logo");
var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
  "applications:firefox-esr.desktop",
  "applications:org.kde.dolphin.desktop",
  "applications:libreoffice-writer.desktop",
  "applications:org.kde.discover.desktop",
  "applications:systemsettings.desktop"
]);
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
panel.addWidget("org.kde.plasma.showdesktop");
