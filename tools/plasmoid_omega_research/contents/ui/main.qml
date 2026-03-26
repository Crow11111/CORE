import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.plasmoid

PlasmoidItem {
    id: root

    // UI Configuration
    compactRepresentation: PlasmaComponents.Button {
        icon.name: "system-search"
        onClicked: root.expanded = !root.expanded
    }

    fullRepresentation: Item {
        Layout.minimumWidth: 400
        Layout.minimumHeight: 250

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10

            PlasmaComponents.Label {
                text: "OMEGA Deep Research"
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                TextArea {
                    id: promptField
                    placeholderText: "Gib deinen Recherche-Prompt hier ein..."
                    wrapMode: TextEdit.Wrap
                    selectByMouse: true
                    font.family: "Monospace"
                    background: Rectangle {
                        color: "transparent"
                        border.color: PlasmaCore.Theme.buttonBackgroundColor
                        border.width: 1
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                
                PlasmaComponents.Button {
                    text: "Löschen"
                    icon.name: "edit-clear"
                    onClicked: promptField.text = ""
                }

                Item { Layout.fillWidth: true }

                PlasmaComponents.Button {
                    text: "Recherche starten"
                    icon.name: "system-run"
                    highlighted: true
                    onClicked: {
                        if (promptField.text.trim().length > 0) {
                            runResearch(promptField.text.trim());
                            promptField.text = "";
                            root.expanded = false;
                        }
                    }
                }
            }
        }
    }

    // Backend Execution
    function runResearch(prompt) {
        // Wir nutzen den internen Executable-Mechanismus von KDE
        // Der Pfad ist absolut auf das OMEGA CORE Verzeichnis gemappt.
        const command = "/OMEGA_CORE/DeepResearch \"" + prompt.replace(/"/g, '\\"') + "\"";
        
        // DataSource für Shell-Execution
        executable.exec(command);
    }

    PlasmaCore.DataSource {
        id: executable
        engine: "executable"
        connectedSources: []
        onNewData: (sourceName, data) => {
            console.log("Deep Research Output:", data.stdout);
            disconnectSource(sourceName);
        }
        function exec(cmd) {
            connectSource(cmd);
        }
    }
}
