# 🛩️ Sistema de Generación de Ortomosaicos

Sistema profesional para generar ortomosaicos con OpenDroneMap, optimizado con arquitectura limpia y detección automática de recursos.

## ✨ Características Principales

- ✅ **Sin copia de imágenes**: Monta directamente las imágenes (read-only)
- ✅ **Detección automática de GPU**: NVIDIA CUDA detectada y configurada
- ✅ **Outputs secuenciales**: `outputs/odm1/`, `odm2/`, `odm3/`...
- ✅ **Solo ortomosaico TIF**: Sin productos innecesarios (3D, DSM, DTM)
- ✅ **Limpieza automática**: Elimina archivos intermedios
- ✅ **Arquitectura limpia**: Core, Infrastructure, CLI separados
- ✅ **Logging profesional**: Archivos timestamped + consola

---

## 📁 Estructura del Proyecto

```
orthomosaic-system/
│
├── core/                          # 🧠 Motor (lógica pura)
│   ├── __init__.py
│   ├── resource_detector.py      # Detecta GPU, CPU, RAM
│   ├── config_builder.py         # Construye config ODM
│   └── odm_engine.py             # Ejecuta ODM
│
├── infrastructure/                # 🔧 Infraestructura
│   ├── __init__.py
│   ├── output_manager.py         # Gestión odm1, odm2...
│   └── logger.py                 # Sistema de logs
│
├── cli/                          # 💬 Interfaz usuario
│   ├── __init__.py
│   └── main.py                   # CLI principal
│
├── outputs/                      # 📦 Salidas (auto-generado)
│   ├── odm1/
│   │   ├── odm_orthophoto/
│   │   │   └── odm_orthophoto.tif  ← RESULTADO
│   │   └── metadata.json
│   ├── odm2/
│   └── odm3/
│
├── logs/                         # 📝 Logs (auto-generado)
│   └── orthomosaic_TIMESTAMP.log
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Instalación

### 1. Clonar repositorio
```bash
git clone <tu-repo>
cd orthomosaic-system
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar Docker
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/)
- **Linux**: `sudo apt-get install docker.io`

### 4. Verificar GPU (opcional)
```bash
nvidia-smi
```

---

## 💻 Uso

### Modo Interactivo (Recomendado)

```bash
python cli/main.py
```

El sistema te guiará:

```
===========================================================
 GENERADOR DE ORTOMOSAICOS - ODM
===========================================================

Sistema Operativo: Windows
CPU Cores:         8 físicos, 16 lógicos
RAM Total:         32.0 GB
RAM Disponible:    18.5 GB
GPU:               ✓ NVIDIA RTX 3080 (10.0 GB)

✓ Docker detectado

[1/4] UBICACIÓN DE IMÁGENES
-----------------------------------------------------------
Ruta a carpeta con imágenes: D:\Personal\project\ortophotos\odm_data_aukerman\images
✓ Encontradas 243 imágenes

[2/4] CALIDAD DE PROCESAMIENTO
===========================================================
  1. lowest  - Mínima - Rápido, baja calidad
  2. low     - Baja - Pruebas rápidas
  3. medium  - Media - Recomendado (balance)
  4. high    - Alta - Mayor calidad, más lento
  5. ultra   - Ultra - Máxima calidad, muy lento

Calidad [3]: 3

[3/4] CANTIDAD DE IMÁGENES
-----------------------------------------------------------
Máximo de imágenes [todas=243]: 

[4/4] CONFIRMACIÓN
===========================================================
  Directorio:        D:\Personal\project\ortophotos\odm_data_aukerman\images
  Total imágenes:    243
  A procesar:        243
  Calidad:           medium
  Concurrencia:      8 threads
  GPU:               ✓ Habilitada
  Productos:         Solo ortomosaico TIF
  Copia imágenes:    ✗ No (montaje directo)
===========================================================

¿Continuar? [s/n]: s

===========================================================
INICIANDO PROCESAMIENTO
===========================================================

Directorio de salida: outputs/odm1
```

