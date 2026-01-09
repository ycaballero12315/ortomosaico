import os
import subprocess
from pathlib import Path
from datetime import datetime

class OrthomosaicGenerator:
    def __init__(self):
        self.odm_image = "opendronemap/odm"
    
    def generar(self, carpeta_imagenes: str, max_imagenes: int = 1000, calidad: str = "low"):
        images_path = Path(carpeta_imagenes)
        
        if not images_path.exists():
            raise FileNotFoundError(f"Carpeta no encontrada: {carpeta_imagenes}")
        
        if images_path.name != "images":
            print(f"La carpeta debe llamarse 'images'")
            print(f"Carpeta actual: {images_path.name}")
            
            parent = images_path.parent
            images_folder = parent / "images"
            
            if not images_folder.exists():
                print(f"No se encontro carpeta 'images' en {parent}")
                return False
            
            images_path = images_folder

        extensiones = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']
        all_images = []
        for ext in extensiones:
            all_images.extend(images_path.glob(ext))
        
        total_imgs = len(all_images)
        imgs_a_usar = min(total_imgs, max_imagenes)
        
        print(f"\nImagenes encontradas: {total_imgs}")
        print(f"Imagenes a procesar: {imgs_a_usar}")
        
        proyecto_path = images_path.parent
        proyecto_nombre = proyecto_path.name
        datasets_path = proyecto_path.parent
        
        print(f"\nEstructura del proyecto:")
        print(f"   Datasets: {datasets_path}")
        print(f"   Proyecto: {proyecto_nombre}")
        print(f"   Imagenes: {images_path}")
        
        quality_map = {
            "lowest": "20",
            "low": "10",
            "medium": "5",
            "high": "2",
            "ultra": "1"
        }
        
        resolution = quality_map.get(calidad, "10")
        
        # Comando Docker, esta logica la cambiamos cuando tenga los binarios descargados en las PC strong
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{datasets_path}:/datasets",
            self.odm_image,
            "--project-path", "/datasets",
            proyecto_nombre,
            "--orthophoto-resolution", resolution,
            "--dem-resolution", resolution,
            "--dsm",
            "--dtm",
            "--feature-quality", calidad,
            "--pc-quality", calidad,
            "--skip-3dmodel",
            "--fast-orthophoto",
            "--orthophoto-no-tiled",
            "--ignore-gsd",
            "--min-num-features", "4000",
            "--matcher-neighbors", "8",
            "--max-concurrency", "2",
        ]
        
        print(f"\nINICIANDO PROCESAMIENTO")
        print("="*60)
        print(f"Tiempo estimado: {self._estimar_tiempo(imgs_a_usar, calidad)}")
        print("="*60)
        
        start = datetime.now()
        
        # Aca se ejecuta el proceso
        process = subprocess.Popen(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Solo para desarrollo: mostrar el proceso en consola
        for line in process.stdout:
            if any(kw in line.lower() for kw in [
                'running', 'completed', 'processing', 'orthophoto',
                'error', 'writing', 'progress'
            ]):
                print(f"   {line.rstrip()}")
        
        process.wait()
        elapsed = datetime.now() - start
        
        # Validamos resultados con su generacion fisica
        ortho_path = proyecto_path / "odm_orthophoto" / "odm_orthophoto.tif"
        
        # Solo en desarrollo: mostrar el proceso en consola
        if ortho_path.exists():
            print(f"\n ¡ORTOMOSAICO GENERADO!")
            print("="*60)
            print(f"Tiempo: {elapsed}")
            self._mostrar_resultados(proyecto_path)
            return True
        else:
            print(f"\nEl ortomosaico no se generó")
            print(f"   Revisa logs en: {proyecto_path / 'odm_report'}")
            print(f"\n📁 Carpetas creadas:")
            for item in proyecto_path.iterdir():
                if item.is_dir() and item.name.startswith("odm_"):
                    print(f"   - {item.name}")
            
            return False
    
    def _estimar_tiempo(self, num_imgs: int, calidad: str) -> str:
        """Estima tiempo de procesamiento"""
        # Tiempo base por imagen en minutos
        tiempo_base = {
            "lowest": 0.5,
            "low": 1,
            "medium": 2,
            "high": 4,
            "ultra": 8
        }
        
        minutos = num_imgs * tiempo_base.get(calidad, 1)
        
        if minutos < 60:
            return f"{int(minutos)} minutos"
        else:
            horas = minutos / 60
            return f"{horas:.1f} horas"
        
    # Solo para comprobar, en desarrollo
    def _mostrar_resultados(self, proyecto_path: Path):
        print(f"\nARCHIVOS GENERADOS:")
        print("-"*60)
        
        # Proceso de ortofoto
        ortho = proyecto_path / "odm_orthophoto" / "odm_orthophoto.tif"
        if ortho.exists():
            size_mb = ortho.stat().st_size / (1024 * 1024)
            print(f"\nORTOMOSAICO (GeoTIFF):")
            print(f"  {ortho}")
            print(f"  {size_mb:.1f} MB")
        
        dsm = proyecto_path / "odm_dem" / "dsm.tif"
        if dsm.exists():
            size_mb = dsm.stat().st_size / (1024 * 1024)
            print(f"\n MODELO ELEVACIÓN:")
            print(f" {dsm}")
            print(f" {size_mb:.1f} MB")
        
        # La famosa nube de puntos
        laz = proyecto_path / "odm_georeferencing" / "odm_georeferenced_model.laz"
        if laz.exists():
            size_mb = laz.stat().st_size / (1024 * 1024)
            print(f"\n NUBE DE PUNTOS:")
            print(f" {laz}")
            print(f" {size_mb:.1f} MB")
        
        print("\n" + "="*60)
        print(f"Todos los archivos en: {proyecto_path}")
        print("="*60)