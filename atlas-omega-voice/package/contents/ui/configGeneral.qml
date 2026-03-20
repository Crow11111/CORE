import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.20 as Kirigami
import org.kde.plasma.jarvis 1.0

Item {
    id: configRootItem
    width: parent ? parent.width : 0
    height: parent ? parent.height : 0

    ScrollView {
        id: configRoot
        anchors.fill: parent
        contentWidth: availableWidth

    ColumnLayout {
        id: configPage
        width: configRoot.availableWidth
        spacing: 0

        // ════════════════════════════════════════
        // DOWNLOAD PROGRESS — always visible at top when downloading
        // ════════════════════════════════════════
        Kirigami.InlineMessage {
            id: downloadBanner
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.smallSpacing
            visible: JarvisBackend.downloading
            type: Kirigami.MessageType.Information
            text: JarvisBackend.downloadStatus

            actions: [
                Kirigami.Action {
                    icon.name: "dialog-cancel"
                    text: i18n("Abbrechen")
                    onTriggered: JarvisBackend.cancelDownload()
                }
            ]
        }

        ProgressBar {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.smallSpacing
            Layout.rightMargin: Kirigami.Units.smallSpacing
            visible: JarvisBackend.downloading
            from: 0; to: 1.0
            value: JarvisBackend.downloadProgress
        }

        // ════════════════════════════════════════
        // LLM SERVER
        // ════════════════════════════════════════
        Kirigami.FormLayout {
            Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("LLM-Server-Verbindung")
            }

            RowLayout {
                Kirigami.FormData.label: i18n("Server URL:")
                spacing: Kirigami.Units.smallSpacing
                TextField {
                    id: serverUrlField
                    text: JarvisBackend.llmServerUrl
                    placeholderText: "http://127.0.0.1:8000"
                    Layout.fillWidth: true
                    onAccepted: JarvisBackend.setLlmServerUrl(text)
                }
                Button {
                    text: i18n("Übernehmen")
                    icon.name: "dialog-ok-apply"
                    onClicked: JarvisBackend.setLlmServerUrl(serverUrlField.text)
                }
            }

            RowLayout {
                Kirigami.FormData.label: i18n("Status:")
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Icon {
                    source: JarvisBackend.connected ? "network-connect" : "network-disconnect"
                    implicitWidth: Kirigami.Units.iconSizes.small
                    implicitHeight: Kirigami.Units.iconSizes.small
                }
                Label {
                    text: JarvisBackend.connected ? i18n("Verbunden") : i18n("Getrennt")
                    color: JarvisBackend.connected ? Kirigami.Theme.positiveTextColor : Kirigami.Theme.negativeTextColor
                    font.bold: true
                }
            }

            Label {
                Kirigami.FormData.label: i18n("Aktives Modell:")
                text: JarvisBackend.currentModelName || i18n("Keins gewählt")
                font.bold: true
            }
        }

        // ════════════════════════════════════════
        // LLM MODELS
        // ════════════════════════════════════════
        Kirigami.FormLayout {
            Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("LLM-Modelle (OMEGA / Router)")
            }

            Label {
                text: i18n("Wähle den Kanal für das CORE-Backend (z. B. core-local-min, core-api-max).")
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                color: Kirigami.Theme.disabledTextColor
                font.pointSize: Kirigami.Theme.smallFont.pointSize
            }
        }

        Repeater {
            model: JarvisBackend.availableLlmModels
            delegate: Kirigami.AbstractCard {
                Layout.fillWidth: true
                Layout.leftMargin: Kirigami.Units.smallSpacing
                Layout.rightMargin: Kirigami.Units.smallSpacing
                contentItem: RowLayout {
                    spacing: Kirigami.Units.largeSpacing
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            spacing: Kirigami.Units.smallSpacing
                            Label {
                                text: modelData.name
                                font.bold: true
                            }
                            Label {
                                text: modelData.size
                                color: Kirigami.Theme.disabledTextColor
                                font.pointSize: Kirigami.Theme.smallFont.pointSize
                            }
                            Kirigami.Icon {
                                visible: modelData.active
                                source: "emblem-default"
                                implicitWidth: Kirigami.Units.iconSizes.small
                                implicitHeight: Kirigami.Units.iconSizes.small
                            }
                        }
                        Label {
                            text: modelData.desc
                            color: Kirigami.Theme.disabledTextColor
                            font.pointSize: Kirigami.Theme.smallFont.pointSize
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                        }
                    }
                    Button {
                        text: modelData.active ? i18n("Aktiv") : (modelData.downloaded ? i18n("Aktivieren") : i18n("Herunterladen"))
                        icon.name: modelData.active ? "checkmark" : (modelData.downloaded ? "media-playback-start" : "download")
                        enabled: !modelData.active && !JarvisBackend.downloading
                        highlighted: modelData.active
                        onClicked: {
                            if (modelData.downloaded) JarvisBackend.setActiveLlmModel(modelData.id)
                            else JarvisBackend.downloadLlmModel(modelData.id)
                        }
                    }
                }
            }
        }

        Button {
            text: i18n("Weitere Modelle (falls aktiv)")
            icon.name: "list-add"
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.topMargin: Kirigami.Units.smallSpacing
            onClicked: JarvisBackend.fetchMoreModels()
        }

        // ════════════════════════════════════════
        // TTS VOICES
        // ════════════════════════════════════════
        Kirigami.FormLayout {
            Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("TTS-Stimmen (Piper / lokal)")
            }

            Label {
                text: i18n("Stimme für lokale Sprachausgabe. Bei OMEGA-TTS über das Backend oft Kore/Gemini — Piper bleibt Fallback.")
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                color: Kirigami.Theme.disabledTextColor
                font.pointSize: Kirigami.Theme.smallFont.pointSize
            }

            Label {
                Kirigami.FormData.label: i18n("Aktive Stimme:")
                text: JarvisBackend.currentVoiceName || i18n("Keine")
                font.bold: true
            }
        }

        Repeater {
            model: JarvisBackend.availableTtsVoices
            delegate: Kirigami.AbstractCard {
                Layout.fillWidth: true
                Layout.leftMargin: Kirigami.Units.smallSpacing
                Layout.rightMargin: Kirigami.Units.smallSpacing
                contentItem: RowLayout {
                    spacing: Kirigami.Units.largeSpacing
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            spacing: Kirigami.Units.smallSpacing
                            Label {
                                text: modelData.name
                                font.bold: true
                            }
                            Label {
                                text: modelData.lang
                                color: Kirigami.Theme.disabledTextColor
                                font.pointSize: Kirigami.Theme.smallFont.pointSize
                            }
                            Kirigami.Icon {
                                visible: modelData.active
                                source: "emblem-default"
                                implicitWidth: Kirigami.Units.iconSizes.small
                                implicitHeight: Kirigami.Units.iconSizes.small
                            }
                        }
                        Label {
                            text: modelData.desc
                            color: Kirigami.Theme.disabledTextColor
                            font.pointSize: Kirigami.Theme.smallFont.pointSize
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                        }
                    }
                    Button {
                        visible: modelData.downloaded
                        text: i18n("Abspielen")
                        icon.name: "media-playback-start"
                        flat: true
                        ToolTip.text: i18n("Stimme anhören")
                        ToolTip.visible: hovered
                        onClicked: JarvisBackend.testVoice(modelData.id)
                    }
                    Button {
                        text: modelData.active ? i18n("Aktiv") : (modelData.downloaded ? i18n("Aktivieren") : i18n("Herunterladen"))
                        icon.name: modelData.active ? "checkmark" : (modelData.downloaded ? "media-playback-start" : "download")
                        enabled: !modelData.active && !JarvisBackend.downloading
                        highlighted: modelData.active
                        onClicked: {
                            if (modelData.downloaded) JarvisBackend.setActiveTtsVoice(modelData.id)
                            else JarvisBackend.downloadTtsVoice(modelData.id)
                        }
                    }
                }
            }
        }

        Button {
            text: i18n("Weitere Stimmen laden")
            icon.name: "list-add"
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.topMargin: Kirigami.Units.smallSpacing
            onClicked: JarvisBackend.fetchMoreVoices()
        }

        // ════════════════════════════════════════
        // VOICE SYNTHESIS SETTINGS
        // ════════════════════════════════════════
        Kirigami.FormLayout {
            Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("Sprachsynthese")
            }

            Slider {
                id: rateSlider
                Kirigami.FormData.label: i18n("Sprechtempo: %1", value.toFixed(2))
                from: -1.0; to: 1.0; stepSize: 0.05
                value: 0.05
                onMoved: JarvisBackend.setTtsRate(value)
            }

            Slider {
                id: pitchSlider
                Kirigami.FormData.label: i18n("Tonhöhe: %1", value.toFixed(2))
                from: -1.0; to: 1.0; stepSize: 0.05
                value: -0.1
                onMoved: JarvisBackend.setTtsPitch(value)
            }

            Slider {
                id: volumeSlider
                Kirigami.FormData.label: i18n("Lautstärke: %1 %", (value * 100).toFixed(0))
                from: 0.0; to: 1.0; stepSize: 0.05
                value: 0.85
                onMoved: JarvisBackend.setTtsVolume(value)
            }

            Button {
                text: i18n("Aktuelle Stimme testen")
                icon.name: "media-playback-start"
                onClicked: JarvisBackend.testVoice(JarvisBackend.currentVoiceName)
            }
        }

        // ════════════════════════════════════════
        // WAKE WORD & AUDIO
        // ════════════════════════════════════════
        Kirigami.FormLayout {
            Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("Wake-Word & Audio")
            }

            CheckBox {
                Kirigami.FormData.label: i18n("Wake-Word automatisch starten:")
                checked: JarvisBackend.autoStartWakeWord
                onToggled: JarvisBackend.setAutoStartWakeWord(checked)
            }

            Label {
                text: i18n("Sage „Atlas“ oder „Jarvis“, um Sprachbefehle ohne Klick zu starten.")
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                color: Kirigami.Theme.disabledTextColor
                font.pointSize: Kirigami.Theme.smallFont.pointSize
            }

            Slider {
                id: voiceCmdSlider
                Kirigami.FormData.label: i18n("Max. Länge Sprachbefehl: %1 Sekunden", value.toFixed(0))
                from: 3; to: 30; stepSize: 1
                value: JarvisBackend.voiceCmdMaxSeconds
                onMoved: JarvisBackend.setVoiceCmdMaxSeconds(value)
            }
        }

        // ════════════════════════════════════════
        // CHAT SETTINGS
        // ════════════════════════════════════════
        Kirigami.FormLayout {
            Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("Chat-Einstellungen")
            }

            Slider {
                id: historySlider
                Kirigami.FormData.label: i18n("Gedächtnis: %1 Nachrichtenpaare", value.toFixed(0))
                from: 5; to: 100; stepSize: 5
                value: JarvisBackend.maxHistoryPairs
                onMoved: JarvisBackend.setMaxHistoryPairs(value)
            }

            Label {
                text: i18n("Mehr Paare = mehr Kontext, aber langsamer und mehr RAM.")
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                color: Kirigami.Theme.disabledTextColor
                font.pointSize: Kirigami.Theme.smallFont.pointSize
            }
        }

        // ════════════════════════════════════════
        // PERSONALITY
        // ════════════════════════════════════════
        Kirigami.FormLayout {
            Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("Persönlichkeit (Systemprompt)")
            }

            Label {
                text: i18n("Leer lassen = deutscher ATLAS-Standardprompt (OMEGA). Sonst eigenen Systemtext setzen.")
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                color: Kirigami.Theme.disabledTextColor
                font.pointSize: Kirigami.Theme.smallFont.pointSize
            }

            TextArea {
                id: personalityField
                Kirigami.FormData.label: i18n("System-Prompt:")
                text: JarvisBackend.personalityPrompt
                placeholderText: i18n("Standard: ATLAS / OMEGA (deutsch) …")
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                wrapMode: TextEdit.Wrap
            }

            Button {
                text: i18n("Speichern")
                icon.name: "document-save"
                onClicked: JarvisBackend.setPersonalityPrompt(personalityField.text)
            }
        }

        // Bottom spacer
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }
    }
}