### Modo Programático (API)

```python
from core.resource_detector import ResourceDetector
from core.config_builder import ConfigBuilder
from core.odm_engine import ODMEngine
from infrastructure.output_manager import OutputManager
from infrastructure.logger import LoggerFactory
from pathlib import Path

# Setup
logger = LoggerFactory.create("mi_ortomosaico")
output_manager = OutputManager()

# Detectar recursos
resources = ResourceDetector.detect()
print(resources)

# Configurar
config = ConfigBuilder.build(resources, quality="high")

# Crear directorio de salida
output_dir = output_manager.create_next_output_dir()

# Ejecutar
engine = ODMEngine(logger)
result = engine.execute(
    images_path=Path("D:/ruta/a/images"),
    output_path=output_dir,
    config=config,
    max_images=100  # Opcional
)

if result.success:
    print(f"✓ Ortomosaico: {result.orthophoto_path}")
    
    # Limpiar
    output_manager.cleanup_intermediate_files(output_dir)
    
    # Guardar metadata
    output_manager.save_metadata(output_dir, {
        "calidad": "high",
        "imagenes": 100
    })
else:
    print(f"✗ Error: {result.error_message}")
```

---

## ⚙️ Configuración

### Calidades Disponibles

| Calidad | Resolución | Feature Quality | Velocidad | Uso Típico |
|---------|------------|-----------------|-----------|------------|
| `lowest` | 10 cm/px | lowest | ⚡⚡⚡⚡⚡ | Tests rápidos |
| `low` | 5 cm/px | low | ⚡⚡⚡⚡ | Previews |
| `medium` | 3 cm/px | medium | ⚡⚡⚡ | **Producción** |
| `high` | 2 cm/px | high | ⚡⚡ | Alta precisión |
| `ultra` | 1 cm/px | ultra | ⚡ | Máxima calidad |

### Detección Automática de Recursos

El sistema ajusta automáticamente:

| Hardware | Sin GPU | Con GPU RTX 3080 |
|----------|---------|------------------|
| **Threads** | 6 (8-2) | 8 |
| **GPU Docker** | - | `--gpus all` |
| **RAM < 8GB** | max 4 threads | max 4 threads |
| **RAM 8-16GB** | max 8 threads | max 8 threads |
| **RAM > 16GB** | sin límite | sin límite |

---

## 📊 Rendimiento

### Tiempos Estimados (243 imágenes, medium quality)

| Configuración | Tiempo | Mejora vs Original |
|---------------|--------|-------------------|
| CPU only (sin optimizaciones) | ~6 horas | - |
| CPU only (optimizado) | ~4 horas | 33% ⚡ |
| GPU RTX 3080 (optimizado) | ~1.5 horas | 75% ⚡⚡⚡ |

### Optimizaciones Aplicadas

✅ `--fast-orthophoto` - Algoritmo rápido  
✅ `--use-hybrid-bundle-adjustment` - Bundle adjustment optimizado  
✅ `--skip-3dmodel` - Sin modelo 3D  
✅ `--skip-report` - Sin reporte HTML  
✅ `-v [images]:ro` - Montaje read-only (sin copia)  
✅ Limpieza automática de intermedios  

---

## 🗂️ Estructura de Outputs

```
outputs/
├── odm1/
│   ├── odm_orthophoto/
│   │   └── odm_orthophoto.tif     ← Ortomosaico final
│   └── metadata.json               ← Info del procesamiento
├── odm2/
└── odm3/
```

### Ejemplo de metadata.json

```json
{
  "images_path": "D:\\Personal\\project\\ortophotos\\odm_data_aukerman\\images",
  "total_images": 243,
  "processed_images": 243,
  "quality": "medium",
  "config": {
    "max_concurrency": 8,
    "use_gpu": true,
    "orthophoto_resolution": 3.0
  },
  "created_at": "2026-01-17T15:30:22.123456",
  "output_dir": "outputs/odm1"
}
```

