# BlackHole Setup Guide

Esta guía explica cómo instalar y configurar [BlackHole](https://existential.audio/blackhole/) para grabar audio del sistema en macOS.

## ¿Qué es BlackHole?

BlackHole es un driver de audio virtual para macOS que crea un dispositivo de audio "loopback". Esto permite capturar cualquier sonido que se reproduce en tu Mac, como:

- 🎵 Música de Spotify, Apple Music, YouTube
- 🎬 Audio de videos y películas
- 🎮 Sonido de videojuegos
- 📞 Audio de llamadas (Zoom, Meet, etc.)

## Instalación

### Opción 1: Homebrew (Recomendado)

```bash
# Versión 2 canales (suficiente para la mayoría de casos)
brew install blackhole-2ch

# O versión 16 canales (para uso avanzado)
brew install blackhole-16ch
```

### Opción 2: Instalador Manual

1. Ve a [existential.audio/blackhole](https://existential.audio/blackhole/)
2. Ingresa tu email para recibir el enlace de descarga
3. Descarga el instalador `.pkg`
4. Ejecuta el instalador y sigue las instrucciones
5. Si macOS bloquea la instalación:
   - Ve a **Preferencias del Sistema > Seguridad y Privacidad**
   - En la pestaña **General**, haz clic en **"Permitir de todos modos"**

## Configuración

### Paso 1: Crear Multi-Output Device

Para grabar el audio del sistema **y** seguir escuchándolo por tus altavoces:

1. Abre **Audio MIDI Setup** (búscalo con Spotlight o en `/Applications/Utilities/`)

2. Haz clic en el botón **"+"** en la esquina inferior izquierda

3. Selecciona **"Create Multi-Output Device"**

4. En el nuevo dispositivo, marca las casillas de:
   - ✅ **BlackHole 2ch** (o 16ch)
   - ✅ **Tu dispositivo de salida** (ej: "MacBook Pro Speakers" o tus auriculares)

5. **IMPORTANTE**: Asegúrate de que tu dispositivo de salida esté como **Master Device** (el primero en la lista o marcado como tal)

6. Marca **"Drift Correction"** para BlackHole

7. (Opcional) Renombra el dispositivo haciendo doble clic en su nombre (ej: "Recording + Speakers")

![Audio MIDI Setup Example](https://existential.audio/blackhole/images/multi-output.png)

### Paso 2: Configurar Salida del Sistema

1. Ve a **Preferencias del Sistema > Sonido > Salida**
2. Selecciona el **Multi-Output Device** que acabas de crear
3. Nota: El control de volumen del sistema puede no funcionar con Multi-Output Device. Ajusta el volumen desde las aplicaciones individuales.

### Paso 3: Verificar la Configuración

1. Reproduce algo de audio (música, video, etc.)
2. Deberías escuchar el audio normalmente
3. Abre Terminal y ejecuta:

```bash
poetry run mp3recorder list-devices
```

Deberías ver **BlackHole 2ch** en la lista de dispositivos de entrada.

## Uso con MP3 Recorder

### Listar Dispositivos

```bash
poetry run mp3recorder list-devices
```

Ejemplo de salida:
```
Available Audio Input Devices:
------------------------------------------------------------
  [0] MacBook Pro Microphone (default)
      Channels: 1, Sample Rate: 48000 Hz
  [1] BlackHole 2ch
      Channels: 2, Sample Rate: 48000 Hz
------------------------------------------------------------
Total: 2 device(s)
```

### Grabar Audio del Sistema

```bash
# Grabar 30 segundos de audio del sistema
poetry run mp3recorder record --duration 30 --device "BlackHole" --output mi_grabacion.mp3
```

### Ejemplo de Flujo Completo

1. **Configura BlackHole** (sigue los pasos anteriores)

2. **Inicia la reproducción** del audio que quieres grabar

3. **Ejecuta la grabación**:
   ```bash
   poetry run mp3recorder record --duration 60 --device "BlackHole" --output grabacion.mp3
   ```

4. **Espera** a que termine la grabación

5. **Verifica el archivo**:
   ```bash
   afplay grabacion.mp3
   ```

## Solución de Problemas

### No aparece BlackHole en la lista de dispositivos

- Reinicia tu Mac después de instalar BlackHole
- Verifica en Audio MIDI Setup que BlackHole esté visible

### No hay audio en la grabación

- Asegúrate de que el **Multi-Output Device** esté seleccionado como salida del sistema
- Verifica que haya audio reproduciéndose durante la grabación

### Audio distorsionado o con eco

- Revisa que **Drift Correction** esté habilitado para BlackHole en Audio MIDI Setup
- Asegúrate de no tener el micrófono capturando audio de los altavoces

### El volumen del sistema no funciona

Esto es normal con Multi-Output Device. Opciones:
- Ajusta el volumen en cada aplicación
- Usa auriculares con control de volumen
- Cambia temporalmente a tu dispositivo normal cuando no estés grabando

## Desinstalación

Si necesitas desinstalar BlackHole:

```bash
# Con Homebrew
brew uninstall blackhole-2ch

# Manual: ejecuta el script de desinstalación incluido
# O elimina estos archivos:
sudo rm -rf /Library/Audio/Plug-Ins/HAL/BlackHole.driver
sudo launchctl kickstart -kp system/com.apple.audio.coreaudiod
```

## Referencias

- [Sitio oficial de BlackHole](https://existential.audio/blackhole/)
- [Repositorio en GitHub](https://github.com/ExistentialAudio/BlackHole)
- [Documentación de Apple: Audio MIDI Setup](https://support.apple.com/guide/audio-midi-setup/)
