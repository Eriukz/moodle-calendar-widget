## Versión para Waybar

Si usas Waybar en vez de Quickshell, hay un módulo `custom` que reutiliza `calfeed.py`.
Waybar no dibuja paneles propios, así que funciona como **ícono + próximo evento en la barra**,
con la **lista completa en el tooltip** al pasar el mouse y una **notificación** al hacer clic.

1. Copia `calfeed.py` y `waybar-calendar.py` a la misma carpeta:
   ```sh
   mkdir -p ~/.config/quickshell/calendar-widget
   cp calfeed.py waybar-calendar.py ~/.config/quickshell/calendar-widget/
   ```
2. Crea tu `sources.txt` como en la instalación normal (paso 2 de arriba).
3. Prueba el módulo solo; debe imprimir una línea de JSON con `text`, `tooltip` y `class`:
   ```sh
   python3 ~/.config/quickshell/calendar-widget/waybar-calendar.py --lang es
   ```
4. Agrega el bloque de `examples/waybar/config.jsonc` a tu config de Waybar, y `"custom/calendar"`
   a la lista de módulos de la barra.
5. Agrega los estilos de `examples/waybar/style.css` y reinicia Waybar (`pkill waybar && waybar &`).

Opciones: `--lang es|en`, `--max N` (filas del tooltip), `--icon "texto"`. Cualquier otra opción
(`--sources`, `--days`, `--urgent-hours`) se pasa a `calfeed.py`.

- **El ícono sale como un cuadro:** el ícono por defecto es de Nerd Fonts. Instala una Nerd Font
  o cambia el ícono con `--icon "📅"`.
- **Refrescar al instante:** `pkill -SIGRTMIN+8 waybar` (usa el `"signal": 8` del ejemplo).
- **El clic no muestra nada:** necesitas `notify-send` y un demonio de notificaciones (dunst, mako, swaync).