---

## 🐛 Troubleshooting

### Error: "Docker no encontrado"

**Solución:**
```bash
# Verificar
docker --version

# Windows - Instalar
winget install Docker.DockerDesktop

# Linux - Instalar
sudo apt-get update
sudo apt-get install docker.io
```

### Error: "No se generó ortofoto"

**Causas comunes:**
1. Overlap insuficiente entre imágenes (<60%)
2. Imágenes sin EXIF/GPS
3. Calidad muy alta + pocas imágenes

**Solución:**
- Revisar logs: `logs/orthomosaic_*.log`
- Probar con `quality="low"` primero
- Verificar EXIF: `exiftool imagen.jpg`

### Performance muy lento

**Optimizaciones:**
1. Reducir calidad: `low` para tests
2. Limitar imágenes: `max_images=50`
3. Verificar GPU: `nvidia-smi`
4. Cerrar apps que consuman RAM

---

## 📈 Comparación vs Versión Original

| Aspecto | Antes ❌ | Ahora ✅ |
|---------|---------|---------|
| **Copia imágenes** | Duplica 10GB+ | Montaje directo (0 copia) |
| **Config GPU** | Manual/hardcoded | Auto-detectada |
| **Outputs** | Sobrescribe | Secuencial (odm1, odm2...) |
| **Productos** | Todos (3D, DSM, DTM) | Solo TIF |
| **Arquitectura** | Monolítica | Clean Architecture |
| **Logging** | print() | Logger profesional |
| **Limpieza** | Manual | Automática |
| **Metadata** | Ninguna | JSON completo |

---

## 🧪 Testing

```bash
# Instalar pytest
pip install pytest

# Ejecutar tests
pytest tests/

# Con coverage
pytest --cov=core --cov=infrastructure tests/
```

---

## 📚 Arquitectura

### Principios SOLID Aplicados

1. **Single Responsibility**: Cada módulo tiene una responsabilidad
2. **Dependency Inversion**: Core no depende de Infrastructure
3. **Separation of Concerns**: Core vs Infrastructure vs CLI

```
┌─────────────┐
│     CLI     │  ← Interfaz de usuario
└──────┬──────┘
       │
       ↓
┌──────────────────────────┐
│    Infrastructure        │  ← Archivos, logs, sistema
│  - OutputManager         │
│  - LoggerFactory         │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│         Core             │  ← Lógica pura
│  - ResourceDetector      │
│  - ConfigBuilder         │
│  - ODMEngine             │
└──────────────────────────┘
```

---

## 🛣️ Roadmap

- [ ] Multi-GPU support
- [ ] Web UI (FastAPI + React)
- [ ] Procesamiento batch automático
- [ ] Compresión TIF (LZW, JPEG)
- [ ] Cloud storage (S3, GCS)
- [ ] Estimación de tiempo
- [ ] Progress bar interactivo

---

## 📝 Changelog

### v2.0.0 (2026-01-17) - Arquitectura Limpia
- ✅ Eliminada copia de imágenes (montaje directo)
- ✅ Arquitectura modular (Core/Infrastructure/CLI)
- ✅ Detección automática de recursos
- ✅ Outputs secuenciales (odm1, odm2...)
- ✅ Solo genera ortomosaico TIF
- ✅ Logging profesional
- ✅ Limpieza automática

### v1.0.0 - Versión Original
- Generación básica de ortomosaicos
- Configuración manual

---

## 📞 Soporte

**Logs**: `logs/orthomosaic_*.log`  
**Metadata**: `outputs/odmN/metadata.json`  
**Docs ODM**: https://docs.opendronemap.org/

---

## 📄 Licencia

MIT License - Úsalo libremente

---

**Versión**: 2.0.0  
**Autor**: Tu nombre  
**Última actualización**: 2026-01-17