import QtQuick 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import QtQuick.Controls 2.15
import org.kde.plasma.jarvis 1.0

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    // OMEGA Color Palette
    readonly property color corePrimary:   "#D22B2B"
    readonly property color bgDark:        "#0D0D0D"
    readonly property color borderDim:     "#2A1010"
    readonly property color orangeAccent:  "#f0a030"
    readonly property string monoFont:     "monospace"

    preferredRepresentation: compactRepresentation
    fullRepresentation: compactRep // Same for desktop pinning
    compactRepresentation: compactRep

    Component {
        id: compactRep
        Item {
            width: 120; height: 40
            RowLayout {
                anchors.fill: parent; spacing: 4

                // LIVE (Zap)
                Rectangle {
                    Layout.fillWidth: true; Layout.fillHeight: true; radius: 4
                    color: zapArea.containsMouse ? Qt.rgba(0.82, 0.17, 0.17, 0.15) : bgDark
                    border.color: borderDim; border.width: 1
                    Text { anchors.centerIn: parent; text: "⚡"; color: orangeAccent; font.pixelSize: 14 }
                    MouseArea {
                        id: zapArea; anchors.fill: parent; hoverEnabled: true
                        onClicked: { JarvisBackend.executeRunCommand("python3 /OMEGA_CORE/src/scripts/core_dictate_clipboard.py live"); }
                    }
                }

                // DEEP (Brain)
                Rectangle {
                    Layout.fillWidth: true; Layout.fillHeight: true; radius: 4
                    color: brainArea.containsMouse ? Qt.rgba(0.82, 0.17, 0.17, 0.15) : bgDark
                    border.color: borderDim; border.width: 1
                    Text { anchors.centerIn: parent; text: "🧠"; color: corePrimary; font.pixelSize: 14 }
                    MouseArea {
                        id: brainArea; anchors.fill: parent; hoverEnabled: true
                        onClicked: { JarvisBackend.executeRunCommand("python3 /OMEGA_CORE/src/scripts/core_dictate_clipboard.py deep"); }
                    }
                }

                // MIC
                Rectangle {
                    Layout.fillWidth: true; Layout.fillHeight: true; radius: 4
                    color: micArea.containsMouse ? Qt.rgba(0.82, 0.17, 0.17, 0.2) : bgDark
                    border.color: corePrimary; border.width: 1
                    Text { anchors.centerIn: parent; text: "🎤"; color: corePrimary; font.pixelSize: 14 }
                    MouseArea {
                        id: micArea; anchors.fill: parent; hoverEnabled: true
                        onClicked: { JarvisBackend.executeRunCommand("python3 /OMEGA_CORE/src/scripts/core_dictate_clipboard.py deep"); }
                    }
                }
            }
        }
    }
}
