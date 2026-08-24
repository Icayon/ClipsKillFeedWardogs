<div align="center">

<img src="assets/app_icon.png" width="120" alt="Clips KillFeed Wardogs Logo">

# Clips KillFeed Wardogs
**Herramienta de detección de bajas y generación automática de clips para Wardogs**

[![Release](https://img.shields.io/github/v/release/Icayon/ClipsKillFeedWardogs?color=2563eb&style=flat-square)](https://github.com/Icayon/ClipsKillFeedWardogs/releases/latest)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Twitch](https://img.shields.io/badge/Twitch-icayon-9146FF?style=flat-square&logo=twitch&logoColor=white)](https://www.twitch.tv/icayon)
[![Twitter](https://img.shields.io/badge/Twitter%20%2F%20X-@ICayonh-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/ICayonh)

[Español](#español) | [English](#english)

</div>

---

## Español

### Descripción
**Clips KillFeed Wardogs** es una aplicación de escritorio diseñada para jugadores y creadores de contenido de Wardogs. Permite procesar grabaciones de partidas largas (OBS / ShadowPlay) y extraer automáticamente cada baja individual o jugada destacada sin necesidad de revisar manualmente horas de metraje.

### Características principales
- **Detección por OCR local**: Reconocimiento de texto en tiempo real sobre el Killfeed para identificar bajas asociadas a tu gamertag.
- **Registro de distancia**: Lectura y catalogación de la distancia de cada enfrentamiento (ej. [45m]).
- **Análisis de picos de audio**: Detección de momentos de alta intensidad vocal en la pista del micrófono para priorizar jugadas destacadas.
- **Preservación de calidad original**: Exportación sin pérdida de resolución ni tasa de bits respecto a la grabación original.
- **Exportación multiformato**:
  - Horizontal 16:9 (estándar para YouTube y edición).
  - Vertical 9:16 (optimizado para TikTok, Shorts y Reels con fondo desenfocado).
  - Montaje unificado (Supercut que une todas las bajas en un único archivo).
- **Panel de configuración**: Ajuste de tiempos antes/después de la baja, selección de carpeta de destino por defecto y conmutador entre aceleración GPU (NVIDIA CUDA / NVENC) o procesamiento por CPU.

### Instrucciones de uso

#### Opción 1: Versión Portable (.EXE para Windows)
1. Descarga el archivo Clips KillFeed Wardogs (Portable).zip desde la sección de **[Releases](../../releases/latest)**.
2. Descomprime el contenido en una carpeta local.
3. Ejecuta Clips KillFeed Wardogs.exe. No requiere instalación previa ni dependencias externas.

#### Opción 2: Ejecución desde código fuente (con uv)
Este proyecto utiliza uv como gestor de entorno y dependencias.

`ash
git clone https://github.com/Icayon/ClipsKillFeedWardogs.git
cd ClipsKillFeedWardogs
uv run AutoClip_AI.py
`

### Autor
Desarrollado y mantenido por **ICayon**:
- Twitch: [twitch.tv/icayon](https://www.twitch.tv/icayon)
- Twitter / X: [@ICayonh](https://x.com/ICayonh)

### Licencia
Este proyecto está bajo la Licencia MIT. Se autoriza el uso, modificación y distribución del software con la **condición obligatoria de mantener siempre visible la atribución y mención expresa a ICayon**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## English

### Overview
**Clips KillFeed Wardogs** is a desktop application designed for Wardogs players and content creators. It automates highlight detection from full-length match recordings (OBS / ShadowPlay), extracting individual kill clips without manual timeline scrubbing.

### Key Features
- **Local OCR Detection**: High-speed on-device text recognition on the Killfeed region to track player-specific eliminations.
- **Distance Tracking**: Automatically parses engagement distances (e.g., [45m]).
- **Audio Peak Analysis**: Evaluates microphone audio tracks to flag high-energy moments and voice peaks.
- **Lossless Quality Retention**: Renders clips maintaining the source recording's native resolution, framerate, and bitrate.
- **Multi-Format Export**:
  - 16:9 Widescreen (standard format).
  - 9:16 Vertical (formatted for TikTok, Shorts, and Reels with cinematic background blur).
  - Supercut Montage (merges all detected kills into a single sequential video).
- **Settings Panel**: Custom lead-in/lead-out durations, default output directory selection, and hardware acceleration toggle (NVIDIA CUDA / NVENC or CPU fallback).

### Getting Started

#### Option 1: Standalone Portable Binary (Windows)
1. Download Clips KillFeed Wardogs (Portable).zip from **[Releases](../../releases/latest)**.
2. Extract the archive to any directory.
3. Launch Clips KillFeed Wardogs.exe. No external dependencies or installation required.

#### Option 2: Run from Source (via uv)
`ash
git clone https://github.com/Icayon/ClipsKillFeedWardogs.git
cd ClipsKillFeedWardogs
uv run AutoClip_AI.py
`

### Author
Created and maintained by **ICayon**:
- Twitch: [twitch.tv/icayon](https://www.twitch.tv/icayon)
- Twitter / X: [@ICayonh](https://x.com/ICayonh)

### License
This project is licensed under the MIT License. You are free to use, modify, and distribute this software provided that **proper attribution to ICayon is preserved in all copies or substantial portions of the Software**. See [LICENSE](LICENSE) for details.
