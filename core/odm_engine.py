import subprocess
import logging
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass


from core.config_builder import ODMConfig

@dataclass
class ProcessingResult:
    success: bool
    orthophoto_path: Optional[Path]
    error_message: Optional[str] = None
    return_code: Optional[int] = None


class ODMEngine:
    
    def __init__(self, logger: Optional[logging.Logger] = None):
      self.logger = logger or logging.getLogger(__name__)
    
    def execute(
        self,
        images_path: Path,
        output_path: Path,
        config: ODMConfig,
        max_images: Optional[int] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> ProcessingResult:
        try:
            cmd = self._build_docker_command(
                images_path, 
                output_path, 
                config, 
                max_images
            )
            
            self.logger.info("Ejecutando ODM...")
            self.logger.info("Completado")
            self.logger.debug(' '.join(cmd))
            
            # Ejecutar proceso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.logger.info(f"ODM: {line}")
                    if progress_callback:
                        progress_callback(line)
            
            process.wait()
            
            if process.returncode != 0:
                error_msg = f"ODM fallo con codigo: {process.returncode}"
                self.logger.error(error_msg)
                return ProcessingResult(
                    success=False,
                    orthophoto_path=None,
                    error_message=error_msg,
                    return_code=process.returncode
                )
            
            orthophoto_path = self._find_orthophoto(output_path)
            
            if orthophoto_path is None:
                error_msg = "No se genero archivo de ortofoto"
                self.logger.error(error_msg)
                return ProcessingResult(
                    success=False,
                    orthophoto_path=None,
                    error_message=error_msg
                )
            
            self.logger.info(f"Ortofoto generada: {orthophoto_path}")
            
            return ProcessingResult(
                success=True,
                orthophoto_path=orthophoto_path
            )
            
        except FileNotFoundError:
            error_msg = "Docker no encontrado. ¿Esta instalado?"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                orthophoto_path=None,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Error ejecutando ODM: {e}"
            self.logger.exception(error_msg)
            return ProcessingResult(
                success=False,
                orthophoto_path=None,
                error_message=error_msg
            )
    @staticmethod
    def _format_path(path: Path) -> str:
            abs_path = str(path.absolute()).replace('\\', '/')
            if len(abs_path) > 1 and abs_path[1] == ':':
                drive = abs_path[0].lower()
                return f"/{drive}{abs_path[2:]}"
            return abs_path
    

    def _build_docker_command(
        self,
        images_path: Path,
        output_path: Path,
        config: ODMConfig,
        max_images: int | None
    ) -> list[str]:
        
        project_name = "odm_project"

        host_images = ODMEngine._format_path(images_path)
        host_output = ODMEngine._format_path(output_path)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{host_images}:/datasets/{project_name}/images:ro",
            "-v", f"{host_output}:/datasets/{project_name}"
        ]

        if config.use_gpu:
            cmd.extend(["--gpus", "all"])
        
        cmd.extend(["--shm-size", "2g"])
        
        cmd.append("opendronemap/odm")
        
        cmd.extend([
            "--project-path", 
            "/datasets"
            ])
        
        cmd.extend(config.to_odm_params())
        
        if max_images:
            cmd.extend(["--max-images", str(max_images)])
        
        cmd.append(project_name)

        self.logger.info(f"Comando completo: {cmd}")
        self.logger.info(f"Ultimos 5 elementos: {cmd[-5:]}")

        return cmd
    
    def _find_orthophoto(self, output_path: Path) -> Path | None:
        target_dir = output_path / "odm_orthophoto"
        
        if not target_dir.exists():
            self.logger.warning(f"No se encontro la carpeta de ortofoto en {target_dir}")
            return None
        
        tifs = [f for f in target_dir.glob("*.tif") if "_tile_" not in f.name]
        return tifs[0] if tifs else None
    
    @staticmethod
    def validate_docker() -> bool:
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False