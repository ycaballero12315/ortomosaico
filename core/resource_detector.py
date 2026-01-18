import subprocess
import psutil
import platform
from dataclasses import dataclass
from typing import Optional

@dataclass
class SystemResources:
    has_gpu: bool
    gpu_name: Optional[str]
    gpu_memory_gb: Optional[float]
    cpu_cores_physical: int
    cpu_cores_logical: int
    total_ram_gb: float
    available_ram_gb: float
    platform: str
    
    def __str__(self) -> str:
        gpu_info = f"{self.gpu_name} ({self.gpu_memory_gb:.1f} GB)" if self.has_gpu else "No detectada"
        return f"""
              Sistema Operativo: {self.platform}
              CPU Cores:         {self.cpu_cores_physical} fisicos, {self.cpu_cores_logical} logicos
              RAM Total:         {self.total_ram_gb:.1f} GB
              RAM Disponible:    {self.available_ram_gb:.1f} GB
              GPU:               {gpu_info}
            """

class ResourceDetector:

    @staticmethod
    def detect() -> SystemResources:
        return SystemResources(
            has_gpu=ResourceDetector._check_gpu(),
            gpu_name=ResourceDetector._get_gpu_name(),
            gpu_memory_gb=ResourceDetector._get_gpu_memory(),
            cpu_cores_physical=psutil.cpu_count(logical=False) or 4,
            cpu_cores_logical=psutil.cpu_count(logical=True) or 8,
            total_ram_gb=psutil.virtual_memory().total / (1024**3),
            available_ram_gb=psutil.virtual_memory().available / (1024**3),
            platform=platform.system()
        )
    
    @staticmethod
    def _check_gpu() -> bool:
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=3
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def _get_gpu_name() -> Optional[str]:
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None
    
    @staticmethod
    def _get_gpu_memory() -> Optional[float]:
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                memory_mb = float(result.stdout.strip().split('\n')[0])
                return memory_mb / 1024
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass
        return None