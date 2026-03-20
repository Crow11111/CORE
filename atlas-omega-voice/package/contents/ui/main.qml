import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.jarvis 1.0

PlasmoidItem {
    id: root
    preferredRepresentation: compactRepresentation
    fullRepresentation: fullRep
    compactRepresentation: compactRep

    readonly property color corePrimary:   "#D22B2B"
    readonly property color coreDim:       "#4A0E0E"
    readonly property color coreGlow:      "#FF4444"
    readonly property color bgDark:        "#060606"
    readonly property color bgPanel:       "#0D0D0D"
    readonly property color bgCard:        "#151515"
    readonly property color borderDim:     "#2A1010"
    readonly property color borderMid:     "#4A1515"
    readonly property color textMain:      "#E0E0E0"
    readonly property color textDim:       "#888888"
    readonly property color orangeAccent:  "#f0a030"
    readonly property color redAlert:      "#FF0000"
    readonly property color greenOk:       "#FFFFFF" // Weiß für OK im neuen Schema
    readonly property string monoFont:     "monospace"
    readonly property string uiFont:       "sans-serif"

    property int currentTab: 0 // 0=chat, 1=system, 2=settings

    // ════════════════════════════════════════════
    //  COMPACT REPRESENTATION — Arc Reactor Icon
    // ════════════════════════════════════════════
    Component {
        id: compactRep
        MouseArea {
            onClicked: root.expanded = !root.expanded
            hoverEnabled: true

            Canvas {
                id: reactorIcon
                anchors.centerIn: parent
                width: Math.min(parent.width, parent.height) - 4
                height: width

                property real phase: 0.0
                NumberAnimation on phase {
                    from: 0; to: 2 * Math.PI; duration: 3000
                    loops: Animation.Infinite
                }
                onPhaseChanged: requestPaint()

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();
                    var cx = width / 2, cy = height / 2, r = width / 2 - 1;

                    // Outer rotating ring segments
                    for (var i = 0; i < 4; i++) {
                        var a = phase + i * Math.PI / 2;
                        ctx.beginPath();
                        ctx.arc(cx, cy, r, a, a + 0.9);
                        ctx.strokeStyle = Qt.rgba(0.82, 0.17, 0.17, 0.5 + 0.3 * Math.sin(phase + i));
                        ctx.lineWidth = 1.5;
                        ctx.stroke();
                    }
                    // Inner counter-rotating
                    for (var j = 0; j < 3; j++) {
                        var b = -phase * 1.5 + j * 2 * Math.PI / 3;
                        ctx.beginPath();
                        ctx.arc(cx, cy, r * 0.6, b, b + 0.8);
                        ctx.strokeStyle = Qt.rgba(0.82, 0.17, 0.17, 0.4);
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                    // Core glow
                    var grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 0.35);
                    grd.addColorStop(0, JarvisBackend.connected ?
                        Qt.rgba(0.82, 0.17, 0.17, 0.95) : Qt.rgba(1.0, 0.3, 0.2, 0.9));
                    grd.addColorStop(1, Qt.rgba(0.82, 0.17, 0.17, 0.0));
                    ctx.beginPath();
                    ctx.arc(cx, cy, r * 0.35, 0, 2 * Math.PI);
                    ctx.fillStyle = grd;
                    ctx.fill();
                }
            }
        }
    }

    // ════════════════════════════════════════════
    //  FULL REPRESENTATION — Main HUD
    // ════════════════════════════════════════════
    Component {
        id: fullRep

        Rectangle {
            id: mainContainer
            width: 460
            height: 640
            color: bgPanel
            radius: 10
            clip: true

            // ── Animated grid background ──
            Canvas {
                anchors.fill: parent
                opacity: 0.04
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.strokeStyle = "#4A1515";
                    ctx.lineWidth = 0.5;
                    for (var x = 0; x < width; x += 20) {
                        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
                    }
                    for (var y = 0; y < height; y += 20) {
                        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
                    }
                }
            }

            // ── Scan line ──
            Rectangle {
                width: parent.width; height: 1
                opacity: 0.12
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "transparent" }
                    GradientStop { position: 0.5; color: corePrimary }
                    GradientStop { position: 1.0; color: "transparent" }
                }
                SequentialAnimation on y {
                    loops: Animation.Infinite
                    NumberAnimation { from: 0; to: mainContainer.height; duration: 5000; easing.type: Easing.InOutSine }
                    NumberAnimation { from: mainContainer.height; to: 0; duration: 5000; easing.type: Easing.InOutSine }
                }
            }

            // ── Corner HUD brackets ──
            Repeater {
                model: 4
                Rectangle {
                    property int corner: index
                    width: 20; height: 20; color: "transparent"
                    x: (corner % 2 === 0) ? 4 : mainContainer.width - 24
                    y: (corner < 2) ? 4 : mainContainer.height - 24
                    Rectangle { width: 12; height: 1; color: coreDim; x: (corner % 2 === 0) ? 0 : parent.width - 12; y: (corner < 2) ? 0 : parent.height - 1 }
                    Rectangle { width: 1; height: 12; color: coreDim; x: (corner % 2 === 0) ? 0 : parent.width - 1; y: (corner < 2) ? 0 : parent.height - 12 }
                }
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 6

                // ════ HEADER ════
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    // Arc reactor spinner
                    Canvas {
                        id: headerReactor
                        width: 42; height: 42
                        property real phase: 0
                        NumberAnimation on phase { from: 0; to: 2 * Math.PI; duration: 2500; loops: Animation.Infinite }
                        onPhaseChanged: requestPaint()
                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.reset();
                            var cx = 21, cy = 21;
                            // Outer ring segments
                            for (var i = 0; i < 4; i++) {
                                var a = phase + i * Math.PI / 2;
                                ctx.beginPath(); ctx.arc(cx, cy, 18, a, a + 1.0);
                                ctx.strokeStyle = Qt.rgba(0.8, 0.1, 0.1, 0.6); ctx.lineWidth = 2; ctx.stroke();
                            }
                            // Middle ring (counter)
                            for (var j = 0; j < 3; j++) {
                                var b = -phase * 1.4 + j * 2.094;
                                ctx.beginPath(); ctx.arc(cx, cy, 12, b, b + 0.8);
                                ctx.strokeStyle = Qt.rgba(0.8, 0.1, 0.1, 0.4); ctx.lineWidth = 1.5; ctx.stroke();
                            }
                            // Inner ring
                            for (var k = 0; k < 6; k++) {
                                var c = phase * 2 + k * 1.047;
                                ctx.beginPath(); ctx.arc(cx, cy, 7, c, c + 0.4);
                                ctx.strokeStyle = Qt.rgba(0.8, 0.1, 0.1, 0.5); ctx.lineWidth = 1; ctx.stroke();
                            }
                            // Core
                            var grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, 5);
                            grd.addColorStop(0, "#FF4444"); grd.addColorStop(1, "#4A0E0E00");
                            ctx.beginPath(); ctx.arc(cx, cy, 5, 0, 2 * Math.PI);
                            ctx.fillStyle = grd; ctx.fill();
                        }
                    }

                    ColumnLayout {
                        spacing: 1
                        Text {
                            text: "ATLAS"
                            color: corePrimary
                            font { pixelSize: 20; bold: true; family: uiFont; letterSpacing: 4 }
                        }
                        Text {
                            text: JarvisBackend.greeting
                            color: coreDim
                            font { pixelSize: 10; family: monoFont; letterSpacing: 1 }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Time display
                    ColumnLayout {
                        spacing: 0
                        Text {
                            text: JarvisBackend.currentTime
                            color: corePrimary
                            font { pixelSize: 16; bold: true; family: monoFont }
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight
                        }
                        Text {
                            text: JarvisBackend.currentDate
                            color: coreDim
                            font { pixelSize: 8; family: monoFont }
                            Layout.alignment: Qt.AlignRight
                        }
                    }

                    // Connection status
                    Rectangle {
                        width: 8; height: 8; radius: 4
                        color: JarvisBackend.connected ? greenOk : redAlert
                        SequentialAnimation on opacity {
                            loops: Animation.Infinite
                            NumberAnimation { from: 1; to: 0.3; duration: 800 }
                            NumberAnimation { from: 0.3; to: 1; duration: 800 }
                        }
                    }
                }

                // ── Thin separator ──
                Rectangle { Layout.fillWidth: true; height: 1; color: borderDim }

                // ════ STATUS BAR ════
                Rectangle {
                    Layout.fillWidth: true; height: 22
                    color: bgDark; radius: 3
                    border.color: borderDim; border.width: 1
                    RowLayout {
                        anchors.fill: parent; anchors.margins: 4; spacing: 6
                        Rectangle {
                            width: 6; height: 6; radius: 3
                            color: JarvisBackend.processing ? orangeAccent :
                                   JarvisBackend.speaking ? corePrimary :
                                   JarvisBackend.voiceCommandMode ? greenOk : coreDim
                            SequentialAnimation on opacity {
                                running: JarvisBackend.processing || JarvisBackend.speaking || JarvisBackend.voiceCommandMode
                                loops: Animation.Infinite
                                NumberAnimation { from: 1; to: 0.2; duration: 500 }
                                NumberAnimation { from: 0.2; to: 1; duration: 500 }
                            }
                        }
                        Text {
                            text: JarvisBackend.statusText
                            color: "#bf3a3a"
                            font { pixelSize: 9; family: monoFont }
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }
                }

                // ════ TAB BAR ════
                RowLayout {
                    Layout.fillWidth: true; spacing: 4
                    Repeater {
                        model: [
                            { label: "CHAT", icon: "◈" },
                            { label: "SYSTEM", icon: "◉" },
                            { label: "SETUP", icon: "⚙" }
                        ]
                        Rectangle {
                            Layout.fillWidth: true; height: 26; radius: 3
                            color: currentTab === index ? Qt.rgba(0.82, 0.17, 0.17, 0.12) : "transparent"
                            border.color: currentTab === index ? corePrimary : borderDim
                            border.width: 1
                            Text {
                                anchors.centerIn: parent
                                text: modelData.icon + " " + modelData.label
                                color: currentTab === index ? corePrimary : coreDim
                                font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 }
                            }
                            MouseArea {
                                anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                onClicked: currentTab = index
                            }
                        }
                    }
                }

                // ════ TAB CONTENT ════
                StackLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true
                    currentIndex: currentTab

                    // ──────────── TAB 0: CHAT ────────────
                    ColumnLayout {
                        spacing: 6

                        // Audio waveform visualizer
                        Canvas {
                            id: waveformCanvas
                            Layout.fillWidth: true; Layout.preferredHeight: 32
                            visible: JarvisBackend.listening || JarvisBackend.speaking || JarvisBackend.voiceCommandMode

                            property real animPhase: 0
                            NumberAnimation on animPhase { from: 0; to: 2 * Math.PI; duration: 1500; loops: Animation.Infinite }
                            onAnimPhaseChanged: requestPaint()

                            onPaint: {
                                var ctx = getContext("2d");
                                ctx.reset();
                                var w = width, h = height, mid = h / 2;
                                var amp = JarvisBackend.voiceCommandMode ? 0.8 :
                                          JarvisBackend.speaking ? 0.5 : 0.3;
                                var level = Math.max(JarvisBackend.audioLevel * 4, 0.05);
                                var color = JarvisBackend.voiceCommandMode ? "#00ff88" :
                                            JarvisBackend.speaking ? "#f0a030" : "#D22B2B";

                                ctx.strokeStyle = color;
                                ctx.lineWidth = 1.5;
                                ctx.globalAlpha = 0.8;
                                ctx.beginPath();
                                for (var x = 0; x < w; x += 2) {
                                    var t = x / w * 4 * Math.PI;
                                    var y = mid + Math.sin(t + animPhase) * mid * amp * level
                                              + Math.sin(t * 2.5 - animPhase * 1.3) * mid * amp * level * 0.4;
                                    if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
                                }
                                ctx.stroke();

                                // Second wave (ghosted)
                                ctx.globalAlpha = 0.25;
                                ctx.beginPath();
                                for (var x2 = 0; x2 < w; x2 += 2) {
                                    var t2 = x2 / w * 4 * Math.PI;
                                    var y2 = mid + Math.sin(t2 + animPhase + 1) * mid * amp * level * 0.7;
                                    if (x2 === 0) ctx.moveTo(x2, y2); else ctx.lineTo(x2, y2);
                                }
                                ctx.stroke();
                            }
                        }

                        // Voice command mode indicator
                        Rectangle {
                            Layout.fillWidth: true; height: 28
                            visible: JarvisBackend.voiceCommandMode
                            color: Qt.rgba(0, 1, 0.53, 0.08); radius: 4
                            border.color: greenOk; border.width: 1
                            RowLayout {
                                anchors.centerIn: parent; spacing: 8
                                Rectangle { width: 8; height: 8; radius: 4; color: greenOk
                                    SequentialAnimation on opacity { loops: Animation.Infinite
                                        NumberAnimation { from: 1; to: 0.2; duration: 400 }
                                        NumberAnimation { from: 0.2; to: 1; duration: 400 }
                                    }
                                }
                                Text { text: "SPRACHBEFEHL AKTIV — JETZT SPRECHEN"; color: greenOk
                                    font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 }
                                }
                            }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                onClicked: JarvisBackend.stopVoiceCommand()
                            }
                        }

                        // Chat history
                        Rectangle {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            color: bgDark; radius: 6
                            border.color: borderDim; border.width: 1; clip: true

                            ListView {
                                id: chatView
                                anchors.fill: parent; anchors.margins: 8
                                model: JarvisBackend.chatHistory; spacing: 6; clip: true
                                onCountChanged: Qt.callLater(function() { chatView.positionViewAtEnd(); })

                                delegate: Item {
                                    width: chatView.width; height: msgCol.height + 6
                                    property var parts: modelData.split("|")
                                    property string role: parts[0]
                                    property string msg: parts.slice(1).join("|")

                                    ColumnLayout {
                                        id: msgCol; width: parent.width; spacing: 2
                                        RowLayout {
                                            spacing: 4
                                            Rectangle { width: 3; height: 10; radius: 1
                                                color: role === "user" ? orangeAccent : corePrimary }
                                            Text {
                                                text: role === "user" ? "DU" : (role === "system" ? "SYSTEM" : "ATLAS")
                                                color: role === "user" ? orangeAccent : (role === "system" ? "#886666" : corePrimary)
                                                font { pixelSize: 8; bold: true; family: monoFont; letterSpacing: 2 }
                                            }
                                        }
                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: msgTxt.contentHeight + 14
                                            color: role === "user" ? "#D22B2B" : (role === "system" ? "#101010" : "#081018")
                                            radius: 4
                                            border.color: role === "user" ? "#D22B2B" : (role === "system" ? "#333" : "#D22B2B")
                                            border.width: 1
                                            // Left accent bar
                                            Rectangle {
                                                width: 2; height: parent.height - 8; y: 4; x: 4; radius: 1
                                                color: role === "user" ? Qt.rgba(0.82, 0.17, 0.17, 0.3) : (role === "system" ? "#555" : Qt.rgba(0.82, 0.17, 0.17, 0.3))
                                            }
                                            Text {
                                                id: msgTxt
                                                anchors { fill: parent; margins: 7; leftMargin: 12 }
                                                text: msg
                                                color: role === "user" ? "#b0c4d8" : (role === "system" ? "#888" : "#D22B2B")
                                                font { pixelSize: role === "system" ? 9 : 11; family: uiFont; italic: role === "system" }
                                                wrapMode: Text.WordWrap; lineHeight: 1.3
                                            }
                                        }
                                    }
                                }

                                // Empty state
                                Column {
                                    anchors.centerIn: parent; visible: chatView.count === 0; spacing: 8
                                    Text {
                                        text: JarvisBackend.greeting
                                        color: coreDim; font { pixelSize: 16; family: uiFont }
                                        horizontalAlignment: Text.AlignHCenter
                                        anchors.horizontalCenter: parent.horizontalCenter
                                    }
                                    Text {
                                        text: "Wobei darf ich helfen?"
                                        color: Qt.rgba(0.82, 0.17, 0.17, 0.8)
                                        font { pixelSize: 12; italic: true; family: uiFont }
                                        horizontalAlignment: Text.AlignHCenter
                                        anchors.horizontalCenter: parent.horizontalCenter
                                    }
                                }
                            }
                        }

                        // Processing bar
                        Rectangle {
                            Layout.fillWidth: true; height: 2; color: bgCard; radius: 1
                            visible: JarvisBackend.processing
                            Rectangle {
                                id: procBar; width: parent.width * 0.25; height: 2; radius: 1
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0; color: "transparent" }
                                    GradientStop { position: 0.5; color: corePrimary }
                                    GradientStop { position: 1; color: "transparent" }
                                }
                                SequentialAnimation on x { loops: Animation.Infinite
                                    NumberAnimation { from: -procBar.width; to: procBar.parent.width; duration: 1500; easing.type: Easing.InOutQuad }
                                }
                            }
                        }

                        // Input area
                        RowLayout {
                            Layout.fillWidth: true; spacing: 5

                            // Mic button
                            Rectangle {
                                width: 34; height: 34; radius: 17
                                color: JarvisBackend.voiceCommandMode ? Qt.rgba(0, 1, 0.53, 0.15) :
                                       micArea.containsMouse ? Qt.rgba(0.82, 0.17, 0.17, 0.1) : "transparent"
                                border.color: JarvisBackend.voiceCommandMode ? greenOk : borderMid; border.width: 1
                                Text { anchors.centerIn: parent; text: "🎤"; font.pixelSize: 14 }
                                MouseArea {
                                    id: micArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        if (JarvisBackend.voiceCommandMode) JarvisBackend.stopVoiceCommand();
                                        else JarvisBackend.startVoiceCommand();
                                    }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true; height: 34
                                color: bgDark; radius: 6
                                border.color: inputField.activeFocus ? corePrimary : borderDim; border.width: 1
                                Behavior on border.color { ColorAnimation { duration: 200 } }

                                TextInput {
                                    id: inputField
                                    anchors { fill: parent; margins: 8 }
                                    color: "#D22B2B"; font { pixelSize: 12; family: uiFont }
                                    clip: true; verticalAlignment: TextInput.AlignVCenter; selectByMouse: true
                                    Text {
                                        anchors.fill: parent; verticalAlignment: Text.AlignVCenter
                                        text: "Sprich, Operator …"; color: "#D22B2B"
                                        font: parent.font; visible: !parent.text && !parent.activeFocus
                                    }
                                    onAccepted: { if (text.trim().length > 0) { JarvisBackend.sendMessage(text.trim()); text = ""; } }
                                    Keys.onEscapePressed: { text = ""; focus = false; }
                                }
                            }

                            // Send
                            Rectangle {
                                width: 34; height: 34; radius: 6
                                color: sendArea.containsMouse ? Qt.rgba(0.82, 0.17, 0.17, 0.12) : "transparent"
                                border.color: borderMid; border.width: 1
                                Text { anchors.centerIn: parent; text: "▶"; color: corePrimary; font.pixelSize: 14 }
                                MouseArea {
                                    id: sendArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                    onClicked: { if (inputField.text.trim().length > 0) { JarvisBackend.sendMessage(inputField.text.trim()); inputField.text = ""; } }
                                }
                            }
                        }

                        // Bottom controls
                        RowLayout {
                            Layout.fillWidth: true; spacing: 4
                            Repeater {
                                model: [
                                    { label: JarvisBackend.wakeWordActive ? "◉ WACH" : "○ WACH", active: JarvisBackend.wakeWordActive, action: "wake" },
                                    { label: "■ STOPP", active: false, action: "stop" },
                                    { label: JarvisBackend.ttsMuted ? "🔇 STUMM" : "🔊 STIMME", active: JarvisBackend.ttsMuted, action: "mute" },
                                    { label: "✕ LEEREN", active: false, action: "clear" }
                                ]
                                Rectangle {
                                    Layout.fillWidth: true; height: 26; radius: 3
                                    color: modelData.active ? Qt.rgba(0.82, 0.17, 0.17, 0.1) : "transparent"
                                    border.color: modelData.active ? corePrimary : borderDim; border.width: 1
                                    Text {
                                        anchors.centerIn: parent; text: modelData.label
                                        color: modelData.active ? corePrimary : coreDim
                                        font { pixelSize: 8; bold: true; family: monoFont; letterSpacing: 1 }
                                    }
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            if (modelData.action === "wake") JarvisBackend.toggleWakeWord();
                                            else if (modelData.action === "stop") JarvisBackend.stopSpeaking();
                                            else if (modelData.action === "mute") JarvisBackend.toggleTtsMute();
                                            else if (modelData.action === "clear") JarvisBackend.clearHistory();
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // ──────────── TAB 1: SYSTEMS ────────────
                    Flickable {
                        contentWidth: width
                        contentHeight: systemsCol.implicitHeight
                        clip: true
                        flickableDirection: Flickable.VerticalFlick
                        boundsBehavior: Flickable.StopAtBounds

                        ColumnLayout {
                            id: systemsCol
                            width: parent.width
                            spacing: 8

                            // System header
                            Text {
                                text: "◈ SYSTEMDIAGNOSE"
                                color: corePrimary
                                font { pixelSize: 11; bold: true; family: monoFont; letterSpacing: 2 }
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: borderDim }

                            // Host info
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: 50
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                ColumnLayout {
                                    anchors { fill: parent; margins: 10 }
                                    spacing: 4
                                    Text { text: "RECHNER: " + JarvisBackend.hostname; color: corePrimary
                                        font { pixelSize: 11; family: monoFont; bold: true } }
                                    Text { text: "KERNEL: " + JarvisBackend.kernelVersion + "  ·  LAUFZEIT: " + JarvisBackend.uptime
                                        color: coreDim; font { pixelSize: 9; family: monoFont } }
                                }
                            }

                            // CPU gauge
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: 70
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                ColumnLayout {
                                    anchors { fill: parent; margins: 10 }
                                    spacing: 6
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text { text: "CPU-LAST"; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                        Item { Layout.fillWidth: true }
                                        Text { text: JarvisBackend.cpuUsage.toFixed(1) + "%"; color: JarvisBackend.cpuUsage > 80 ? redAlert : corePrimary
                                            font { pixelSize: 14; bold: true; family: monoFont } }
                                    }
                                    // Bar
                                    Rectangle {
                                        Layout.fillWidth: true; height: 6; color: "#D22B2B"; radius: 3
                                        Rectangle {
                                            width: parent.width * Math.min(JarvisBackend.cpuUsage / 100, 1); height: 6; radius: 3
                                            gradient: Gradient {
                                                orientation: Gradient.Horizontal
                                                GradientStop { position: 0; color: "#D22B2B" }
                                                GradientStop { position: 0.7; color: JarvisBackend.cpuUsage > 80 ? "#ff4444" : corePrimary }
                                            }
                                            Behavior on width { NumberAnimation { duration: 300 } }
                                        }
                                    }
                                    Text { text: "TEMP: " + JarvisBackend.cpuTemp + " °C"; color: JarvisBackend.cpuTemp > 80 ? redAlert : coreDim
                                        font { pixelSize: 9; family: monoFont } }
                                }
                            }

                            // Memory gauge
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: 60
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                ColumnLayout {
                                    anchors { fill: parent; margins: 10 }
                                    spacing: 6
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text { text: "RAM"; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                        Item { Layout.fillWidth: true }
                                        Text {
                                            text: (JarvisBackend.memoryUsedGb > 0 ? JarvisBackend.memoryUsedGb.toFixed(1) : "0.0") + " / " + (JarvisBackend.memoryTotalGb > 0 ? JarvisBackend.memoryTotalGb.toFixed(1) : "0.0") + " GB"
                                            color: corePrimary; font { pixelSize: 12; bold: true; family: monoFont }
                                        }
                                    }
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Rectangle {
                                            Layout.fillWidth: true; height: 6; color: "#D22B2B"; radius: 3
                                            Rectangle {
                                                width: parent.width * Math.min(JarvisBackend.memoryUsage / 100, 1); height: 6; radius: 3
                                                gradient: Gradient {
                                                    orientation: Gradient.Horizontal
                                                    GradientStop { position: 0; color: "#D22B2B" }
                                                    GradientStop { position: 0.7; color: JarvisBackend.memoryUsage > 85 ? redAlert : corePrimary }
                                                }
                                                Behavior on width { NumberAnimation { duration: 300 } }
                                            }
                                        }
                                        Text {
                                            text: JarvisBackend.memoryUsage > 0 ? JarvisBackend.memoryUsage.toFixed(0) + "%" : "0%"
                                            color: coreDim; font { pixelSize: 9; family: monoFont }
                                        }
                                    }
                                }
                            }

                            // OMEGA Daemons
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: Math.max(120, daemonListView.contentHeight + 35)
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1; clip: true
                                ColumnLayout {
                                    anchors { fill: parent; margins: 10 }
                                    spacing: 6
                                    Text { text: "◈ OMEGA DAEMONS"; color: coreDim
                                        font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                    Rectangle { Layout.fillWidth: true; height: 1; color: borderDim }

                                    ListView {
                                        id: daemonListView
                                        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 5
                                        model: JarvisBackend.daemonStatus
                                        delegate: RowLayout {
                                            width: daemonListView.width; spacing: 8
                                            Rectangle {
                                                width: 8; height: 8; radius: 4
                                                color: modelData.active ? greenOk : redAlert
                                                SequentialAnimation on opacity {
                                                    running: !modelData.active
                                                    loops: Animation.Infinite
                                                    NumberAnimation { from: 1; to: 0.3; duration: 800 }
                                                    NumberAnimation { from: 0.3; to: 1; duration: 800 }
                                                }
                                            }
                                            Text {
                                                text: modelData.name.replace("omega-", "").toUpperCase()
                                                color: corePrimary
                                                font { pixelSize: 10; family: monoFont; bold: true }
                                                Layout.fillWidth: true
                                            }
                                            Text {
                                                text: modelData.status
                                                color: modelData.active ? coreDim : redAlert
                                                font { pixelSize: 8; family: monoFont }
                                            }

                                            // Control buttons
                                            RowLayout {
                                                spacing: 6
                                                Rectangle {
                                                    width: 18; height: 18; radius: 3; color: "transparent"
                                                    border.color: borderMid; border.width: 1
                                                    Text { anchors.centerIn: parent; text: "⟳"; color: coreDim; font.pixelSize: 10 }
                                                    MouseArea {
                                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                        onClicked: JarvisBackend.controlDaemon(modelData.name, "restart")
                                                    }
                                                }
                                                Rectangle {
                                                    width: 18; height: 18; radius: 3; color: "transparent"
                                                    border.color: borderMid; border.width: 1
                                                    Text {
                                                        anchors.centerIn: parent
                                                        text: modelData.active ? "■" : "▶"
                                                        color: coreDim; font.pixelSize: 8
                                                    }
                                                    MouseArea {
                                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                        onClicked: JarvisBackend.controlDaemon(modelData.name, modelData.active ? "stop" : "start")
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            // LLM Connection status
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: 50
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                RowLayout {
                                    anchors { fill: parent; margins: 10 }
                                    spacing: 10
                                    Rectangle { width: 10; height: 10; radius: 5
                                        color: JarvisBackend.connected ? greenOk : redAlert
                                        SequentialAnimation on opacity { loops: Animation.Infinite
                                            NumberAnimation { from: 1; to: 0.3; duration: 800 }
                                            NumberAnimation { from: 0.3; to: 1; duration: 800 }
                                        }
                                    }
                                    ColumnLayout {
                                        spacing: 2
                                        Text { text: "LLM SERVER"; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                        Text { text: JarvisBackend.connected ? ("CONNECTED — " + JarvisBackend.llmServerUrl) : "OFFLINE — RECONNECTING..."
                                            color: JarvisBackend.connected ? greenOk : redAlert
                                            font { pixelSize: 10; family: monoFont } }
                                    }
                                }
                            }

                            // Reminders section
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: Math.max(120, reminderListView.contentHeight + 50)
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1; clip: true
                                ColumnLayout {
                                    anchors { fill: parent; margins: 10 }
                                    spacing: 4
                                    Text { text: "⏰ AKTIVE ERINNERUNGEN"; color: coreDim
                                        font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                    Rectangle { Layout.fillWidth: true; height: 1; color: borderDim }

                                    ListView {
                                        id: reminderListView
                                        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 4
                                        model: JarvisBackend.activeReminders
                                        delegate: RowLayout {
                                            width: parent ? parent.width : 0; spacing: 8
                                            Text { text: modelData.time; color: orangeAccent; font { pixelSize: 10; family: monoFont } }
                                            Text { text: modelData.text; color: "#b0c4d8"; font { pixelSize: 10; family: uiFont }
                                                Layout.fillWidth: true; elide: Text.ElideRight }
                                            Text { text: "✕"; color: redAlert; font { pixelSize: 10; bold: true }
                                                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                    onClicked: JarvisBackend.removeReminder(index) }
                                            }
                                        }
                                        Text { anchors.centerIn: parent; visible: parent.count === 0
                                            text: "Keine aktiven Erinnerungen"; color: "#D22B2B"
                                            font { pixelSize: 10; italic: true; family: uiFont } }
                                    }
                                }
                            }
                        }
                    }

                    // ──────────── TAB 2: CONFIG ────────────
                    Flickable {
                        contentWidth: width
                        contentHeight: configCol.implicitHeight
                        clip: true
                        flickableDirection: Flickable.VerticalFlick
                        boundsBehavior: Flickable.StopAtBounds

                        ColumnLayout {
                            id: configCol
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "⚙ SCHNELLZUGRIFF"
                                color: corePrimary
                                font { pixelSize: 11; bold: true; family: monoFont; letterSpacing: 2 }
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: borderDim }

                            // ── STATUS INFO ──
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: statusInfoCol.implicitHeight + 20
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                ColumnLayout {
                                    id: statusInfoCol
                                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: 10 }
                                    spacing: 4
                                    Text { text: "STATUS"; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                    Text { text: "LLM: " + JarvisBackend.currentModelName; color: "#b0c4d8"; font { pixelSize: 9; family: monoFont } }
                                    Text { text: "Stimme: " + JarvisBackend.currentVoiceName; color: "#b0c4d8"; font { pixelSize: 9; family: monoFont } }
                                    Text { text: "Server: " + JarvisBackend.llmServerUrl; color: "#b0c4d8"; font { pixelSize: 9; family: monoFont } }
                                    Text { text: "Verbindung: " + (JarvisBackend.connected ? "Online" : "Offline"); color: JarvisBackend.connected ? greenOk : redAlert; font { pixelSize: 9; bold: true; family: monoFont } }
                                }
                            }

                            // ── VOICE SYNTHESIS SLIDERS ──
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: ttsCol.implicitHeight + 20
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                ColumnLayout {
                                    id: ttsCol
                                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: 10 }
                                    spacing: 10
                                    Text { text: "STIMM-SYNTHESE"; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }

                                    // Rate slider
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 2
                                        RowLayout { Layout.fillWidth: true
                                            Text { text: "TEMPO"; color: coreDim; font { pixelSize: 9; family: monoFont } }
                                            Item { Layout.fillWidth: true }
                                            Text { text: rateSlider.value.toFixed(2); color: corePrimary; font { pixelSize: 9; family: monoFont } }
                                        }
                                        Slider { id: rateSlider; Layout.fillWidth: true; Layout.preferredHeight: 24
                                            from: -1.0; to: 1.0; value: 0.05; stepSize: 0.05; onMoved: JarvisBackend.setTtsRate(value)
                                            background: Rectangle { x: rateSlider.leftPadding; width: rateSlider.availableWidth; height: 4; radius: 2
                                                y: rateSlider.topPadding + rateSlider.availableHeight/2 - 2; color: "#D22B2B"
                                                Rectangle { width: rateSlider.visualPosition * parent.width; height: 4; radius: 2; color: corePrimary } }
                                            handle: Rectangle { x: rateSlider.leftPadding + rateSlider.visualPosition*(rateSlider.availableWidth-width)
                                                y: rateSlider.topPadding + rateSlider.availableHeight/2 - 7; implicitWidth: 14; implicitHeight: 14; radius: 7
                                                color: rateSlider.pressed ? Qt.lighter(corePrimary,1.2) : corePrimary; border.color: "#D22B2B"; border.width: 2 } }
                                    }
                                    // Pitch slider
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 2
                                        RowLayout { Layout.fillWidth: true
                                            Text { text: "TON"; color: coreDim; font { pixelSize: 9; family: monoFont } }
                                            Item { Layout.fillWidth: true }
                                            Text { text: pitchSlider.value.toFixed(2); color: corePrimary; font { pixelSize: 9; family: monoFont } }
                                        }
                                        Slider { id: pitchSlider; Layout.fillWidth: true; Layout.preferredHeight: 24
                                            from: -1.0; to: 1.0; value: -0.1; stepSize: 0.05; onMoved: JarvisBackend.setTtsPitch(value)
                                            background: Rectangle { x: pitchSlider.leftPadding; width: pitchSlider.availableWidth; height: 4; radius: 2
                                                y: pitchSlider.topPadding + pitchSlider.availableHeight/2 - 2; color: "#D22B2B"
                                                Rectangle { width: pitchSlider.visualPosition * parent.width; height: 4; radius: 2; color: corePrimary } }
                                            handle: Rectangle { x: pitchSlider.leftPadding + pitchSlider.visualPosition*(pitchSlider.availableWidth-width)
                                                y: pitchSlider.topPadding + pitchSlider.availableHeight/2 - 7; implicitWidth: 14; implicitHeight: 14; radius: 7
                                                color: pitchSlider.pressed ? Qt.lighter(corePrimary,1.2) : corePrimary; border.color: "#D22B2B"; border.width: 2 } }
                                    }
                                    // Volume slider
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 2
                                        RowLayout { Layout.fillWidth: true
                                            Text { text: "LAUT"; color: coreDim; font { pixelSize: 9; family: monoFont } }
                                            Item { Layout.fillWidth: true }
                                            Text { text: (volSlider.value * 100).toFixed(0) + "%"; color: corePrimary; font { pixelSize: 9; family: monoFont } }
                                        }
                                        Slider { id: volSlider; Layout.fillWidth: true; Layout.preferredHeight: 24
                                            from: 0.0; to: 1.0; value: 0.85; stepSize: 0.05; onMoved: JarvisBackend.setTtsVolume(value)
                                            background: Rectangle { x: volSlider.leftPadding; width: volSlider.availableWidth; height: 4; radius: 2
                                                y: volSlider.topPadding + volSlider.availableHeight/2 - 2; color: "#D22B2B"
                                                Rectangle { width: volSlider.visualPosition * parent.width; height: 4; radius: 2; color: corePrimary } }
                                            handle: Rectangle { x: volSlider.leftPadding + volSlider.visualPosition*(volSlider.availableWidth-width)
                                                y: volSlider.topPadding + volSlider.availableHeight/2 - 7; implicitWidth: 14; implicitHeight: 14; radius: 7
                                                color: volSlider.pressed ? Qt.lighter(corePrimary,1.2) : corePrimary; border.color: "#D22B2B"; border.width: 2 } }
                                    }
                                }
                            }

                            // ── QUICK TIMERS ──
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: timerCol.implicitHeight + 20
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                ColumnLayout {
                                    id: timerCol
                                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: 10 }
                                    spacing: 8
                                    Text { text: "SCHNELL-TIMER"; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                    Flow {
                                        Layout.fillWidth: true; spacing: 6
                                        Repeater {
                                            model: [
                                                { label: "1 MIN", secs: 60 }, { label: "5 MIN", secs: 300 },
                                                { label: "15 MIN", secs: 900 }, { label: "30 MIN", secs: 1800 },
                                                { label: "1 STD", secs: 3600 }
                                            ]
                                            Rectangle {
                                                width: 68; height: 26; radius: 3
                                                color: timerBtnArea.containsMouse ? Qt.rgba(0.82, 0.17, 0.17, 0.1) : "transparent"
                                                border.color: borderMid; border.width: 1
                                                Text { anchors.centerIn: parent; text: modelData.label; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont } }
                                                MouseArea { id: timerBtnArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                                    onClicked: JarvisBackend.addReminder("Timer: " + modelData.label, modelData.secs) }
                                            }
                                        }
                                    }
                                }
                            }

                            // ── CONFIGURE HINT ──
                            Rectangle {
                                Layout.fillWidth: true; Layout.preferredHeight: hintCol.implicitHeight + 20
                                color: bgDark; radius: 6; border.color: borderDim; border.width: 1
                                ColumnLayout {
                                    id: hintCol
                                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: 10 }
                                    spacing: 6
                                    Text { text: "VOLLSTÄNDIGE EINSTELLUNGEN"; color: coreDim; font { pixelSize: 9; bold: true; family: monoFont; letterSpacing: 1 } }
                                    Text {
                                        text: "Rechtsklick auf das Plasmoid →\n„ATLAS Ω Voice konfigurieren …“\n(LLM, Stimmen, Sprachbefehle, mehr)."
                                        color: "#b0c4d8"
                                        font { pixelSize: 9; family: uiFont }
                                        lineHeight: 1.3
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ════ CONNECTIONS ════
    Connections {
        target: JarvisBackend
        function onWakeWordDetected() {
            root.expanded = true;
            currentTab = 0;
        }
        function onReminderTriggered(text) {
            root.expanded = true;
            currentTab = 0;
        }
    }
}
