import QtQuick 2.15
import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.jarvis 1.0
import QtQuick.Layouts 1.15

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    readonly property color corePrimary: "#D22B2B"
    readonly property color bgDark: "#0D0D0D"

    // Wir tracken den Status lokal für die Animation
    property bool isRecording: false

    compactRepresentation: Item {
        width: 44; height: 44
        Rectangle {
            anchors.fill: parent; radius: 22
            color: isRecording ? Qt.rgba(0.82, 0.17, 0.17, 0.3) : (micArea.containsMouse ? Qt.rgba(0.82, 0.17, 0.17, 0.2) : bgDark)
            border.color: isRecording ? "#FF0000" : corePrimary; border.width: 1

            Text {
                anchors.centerIn: parent; text: isRecording ? "⏹️" : "🎤"
                color: isRecording ? "#FF0000" : corePrimary; font.pixelSize: 18
            }

            // Pulsieren während Aufnahme
            SequentialAnimation on opacity {
                running: isRecording; loops: Animation.Infinite
                NumberAnimation { from: 1; to: 0.4; duration: 800 }
                NumberAnimation { from: 0.4; to: 1; duration: 800 }
            }

            MouseArea {
                id: micArea; anchors.fill: parent; hoverEnabled: true
                onClicked: {
                    const mode = JarvisBackend.dictateModeDeep ? "deep" : "live";
                    JarvisBackend.executeRunCommand("python3 ~/OMEGA_CORE/src/scripts/core_dictate_clipboard.py toggle " + mode);
                    isRecording = !isRecording;
                }
            }
        }
    }
    fullRepresentation: compactRepresentation
}
