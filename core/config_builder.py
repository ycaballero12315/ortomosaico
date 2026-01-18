from dataclasses import dataclass
from typing import Dict, Any
from core.resource_detector import SystemResources
from config.settings import settings

@dataclass
class ODMConfig:
    max_concurrency: int
    feature_quality: str
    pc_quality: str
    mesh_size: int
    orthophoto_resolution: float
    dem_resolution: float
    
    use_gpu: bool
    
    generate_dsm: bool = False
    generate_dtm: bool = False
    skip_3dmodel: bool = True
    skip_report: bool = True
    
    fast_orthophoto: bool = True
    use_hybrid_bundle_adjustment: bool = True
    
    def to_odm_params(self) -> list[str]:
        params = [
        "--max-concurrency", str(self.max_concurrency),
        "--feature-quality", self.feature_quality,
        "--pc-quality", self.pc_quality,
        "--mesh-size", str(self.mesh_size),
        "--orthophoto-resolution", str(self.orthophoto_resolution),
        "--dem-resolution", str(self.dem_resolution),
        ]

        if self.skip_3dmodel:
            params.append("--skip-3dmodel")

        if self.skip_report:
            params.append("--skip-report")

        if self.fast_orthophoto:
            params.append("--fast-orthophoto")

        if self.use_hybrid_bundle_adjustment:
            params.append("--use-hybrid-bundle-adjustment")

        # DSM y DTM - solo agregar flags si NO se generan
        if self.generate_dsm:
            params.append("--dsm")
        if self.generate_dtm:
            params.append("--dtm")

        return params
    
    def __str__(self) -> str:
        return f"""
              Configuraci0n ODM:
              Concurrencia:      {self.max_concurrency} threads
              Feature Quality:   {self.feature_quality}
              PC Quality:        {self.pc_quality}
              Resoluci0n Ortho:  {self.orthophoto_resolution} cm/px
              GPU:               {'Habilitada' if self.use_gpu else 'Deshabilitada'}
              Productos:         Solo ortomosaico TIF
              Optimizaciones:    Fast orthophoto, Hybrid bundle adjustment
            """


class ConfigBuilder:
    QUALITY_PRESETS: Dict[str, Dict[str, Any]] = {
        "lowest": {
            "feature_quality": "lowest",
            "pc_quality": "lowest",
            "mesh_size": 100000,
            "orthophoto_resolution": 10.0,
            "dem_resolution": 10.0
        },
        "low": {
            "feature_quality": "low",
            "pc_quality": "low",
            "mesh_size": 200000,
            "orthophoto_resolution": 5.0,
            "dem_resolution": 5.0
        },
        "medium": {
            "feature_quality": "medium",
            "pc_quality": "medium",
            "mesh_size": 500000,
            "orthophoto_resolution": 3.0,
            "dem_resolution": 3.0
        },
        "high": {
            "feature_quality": "high",
            "pc_quality": "high",
            "mesh_size": 1000000,
            "orthophoto_resolution": 2.0,
            "dem_resolution": 2.0
        },
        "ultra": {
            "feature_quality": "ultra",
            "pc_quality": "ultra",
            "mesh_size": 2000000,
            "orthophoto_resolution": 1.0,
            "dem_resolution": 1.0
        }
    }
    
    @staticmethod
    def build(resources: SystemResources, quality: str | None = None) -> ODMConfig:
        if quality is None:
            quality = settings.DEFAULT_QUALITY
    
        preset = ConfigBuilder.QUALITY_PRESETS.get(
            quality.lower(), 
            ConfigBuilder.QUALITY_PRESETS[settings.DEFAULT_QUALITY]
            )

        max_concurrency = ConfigBuilder._calculate_concurrency(resources)
        use_gpu = ConfigBuilder._should_use_gpu(resources)

        return ODMConfig(
            max_concurrency=max_concurrency,
            use_gpu=use_gpu,
            **preset
        )
    
    @staticmethod
    def _should_use_gpu(resources: SystemResources) -> bool:
        gpu_setting = settings.ENABLE_GPU.lower()
    
        if gpu_setting == "true":
            return True
        elif gpu_setting == "false":
            return False
        else: 
            return resources.has_gpu
        
    @staticmethod
    def _calculate_concurrency(resources: SystemResources) -> int:
        ram_based = int(resources.available_ram_gb / settings.PI_FACTOR)
    
        return max(settings.MIN_CONCURRENCY, min(resources.cpu_cores_physical, ram_based))