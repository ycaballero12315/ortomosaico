from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

class Settings:
    _instance: Optional['Settings'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Settings._initialized:
            return
        
        self.PROJECT_ROOT = Path(__file__).parent.parent.resolve()
        
        # Cargar variables de entorno desde .env
        env_path = self.PROJECT_ROOT / ".env"
        load_dotenv(env_path)
        
        self.OUTPUTS_DIR = Path(os.getenv("OUTPUTS_DIR", str(self.PROJECT_ROOT / "outputs")))
        self.LOGS_DIR = Path(os.getenv("LOGS_DIR", str(self.PROJECT_ROOT / "logs")))
        self.CONFIG_DIR = Path(os.getenv("CONFIG_DIR", str(self.PROJECT_ROOT / "config")))
        self.DATA_DIR = Path(os.getenv("DATA_DIR", str(self.PROJECT_ROOT / "data")))
        
        self._ensure_directories()
        
        # Configuración de ODM (desde .env)
        self.ODM_PROJECT_NAME = os.getenv("ODM_PROJECT_NAME", "odm_project")
        self.ODM_DOCKER_IMAGE = os.getenv("ODM_DOCKER_IMAGE", "opendronemap/odm")
        self.ODM_SHARED_MEMORY = os.getenv("ODM_SHARED_MEMORY", "2g")
        
        self.SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
        self.METADATA_FILENAME = os.getenv("METADATA_FILENAME", "metadata.json")
        
        self.MIN_CONCURRENCY = int(os.getenv("MIN_CONCURRENCY", "2"))
        self.PI_FACTOR = float(os.getenv("PI_FACTOR", "3.14"))
        
        self.KEEP_LOGS_AFTER_CLEANUP = os.getenv("KEEP_LOGS_AFTER_CLEANUP", "true").lower() == "true"
        self.DIRS_TO_CLEANUP = [
            "odm_meshing",
            "odm_texturing",
            "odm_dem",
            "odm_georeferencing",
            "opensfm",
            "submodels",
            "entwine_pointcloud"
        ]
        
        self.ENABLE_GPU = os.getenv("ENABLE_GPU", "auto")
        
        self.DEFAULT_QUALITY = os.getenv("DEFAULT_QUALITY", "medium")
        
        Settings._initialized = True
    
    def _ensure_directories(self):
        for dir_path in [self.OUTPUTS_DIR, self.LOGS_DIR, self.CONFIG_DIR, self.DATA_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_output_path(self, project_number: int) -> Path:
        return self.OUTPUTS_DIR / f"odm{project_number}"
    
    def get_log_path(self, log_name: str, timestamp: str) -> Path:
        return self.LOGS_DIR / f"{log_name}_{timestamp}.log"
    
    def get_orthophoto_dir(self, output_dir: Path) -> Path:
        return output_dir / "odm_orthophoto"
    
    def reload(self):
        Settings._initialized = False
        self.__init__()
    
    def __repr__(self) -> str:
        return (
            f"Settings(\n"
            f"  PROJECT_ROOT={self.PROJECT_ROOT}\n"
            f"  OUTPUTS_DIR={self.OUTPUTS_DIR}\n"
            f"  LOGS_DIR={self.LOGS_DIR}\n"
            f"  ODM_DOCKER_IMAGE={self.ODM_DOCKER_IMAGE}\n"
            f"  PI_FACTOR={self.PI_FACTOR}\n"
            f"  MIN_CONCURRENCY={self.MIN_CONCURRENCY}\n"
            f")"
        )

settings = Settings()