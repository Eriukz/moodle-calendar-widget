# moodle-calendar-widget

Widget de escritorio para Linux que muestra tus entregas de Moodle (y cualquier calendario `.ics`) en un panel flotante. Funciona con **Quickshell** y tiene una versión para **Waybar**.

<!-- Para agregar una captura: sube captura.png al repo y descomenta la línea de abajo -->
<!-- ![Captura del widget](captura.png) -->

## Qué hace

- Lee tu calendario de Moodle por su enlace de exportación `.ics` y muestra los próximos eventos.
- Marca en rojo lo que vence en menos de 24 horas y atenúa lo vencido.
- Se actualiza solo cada 10 minutos.
- Si una fuente falla, muestra el error en el widget sin tumbarlo.
- Solo usa la librería estándar de Python, sin dependencias extra.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `calfeed.py` | Lee las fuentes `.ics` y escupe JSON con los eventos |
| `CalendarWidget.qml` | Panel flotante para Quickshell |
| `waybar-calendar.py` | Módulo para Waybar (reutiliza `calfeed.py`) |
| `examples/waybar/` | Ejemplos de `config.jsonc` y `style.css` para Waybar |

## Requisitos

- Python 3
- Quickshell (para el panel) o Waybar (para el módulo de barra)
- Opcional para Waybar: `notify-send` y un demonio de notificaciones (dunst, mako, swaync)

## 1. Obtén tu enlace de Moodle

En Moodle ve a **Calendario → Importar o exportar calendarios → Exportar calendario**, elige los eventos que quieras y pulsa **Obtener URL del calendario**. Copia el enlace.

> **Ojo:** ese enlace incluye un token personal. Quien lo tenga puede ver tu calendario. No lo subas a GitHub ni lo compartas.

## 2. Crea tu archivo de fuentes

Crea `sources.txt` (una fuente por línea):

```
moodle=https://TU-MOODLE/calendar/export_execute.php?...
local=/ruta/a/archivo.ics
```

- `moodle=` es una URL. `local=` es un archivo, útil para pruebas.
- Las líneas que empiezan con `#` se ignoran.
- `sources.txt` **no se sube al repo** (está en `.gitignore`).

## 3A. Instalación en Quickshell

1. Copia los archivos a tu configuración de Quickshell (aquí se usa `~/.config/quickshell/ii/`):
   ```sh
   cp calfeed.py CalendarWidget.qml ~/.config/quickshell/ii/
   ```
2. Pon tu `sources.txt` en la misma carpeta (`~/.config/quickshell/ii/sources.txt`).
3. Agrega `CalendarWidget {}` al `shell.qml` (o al módulo que cargue tus ventanas) y reinicia Quickshell.
4. Muestra u oculta el panel con:
   ```sh
   qs -c ii ipc call calwidget toggle
   ```
   También existen `show` y `hide`. Para usarlo con un atajo en Hyprland:
   ```
   bind = SUPER, K, exec, qs -c ii ipc call calwidget toggle
   ```

Si tu configuración no se llama `ii`, cambia el nombre en el comando (`qs -c TU_CONFIG ...`) y las rutas al inicio de `CalendarWidget.qml`.

## 3B. Versión para Waybar

Waybar no dibuja paneles propios, así que funciona como **ícono + próximo evento en la barra**, con la **lista completa en el tooltip** al pasar el mouse y una **notificación** al hacer clic.

1. Copia `calfeed.py` y `waybar-calendar.py` a la misma carpeta:
   ```sh
   mkdir -p ~/.config/quickshell/calendar-widget
   cp calfeed.py waybar-calendar.py ~/.config/quickshell/calendar-widget/
   ```
2. Por defecto `calfeed.py` busca las fuentes en `~/.config/quickshell/secrets/sources.txt`. Crea ahí tu `sources.txt`, o indica otra ruta con `--sources RUTA`.
3. Prueba el módulo solo. Debe imprimir una línea de JSON con `text`, `tooltip` y `class`:
   ```sh
   python3 ~/.config/quickshell/calendar-widget/waybar-calendar.py --lang es
   ```
4. Agrega el bloque de `examples/waybar/config.jsonc` a tu configuración de Waybar y `"custom/calendar"` a la lista de módulos de la barra.
5. Agrega los estilos de `examples/waybar/style.css` y reinicia Waybar:
   ```sh
   pkill waybar && waybar &
   ```

**Opciones:** `--lang es|en`, `--max N` (filas del tooltip), `--icon "texto"`. Cualquier otra opción (`--sources`, `--days`) se pasa a `calfeed.py`.

## Nombres de materias

Moodle manda un código por materia (por ejemplo `GRRD26B_224424`). Para mostrar un nombre corto, edita el diccionario `COURSES` al inicio de `calfeed.py`:

```python
COURSES = {
    "GRRD26B_224424": "Gestión de Riesgos",
}
```

Si no lo llenas, el widget muestra la primera parte del código.

## Problemas comunes

- **El ícono sale como un cuadro:** el ícono por defecto es de Nerd Fonts. Instala una Nerd Font o usa `--icon "📅"`.
- **No aparecen eventos:** revisa que `sources.txt` exista en la ruta correcta y que la URL de Moodle siga vigente. El widget muestra el error en pantalla.
- **Las horas salen corridas:** `calfeed.py` usa la zona horaria de México (UTC-6). Cambia la línea `TZ = timezone(timedelta(hours=-6))` si estás en otra.
- **Refrescar al instante en Waybar:** `pkill -SIGRTMIN+8 waybar` (usa el `"signal": 8` del ejemplo).
- **El clic en Waybar no muestra nada:** instala `notify-send` y un demonio de notificaciones.

## Seguridad

Tu enlace de Moodle es privado y `sources.txt` está excluido del repo con `.gitignore`. No pegues tu enlace en capturas, issues ni mensajes de error. Si lo subiste por error, genera un enlace nuevo desde Moodle para invalidar el anterior.
