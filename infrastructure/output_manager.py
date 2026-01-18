import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from config.settings import settings
class OutputManager:
    
    def __init__(self, base_path: Optional[str] = None):
      
        if base_path is None:
            base_path = settings.OUTPUTS_DIR
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def create_next_output_dir(self) -> Path:
        # base_dir = Path("outputs")
        # base_dir.mkdir(exist_ok=True) 
        
        i = 1
        while (self.base_path / f"odm{i}").exists():
            i += 1
        
        new_dir = self.base_path / f"odm{i}"
        new_dir.mkdir(parents=True)
        return new_dir
    
    def get_latest_output_dir(self, prefix: str = "odm") -> Optional[Path]:
        
        existing_dirs = sorted(
            [d for d in self.base_path.iterdir() 
             if d.is_dir() and d.name.startswith(prefix)],
            key=lambda x: self._extract_number(x.name, prefix),
            reverse=True
        )
        
        return existing_dirs[0] if existing_dirs else None
    
    def list_output_dirs(self, prefix: str = "odm") -> list[Path]:
        
        return sorted(
            [d for d in self.base_path.iterdir() 
             if d.is_dir() and d.name.startswith(prefix)],
            key=lambda x: self._extract_number(x.name, prefix)
        )
    
    def cleanup_intermediate_files(self, output_dir: Path, keep_logs: bool = True):

        if not output_dir.exists():
            return
        
        if keep_logs is None:
            keep_logs = settings.KEEP_LOGS_AFTER_CLEANUP

        orthophoto_dir = settings.get_orthophoto_dir(output_dir)
    
        if not orthophoto_dir.exists():
            return

        for item in output_dir.iterdir():
            # Saltar odm_orthophoto
            if item.name == "odm_orthophoto":
                continue
        
            if keep_logs and item.name == "logs":
                continue
        
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except Exception as e:
                pass
    
    def save_metadata(self, output_dir: Path, metadata: Dict[str, Any]):
        
        metadata_file = output_dir / settings.METADATA_FILENAME
        
        metadata['created_at'] = datetime.now().isoformat()
        metadata['output_dir'] = str(output_dir)
        
        metadata_serializable = self._make_serializable(metadata)
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_serializable, f, indent=2, ensure_ascii=False)
    
    def load_metadata(self, output_dir: Path) -> Optional[Dict[str, Any]]:
        metadata_file = output_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_disk_usage(self, output_dir: Path) -> Dict[str, float]:
        
        if not output_dir.exists():
            return {"total_mb": 0}
        
        total_size = 0
        orthophoto_size = 0
        
        orthophoto_dir = settings.get_orthophoto_dir(output_dir)

        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                
                if orthophoto_dir.exists() and orthophoto_dir in file_path.parents:
                    if file_path.suffix == ".tif":
                        orthophoto_size += size
        
        return {
            "total_mb": total_size / (1024**2),
            "orthophoto_mb": orthophoto_size / (1024**2),
            "other_mb": (total_size - orthophoto_size) / (1024**2)
        }
    
    def _extract_number(self, dirname: str, prefix: str) -> int:
        try:
            return int(dirname.replace(prefix, ""))
        except ValueError:
            return 0
    
    def _make_serializable(self, obj: Any) -> Any:
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        return obj