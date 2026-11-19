#!/usr/bin/env python3
"""waybar-calendar.py - Waybar custom module for the calendar widget.

Runs calfeed.py (same folder) and prints one line of Waybar JSON:
  text (icon + next event), tooltip (upcoming list), class (urgent / empty / error / normal).

Waybar config:  "exec": "python3 ~/.config/quickshell/calendar-widget/waybar-calendar.py --lang es"
Options:  --lang es|en   --max N (tooltip rows)   --icon STR   --notify (send the list as a
notification and exit). Any other option (--sources, --days, --urgent-hours) goes to calfeed.py.
"""
import argparse, html, json, os, subprocess, sys
from datetime import datetime

HERE = os.path.dirname(os.path.realpath(__file__))

T = {
    "es": {"none": "Sin eventos próximos", "today": "Hoy", "tomorrow": "Mañana",
           "days": ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"],
           "months": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]},
    "en": {"none": "No upcoming events", "today": "Today", "tomorrow": "Tomorrow",
           "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
           "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]},
}


def label(t, epoch):
    d = datetime.fromtimestamp(epoch)
    diff = (d.date() - datetime.now().date()).days
    if diff == 0:
        day = t["today"]
    elif diff == 1:
        day = t["tomorrow"]
    else:
        day = f'{t["days"][d.weekday()]} {d.day} {t["months"][d.month - 1]}'
    return f"{day} {d.strftime('%H:%M')}"


def load(passthrough):
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "calfeed.py"), *passthrough],
                           capture_output=True, text=True, timeout=45)
        return json.loads(r.stdout)
    except Exception as e:  # never print details: they could contain URLs
        return {"events": [], "errors": [f"calfeed: {type(e).__name__}"]}


def short(s, n=60):
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="es", choices=sorted(T))
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--icon", default="")
    ap.add_argument("--notify", action="store_true")
    args, passthrough = ap.parse_known_args()
    t = T[args.lang]

    data = load(passthrough)
    events, errors = data.get("events", []), data.get("errors", [])
    upcoming = [e for e in events if not e["overdue"]]
    urgent = [e for e in upcoming if e["urgent"]]

    if args.notify:
        body = "\n".join(f'{label(t, e["epoch"])}  {html.escape(short(e["title"]))}'
                         for e in upcoming[: args.max]) or t["none"]
        try:
            subprocess.run(["notify-send", "-a", "Calendar", "Calendar", body], timeout=10)
        except Exception:
            print(body)
        return

    lines = []
    for e in events[: args.max]:
        course = f' · {html.escape(e["course"])}' if e["course"] else ""
        row = f'{html.escape(label(t, e["epoch"]))}  {html.escape(short(e["title"]))}{course}'
        if e["overdue"]:
            row = f'<span alpha="55%">{row}</span>'
        elif e["urgent"]:
            row = f'<span foreground="#ff7a7a">{row}</span>'
        lines.append(row)
    for er in errors:
        lines.append(f'<span foreground="#ffb86c">⚠ {html.escape(er)}</span>')

    if errors and not events:
        cls = "error"
    elif not upcoming:
        cls = "empty"
    elif urgent:
        cls = "urgent"
    else:
        cls = "normal"

    text = f'{args.icon} {label(t, upcoming[0]["epoch"])}' if upcoming else args.icon
    print(json.dumps({"text": text, "tooltip": "\n".join(lines) or t["none"], "class": cls},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
