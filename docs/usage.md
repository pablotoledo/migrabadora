# Guía de Uso - MP3 Recorder

Esta guía describe cómo usar la aplicación MP3 Recorder desde la terminal.

## Requisitos Previos

- Python 3.10+
- FFmpeg instalado (`brew install ffmpeg`)
- Dependencias instaladas (`poetry install`)

## Comandos Disponibles

### Listar Dispositivos de Audio

```bash
poetry run mp3recorder list-devices
```

Muestra todos los dispositivos de entrada de audio disponibles en el sistema.

**Salida de ejemplo:**
```
Available Audio Input Devices:
------------------------------------------------------------
  [0] MacBook Pro Microphone (default)
      Channels: 1, Sample Rate: 48000 Hz
  [1] BlackHole 2ch
      Channels: 2, Sample Rate: 48000 Hz
  [2] USB Audio Device
      Channels: 2, Sample Rate: 44100 Hz
------------------------------------------------------------
Total: 3 device(s)
```

### Grabar Audio

```bash
poetry run mp3recorder record --duration <segundos> --output <archivo.mp3> [opciones]
```

**Argumentos requeridos:**
- `-d, --duration`: Duración de la grabación en segundos
- `-o, --output`: Ruta del archivo MP3 de salida

**Opciones:**
- `--device`: Nombre del dispositivo (búsqueda parcial, ej: "BlackHole")
- `--sample-rate`: Frecuencia de muestreo en Hz (default: 44100)
- `--channels`: Número de canales, 1=mono, 2=stereo (default: 2)
- `--bitrate`: Bitrate MP3 en kbps: 128, 192, 256, 320 (default: 192)

## Ejemplos de Uso

### Grabación Básica (Micrófono)

```bash
# Grabar 10 segundos desde el micrófono por defecto
poetry run mp3recorder record -d 10 -o grabacion.mp3
```

### Grabar Audio del Sistema (BlackHole)

```bash
# Grabar 60 segundos del audio del sistema
poetry run mp3recorder record -d 60 --device "BlackHole" -o sistema.mp3
```

### Grabación de Alta Calidad

```bash
# Grabar con máxima calidad
poetry run mp3recorder record -d 30 -o hq.mp3 --bitrate 320 --sample-rate 48000
```

### Grabación Mono

```bash
# Grabar en mono (archivo más pequeño)
poetry run mp3recorder record -d 20 -o mono.mp3 --channels 1
```

### Usar como Módulo Python

```bash
# Ejecutar como módulo
poetry run python -m mp3recorder list-devices
poetry run python -m mp3recorder record -d 5 -o test.mp3
```

## Uso Programático

También puedes usar el grabador como biblioteca Python:

```python
from mp3recorder import AudioRecorder
from mp3recorder.devices import list_audio_devices, get_device_by_name

# Listar dispositivos
devices = list_audio_devices()
for d in devices:
    print(f"{d.name}: {d.channels}ch @ {d.sample_rate}Hz")

# Grabar con dispositivo específico
blackhole = get_device_by_name("BlackHole")
if blackhole:
    recorder = AudioRecorder(device=blackhole.index)
    recorder.record(duration=10)
    recorder.save_mp3("output.mp3")

# Función de conveniencia
from mp3recorder.recorder import record_audio
record_audio(
    duration=30,
    output_path="grabacion.mp3",
    device="BlackHole",
    bitrate="256k"
)
```

## Reproducir Grabaciones

Después de grabar, puedes reproducir el archivo con:

```bash
# Reproductor integrado de macOS
afplay grabacion.mp3

# O abre con el reproductor por defecto
open grabacion.mp3
```

## Notas Importantes

1. **FFmpeg es obligatorio** para la codificación MP3. Si no está instalado, la grabación fallará al intentar guardar.

2. **Permisos de micrófono**: La primera vez que ejecutes la grabación, macOS puede solicitar permiso para acceder al micrófono.

3. **Duración**: No hay límite de duración, pero grabaciones muy largas consumirán más memoria RAM durante el proceso.

4. **Formato de salida**: Actualmente solo se soporta MP3. Para WAV, usa la API programática con `recorder.save_wav()`.
