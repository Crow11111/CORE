import QtQuick 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.jarvis 1.0

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    readonly property color corePrimary: "#D22B2B"
    readonly property color bgDark: "#0D0D0D"
    readonly property color orangeAccent: "#f0a030"
    readonly property color borderDim: "#2A1010"

    compactRepresentation: Item {
        width: 80; height: 36
        RowLayout {
            anchors.fill: parent; spacing: 4

            // LIVE (Zap)
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 4
                color: !JarvisBackend.dictateModeDeep ? Qt.rgba(0.82, 0.17, 0.17, 0.2) : bgDark
                border.color: !JarvisBackend.dictateModeDeep ? orangeAccent : borderDim
                border.width: 1
                Text { anchors.centerIn: parent; text: "⚡"; color: orangeAccent; font.pixelSize: 14 }
                MouseArea {
                    id: liveArea; anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                    onClicked: JarvisBackend.setDictateMode(false)
                }
            }

            // DEEP (Brain)
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 4
                color: JarvisBackend.dictateModeDeep ? Qt.rgba(0.82, 0.17, 0.17, 0.2) : bgDark
                border.color: JarvisBackend.dictateModeDeep ? corePrimary : borderDim
                border.width: 1
                Text { anchors.centerIn: parent; text: "🧠"; color: corePrimary; font.pixelSize: 14 }
                MouseArea {
                    id: deepArea; anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                    onClicked: JarvisBackend.setDictateMode(true)
                }
            }
        }
    }
    fullRepresentation: compactRepresentation
}
