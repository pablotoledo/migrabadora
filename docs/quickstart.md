# Guía de Inicio Rápido - MP3 Recorder

Manual paso a paso para configurar y usar el grabador MP3 en macOS.

---

## 📋 Requisitos Previos

| Requisito | Estado | Comando de verificación |
|-----------|--------|------------------------|
| Python 3.10+ | ✅ | `python3 --version` |
| Poetry | ✅ | `poetry --version` |
| FFmpeg | ✅ | `which ffmpeg` |
| BlackHole | ⚠️ Opcional | Solo para grabar audio del sistema |

---

## 🚀 Instalación

### 1. Instalar dependencias del proyecto

```bash
cd /Users/U10089513/Desktop/recording
poetry install
```

### 2. Verificar que FFmpeg está instalado

```bash
which ffmpeg
# Si no está instalado:
brew install ffmpeg
```

---

## 🎙️ Uso Básico - Grabar desde Micrófono

### Listar dispositivos disponibles

```bash
poetry run mp3recorder list-devices
```

Salida ejemplo:
```
Available Audio Input Devices:
------------------------------------------------------------
  [0] Jabra Evolve 75 SE (default)
      Channels: 1, Sample Rate: 16000 Hz
  [6] MacBook Pro Microphone
      Channels: 1, Sample Rate: 48000 Hz
------------------------------------------------------------
```

### Grabar audio (micrófono interno)

```bash
# Grabar 10 segundos desde el micrófono del MacBook
poetry run mp3recorder record -d 10 --device "MacBook" --channels 1 -o grabacion.mp3
```

### Opciones de grabación

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `-d, --duration` | Duración en segundos | `-d 30` |
| `-o, --output` | Archivo de salida | `-o audio.mp3` |
| `--device` | Nombre del dispositivo (parcial) | `--device "MacBook"` |
| `--channels` | Canales: 1=mono, 2=stereo | `--channels 1` |
| `--bitrate` | Calidad: 128, 192, 256, 320 | `--bitrate 320` |

---

## 🔊 Configuración de BlackHole (Audio del Sistema)

BlackHole permite capturar el audio que suena en tu Mac (Spotify, YouTube, etc.).

### Paso 1: Instalar BlackHole

```bash
brew install blackhole-2ch
```

### Paso 2: Configurar Multi-Output Device

1. Abre **Audio MIDI Setup**:
   ```bash
   open /Applications/Utilities/Audio\ MIDI\ Setup.app
   ```

2. Haz clic en el botón **"+"** (esquina inferior izquierda)

3. Selecciona **"Create Multi-Output Device"**

4. Marca las casillas:
   - ✅ **BlackHole 2ch**
   - ✅ **Tu dispositivo de salida** (ej: MacBook Pro Speakers)

5. Habilita **"Drift Correction"** para BlackHole

6. *Opcional*: Renombra el dispositivo a "Recording + Speakers"

### Paso 3: Configurar Salida del Sistema

1. Ve a **Preferencias del Sistema > Sonido > Salida**
2. Selecciona el **Multi-Output Device** que creaste

> ⚠️ **Nota**: El control de volumen del sistema no funciona con Multi-Output Device. Ajusta el volumen en las aplicaciones.

### Paso 4: Grabar Audio del Sistema

```bash
# Inicia música o video, luego ejecuta:
poetry run mp3recorder record -d 30 --device "BlackHole" -o sistema.mp3
```

---

## ✅ Verificación

### Probar que funciona

```bash
# 1. Lista dispositivos
poetry run mp3recorder list-devices

# 2. Graba 5 segundos de prueba
poetry run mp3recorder record -d 5 --device "MacBook" --channels 1 -o test.mp3

# 3. Reproduce la grabación
afplay test.mp3
```

### Verificar archivo MP3

```bash
file test.mp3
# Debe mostrar: Audio file with ID3 version 2.4.0, contains: MPEG ADTS...
```

---

## 🔧 Solución de Problemas

| Error | Solución |
|-------|----------|
| `Invalid number of channels` | Usa `--channels 1` para dispositivos mono |
| `Device not found` | Verifica el nombre con `list-devices` |
| `No audio in recording` | Comprueba que Multi-Output Device está activo |
| `ffmpeg not found` | Ejecuta `brew install ffmpeg` |

---

## 📁 Archivos del Proyecto

```
recording/
├── docs/
│   ├── blackhole_setup.md  # Guía detallada de BlackHole
│   └── usage.md            # Documentación completa de la API
├── src/mp3recorder/        # Código fuente
└── tests/                  # Tests unitarios
```

---

*Generado el 28 de enero de 2026*
