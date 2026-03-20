import QtQuick 2.15
import org.kde.plasma.configuration 2.0

ConfigModel {
    ConfigCategory {
        name: i18n("Allgemein")
        icon: "configure"
        source: "configGeneral.qml"
    }
    ConfigCategory {
        name: i18n("Sprachbefehle")
        icon: "dialog-scripts"
        source: "configCommands.qml"
    }
    ConfigCategory {
        name: i18n("ATLAS")
        icon: "preferences-desktop-text-to-speech"
        source: "configAbout.qml"
    }
}
