#!/usr/bin/env python3
"""calfeed.py - junta fuentes .ics (Moodle, y luego Google) y escupe JSON para el widget.

Fuentes: archivo ~/.config/quickshell/secrets/sources.txt, una por línea:
    moodle=https://...export_execute.php?...        (URL)
    local=/ruta/a/archivo.ics                         (archivo, útil para pruebas)
Uso:  calfeed.py [--days 30] [--sources RUTA]
Solo usa la librería estándar.
"""
import argparse, json, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=-6))  # México ya no usa horario de verano

# Edita esto: código de categoría de Moodle -> nombre corto de la materia
COURSES = {
    # "GRRD26B_224424": "Gestión de Riesgos",
}

def read_source(spec):
    name, _, loc = spec.partition("=")
    if loc.startswith(("http://", "https://")):
        with urllib.request.urlopen(loc, timeout=20) as r:
            return name, r.read().decode("utf-8", "replace")
    with open(os.path.expanduser(loc), encoding="utf-8") as f:
        return name, f.read()

def unfold(text):
    out = []
    for line in text.replace("\r\n", "\n").split("\n"):
        if line[:1] in (" ", "\t") and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out

def unescape(s):
    return (s.replace("\\n", "\n").replace("\\,", ",")
             .replace("\\;", ";").replace("\\\\", "\\"))

def parse_dt(val):
    val = val.strip()
    if re.fullmatch(r"\d{8}T\d{6}Z", val):
        return datetime.strptime(val, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).astimezone(TZ)
    if re.fullmatch(r"\d{8}T\d{6}", val):
        return datetime.strptime(val, "%Y%m%dT%H%M%S").replace(tzinfo=TZ)
    if re.fullmatch(r"\d{8}", val):
        return datetime.strptime(val, "%Y%m%d").replace(tzinfo=TZ)
    return None

def parse_events(text, source):
    events, cur = [], None
    for line in unfold(text):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT" and cur is not None:
            start = parse_dt(cur.get("DTSTART", ""))
            if start:
                title = unescape(cur.get("SUMMARY", "(sin título)"))
                title = re.sub(r"\s+está en fecha de entrega$", "", title)
                cat = cur.get("CATEGORIES", "")
                events.append({
                    "title": title,
                    "source": source,
                    "course": COURSES.get(cat, cat.split("_")[0] if cat else ""),
                    "start": start,
                })
            cur = None
        elif cur is not None and ":" in line:
            key, _, val = line.partition(":")
            cur[key.split(";")[0]] = val
    return events

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--sources", default="~/.config/quickshell/secrets/sources.txt")
    args = ap.parse_args()

    with open(os.path.expanduser(args.sources), encoding="utf-8") as f:
        specs = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    now = datetime.now(TZ)
    lo, hi = now - timedelta(days=1), now + timedelta(days=args.days)
    events, errors = [], []
    for spec in specs:
        try:
            name, text = read_source(spec)
            events += parse_events(text, name)
        except Exception as e:  # una fuente caída no tumba el widget
            errors.append(f"{spec.split('=')[0]}: {e}")

    events = sorted((e for e in events if lo <= e["start"] <= hi), key=lambda e: e["start"])
    out = []
    for e in events:
        delta = e["start"] - now
        out.append({
            "title": e["title"], "source": e["source"], "course": e["course"],
            "start": e["start"].isoformat(), "epoch": int(e["start"].timestamp()),
            "overdue": delta.total_seconds() < 0,
            "urgent": 0 <= delta.total_seconds() < 86400,
        })
    json.dump({"generated": now.isoformat(), "events": out, "errors": errors},
              sys.stdout, ensure_ascii=False)

if __name__ == "__main__":
    main()
