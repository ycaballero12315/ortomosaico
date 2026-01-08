import os
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

class OrthomosaicGenerator:
    def __init__(self):
        self.odm_image = "opendronemap/odm"
    
    def generar(self, carpeta_imagenes: str, max_imagenes: int = 1000, calidad: str = "low"):
        images_path = Path(carpeta_imagenes)
        
        if not images_path.exists():
            raise FileNotFoundError(f"Carpeta no encontrada: {carpeta_imagenes}")
        
        if images_path.name != "images":
            print(f"La carpeta debe llamarse 'images'")
            parent = images_path.parent
            images_folder = parent / "images"
            
            if not images_folder.exists():
                print(f"No se encontró carpeta 'images' en {parent}")
                return False
            
            images_path = images_folder

        extensiones = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']
        all_images = []
        for ext in extensiones:
            all_images.extend(images_path.glob(ext))
        
        total_imgs = len(all_images)
        imgs_a_usar = min(total_imgs, max_imagenes)
        
        print(f"\nImágenes encontradas: {total_imgs}")
        print(f"Imágenes a procesar: {imgs_a_usar}")
        
        proyecto_path = images_path.parent
        proyecto_nombre = proyecto_path.name
        datasets_path = proyecto_path.parent
        
        # Preparar carpeta ortomosaic
        ortomosaic_nombre = self._preparar_nombre_output(proyecto_path)
        if ortomosaic_nombre is None:
            print("Operación cancelada")
            return False
        
        print(f"\nEstructura del proyecto:")
        print(f"   Datasets: {datasets_path}")
        print(f"   Proyecto: {proyecto_nombre}")
        print(f"   Imágenes: {images_path}")
        print(f"   Output: {ortomosaic_nombre}")
        
        quality_map = {
            "lowest": "20",
            "low": "10",
            "medium": "5",
            "high": "2",
            "ultra": "1"
        }
        
        resolution = quality_map.get(calidad, "10")
        
        # Comando Docker - procesa directo en carpeta ortomosaic
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{datasets_path}:/datasets",
            self.odm_image,
            "--project-path", "/datasets",
            f"{proyecto_nombre}/{ortomosaic_nombre}",  # Ruta relativa dentro del proyecto
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
        
        process = subprocess.Popen(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            if any(kw in line.lower() for kw in [
                'running', 'completed', 'processing', 'orthophoto',
                'error', 'writing', 'progress'
            ]):
                print(f"   {line.rstrip()}")
        
        process.wait()
        elapsed = datetime.now() - start
        
        carpeta_output = proyecto_path / ortomosaic_nombre
        ortho_path = carpeta_output / "odm_orthophoto" / "odm_orthophoto.tif"
        
        if ortho_path.exists():
            print(f"\n¡ORTOMOSAICO GENERADO!")
            print("="*60)
            print(f"Tiempo: {elapsed}")
            self._mostrar_resultados(carpeta_output)
            return True
        else:
            print(f"\nEl ortomosaico no se generó")
            print(f"Revisa logs en: {carpeta_output / 'odm_report'}")
            return False
    
    def _preparar_nombre_output(self, proyecto_path: Path) -> str:
        """Determina nombre de carpeta output (ortomosaic o con timestamp)"""
        ortomosaic_base = proyecto_path / "ortomosaic"
        
        if not ortomosaic_base.exists():
            ortomosaic_base.mkdir(parents=True)
            print(f"\nCreada carpeta: ortomosaic")
            return "ortomosaic"
        
        contenido = list(ortomosaic_base.iterdir())
        if len(contenido) == 0:
            print(f"\nUsando carpeta existente: ortomosaic")
            return "ortomosaic"
        
        print(f"\nYa existe ortomosaic con {len(contenido)} archivos")
        print("Opciones:")
        print("  1. Sobrescribir")
        print("  2. Crear nueva con timestamp")
        print("  3. Cancelar")
        
        opcion = input("\nOpcion [2]: ").strip() or "2"
        
        if opcion == "1":
            confirm = input("Confirmar eliminación? [s/n]: ").strip().lower()
            if confirm == 's':
                shutil.rmtree(ortomosaic_base)
                ortomosaic_base.mkdir()
                return "ortomosaic"
            return None
        elif opcion == "2":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"ortomosaic_{timestamp}"
        else:
            return None
    
    def _estimar_tiempo(self, num_imgs: int, calidad: str) -> str:
        tiempo_base = {"lowest": 0.5, "low": 1, "medium": 2, "high": 4, "ultra": 8}
        minutos = num_imgs * tiempo_base.get(calidad, 1)
        return f"{int(minutos)} minutos" if minutos < 60 else f"{minutos/60:.1f} horas"
    
    def _mostrar_resultados(self, carpeta_output: Path):
        print(f"\nARCHIVOS GENERADOS:")
        print("-"*60)
        
        ortho = carpeta_output / "odm_orthophoto" / "odm_orthophoto.tif"
        if ortho.exists():
            print(f"\nORTOMOSAICO: {ortho}")
            print(f"  {ortho.stat().st_size / (1024 * 1024):.1f} MB")
        
        dsm = carpeta_output / "odm_dem" / "dsm.tif"
        if dsm.exists():
            print(f"\nMODELO ELEVACIÓN: {dsm}")
            print(f"  {dsm.stat().st_size / (1024 * 1024):.1f} MB")
        
        laz = carpeta_output / "odm_georeferencing" / "odm_georeferenced_model.laz"
        if laz.exists():
            print(f"\nNUBE PUNTOS: {laz}")
            print(f"  {laz.stat().st_size / (1024 * 1024):.1f} MB")
        
        print("\n" + "="*60)
        print(f"Carpeta: {carpeta_output}")
        print("="*60)