import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

// Widget de agenda: oculto por defecto, se muestra/oculta con
//   qs -c ii ipc call calwidget toggle
PanelWindow {
    id: root

    // --- Ajustes rápidos ---
    property string feedScript: Quickshell.env("HOME") + "/.config/quickshell/ii/calfeed.py"
    property string sourcesFile: Quickshell.env("HOME") + "/.config/quickshell/ii/sources.txt"
    property int refreshMs: 600000
    property int maxEvents: 12

    property bool shown: false
    property var events: []
    property var errors: []

    visible: shown
    onShownChanged: if (shown && !feed.running) feed.running = true

    WlrLayershell.layer: WlrLayer.Top
    WlrLayershell.namespace: "calwidget"
    exclusionMode: ExclusionMode.Ignore
    anchors { top: true; right: true }
    margins { top: 60; right: 24 }
    implicitWidth: 360
    implicitHeight: 480
    color: "transparent"

    IpcHandler {
        target: "calwidget"
        function toggle(): void { root.shown = !root.shown }
        function show(): void { root.shown = true }
        function hide(): void { root.shown = false }
    }

    SystemClock { id: clock; precision: SystemClock.Minutes }

    Process {
        id: feed
        command: ["python3", root.feedScript, "--sources", root.sourcesFile]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    const d = JSON.parse(text)
                    root.events = d.events
                    root.errors = d.errors
                } catch (e) {
                    root.errors = ["No pude leer el JSON: " + e]
                }
            }
        }
    }

    Timer {
        interval: root.refreshMs
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: if (!feed.running) feed.running = true
    }

    readonly property var _dias: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
    readonly property var _meses: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    function fechaLarga(d) { return root._dias[d.getDay()] + " " + d.getDate() + " de " + root._meses[d.getMonth()] }
    function fechaCorta(d) { return root._dias[d.getDay()].slice(0, 3) + " " + d.getDate() + " " + root._meses[d.getMonth()].slice(0, 3) }

    function dayLabel(epoch) {
        const d = new Date(epoch * 1000)
        const today = new Date(); today.setHours(0, 0, 0, 0)
        const diff = Math.round((new Date(d).setHours(0, 0, 0, 0) - today) / 86400000)
        if (diff === 0) return "Hoy"
        if (diff === 1) return "Mañana"
        return root.fechaCorta(d)
    }

    Rectangle {
        anchors.fill: parent
        radius: 18
        color: "#99101418"
        border.width: 1
        border.color: "#22ffffff"
        Text { text: "✕"; color: "#aab2bd"; font.pixelSize: 16; z: 10; anchors.top: parent.top; anchors.right: parent.right; anchors.topMargin: 12; anchors.rightMargin: 14; MouseArea { anchors.fill: parent; anchors.margins: -8; onClicked: root.shown = false } }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 12

            Text {
                text: root.fechaLarga(clock.date)
                color: "#ffffff"
                font.pixelSize: 20
                font.bold: true
            }

            Text {
                visible: root.errors.length > 0
                text: "⚠ " + root.errors.join("\n")
                color: "#ffb86c"
                font.pixelSize: 11
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            ListView {
                id: list
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: 8
                model: root.events.slice(0, root.maxEvents)

                delegate: Rectangle {
                    required property var modelData
                    width: list.width
                    height: 54
                    radius: 10
                    opacity: modelData.overdue ? 0.45 : 1
                    color: modelData.urgent ? "#44ff5555" : "#1fffffff"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 2

                        Text {
                            text: modelData.title
                            color: "#ffffff"
                            font.pixelSize: 13
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        Text {
                            text: root.dayLabel(modelData.epoch) + " · "
                                  + Qt.formatDateTime(new Date(modelData.epoch * 1000), "HH:mm")
                                  + (modelData.course ? " · " + modelData.course : "")
                            color: modelData.urgent ? "#ff9d9d" : "#aab2bd"
                            font.pixelSize: 11
                        }
                    }
                }
            }

            Text {
                visible: root.events.length === 0 && root.errors.length === 0
                text: "Sin eventos próximos"
                color: "#aab2bd"
                font.pixelSize: 12
            }
        }
    }
}
