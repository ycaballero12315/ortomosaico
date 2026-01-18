import sys
from pathlib import Path
from typing import Optional

from core.resource_detector import ResourceDetector
from core.config_builder import ConfigBuilder
from core.odm_engine import ODMEngine

from infrastructure.output_manager import OutputManager
from infrastructure.logger import LoggerFactory

class OrthomosaicCLI:
  
    def __init__(self):
        self.logger = LoggerFactory.create("orthomosaic")
        self.output_manager = OutputManager()
    
    def run(self):
        
        try:
            self._print_header()

            resources = ResourceDetector.detect()
            self.logger.info(resources)
            print(resources) #Mostrar solo en desarrollo
            
            if not ODMEngine.validate_docker():
                self.logger.warning("ERROR: Docker no esta instalado o no esta corriendo")
                print("ERROR: Docker no esta instalado o no esta corriendo") #Solo en desarrollo
                return
            
            self.logger.info("Docker detectado\n")
            print("Docker detectado\n") #Solo en etapa de desarrollo

            images_dir = self._get_images_directory()
            if images_dir is None:
                return
            
            image_count = self._count_images(images_dir)
            self.logger.info(f"Encontradas {image_count} imagenes\n")
            print(f"Encontradas {image_count} imagenes\n")
            
            quality = self._get_quality_choice()
            
            max_images = self._get_max_images(image_count)
            
            config = ConfigBuilder.build(resources, quality)
            
            if not self._confirm_execution(images_dir, image_count, max_images, quality, config):
                self.logger.info("\nProceso cancelado por el usuario")
                print("\nProceso cancelado por el usuario") #Solo en etapa de desarrollo
                return
            
            self._execute_processing(images_dir, config, max_images, image_count)
            
        except KeyboardInterrupt as e:
            self.logger.exception(f"\n\n Proceso interrumpido por el usuario {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.exception(f"Error inesperado: {e}")
            sys.exit(1)
    
    def _print_header(self):
        print("="*60)
        print(" GENERADOR DE ORTOMOSAICOS - ODM")
        print("="*60)
        print("Solo ortomosaico TIF")
        print("="*60)
    
    def _get_images_directory(self) -> Optional[Path]:
        print("\n[1/4] UBICACION DE IMAGENES")
        print("-"*60)
        
        while True:
            try:
                path_input = input("Ruta a carpeta con imagenes: ").strip()
                
                if not path_input:
                    print("Debe ingresar una ruta")
                    continue

                path_input = path_input.strip('"').strip("'")
                path = Path(path_input)

                if path.name != "images":
                    images_subdir = path / "images"
                    if images_subdir.exists() and images_subdir.is_dir():
                        print(f"Usando subcarpeta: {images_subdir}")
                        path = images_subdir
                    else:
                        print(f"No se encontro carpeta 'images' en {path}")
                        print("ODM requiere que las imagenes esten en una carpeta llamada 'images'")
                        retry = input("\n¿Intentar con otra ruta? [s/n]: ").strip().lower()
                        if retry not in {'s', 'si', 'sí', 'y', 'yes'}:
                            return None
                        continue

                if not path.exists():
                    print(f"El directorio no existe: {path}")
                    retry = input("\n¿Intentar con otra ruta? [s/n]: ").strip().lower()
                    if retry not in {'s', 'si', 'sí', 'y', 'yes'}:
                        return None
                    continue
                
                return path
                
            except Exception as e:
                print(f"Error: {e}")
                return None
    
    def _count_images(self, path: Path) -> int:
        extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
        return len([
            f for f in path.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ])
    
    def _get_quality_choice(self) -> str:
        print("\n[2/4] CALIDAD DE PROCESAMIENTO")
        print("="*60)
        
        options = {
            "1": ("lowest", "Minima - Rapido, baja calidad"),
            "2": ("low", "Baja - Pruebas rapidas"),
            "3": ("medium", "Media - Recomendado (balance)"),
            "4": ("high", "Alta - Mayor calidad, mas lento"),
            "5": ("ultra", "Ultra - Maxima calidad, muy lento")
        }
        
        for key, (name, desc) in options.items():
            print(f"  {key}. {name:8s} - {desc}")
        
        while True:
            choice = input("\nCalidad [3]: ").strip() or "3"
            if choice in options:
                quality, _ = options[choice]
                return quality
            print("Opcion invalida. Elija entre 1-5.")
    
    def _get_max_images(self, total: int) -> Optional[int]:
        print("\n[3/4] CANTIDAD DE IMAGENES")
        print("-"*60)
        
        while True:
            try:
                max_input = input(f"Maximo de imagenes [todas={total}]: ").strip()
                
                if not max_input:
                    return None
                
                max_imgs = int(max_input)
                
                if max_imgs < 1:
                    print("Debe procesar al menos 1 imagen")
                    continue
                
                if max_imgs > total:
                    print(f"Solo hay {total} imagenes disponibles")
                    continue
                
                return max_imgs
                
            except ValueError:
                print("Ingrese un numero valido")
    
    def _confirm_execution(
        self,
        images_dir: Path,
        total_images: int,
        max_images: Optional[int],
        quality: str,
        config
    ) -> bool:
        print("\n[4/4] CONFIRMACION")
        print("="*60)
        print(f"  Directorio:        {images_dir}")
        print(f"  Total imagenes:    {total_images}")
        print(f"  A procesar:        {max_images or total_images}")
        print(f"  Calidad:           {quality}")
        print(f"  Concurrencia:      {config.max_concurrency} threads")
        print(f"  GPU:               {'Habilitada' if config.use_gpu else 'Deshabilitada'}")
        print(f"  Productos:         Solo ortomosaico TIF")
        print(f"  Copia imágenes:    No (montaje directo)")
        print("="*60)
        
        while True:
            response = input("\n¿Continuar? [s/n]: ").strip().lower()
            if response in {'s', 'si', 'sí', 'y', 'yes'}:
                return True
            elif response in {'n', 'no'}:
                return False
            print("Responda 's' para si o 'n' para no")
    
    def _execute_processing(
        self,
        images_dir: Path,
        config,
        max_images: int | None,
        total_images: int
    ):
        print("\n" + "="*60)
        print("INICIANDO PROCESAMIENTO")
        print("="*60)
        
        output_dir = self.output_manager.create_next_output_dir()
        print(f"\nDirectorio de salida: {output_dir}")
        
        # Crear engine
        engine = ODMEngine(self.logger)
        
        result = engine.execute(
            images_path=images_dir,
            output_path=output_dir,
            config=config,
            max_images=max_images
        )
        if result.success:
            self.output_manager.save_metadata(output_dir, {
                "images_path": str(images_dir),
                "total_images": total_images,
                "processed_images": max_images or total_images,
                "quality": config.feature_quality,
                "config": {
                    "max_concurrency": config.max_concurrency,
                    "use_gpu": config.use_gpu,
                    "orthophoto_resolution": config.orthophoto_resolution
                }
            })
        
        if result.success:
            print("\n" + "="*60)
            print("LIMPIANDO ARCHIVOS INTERMEDIOS...")
            print("="*60)
            self.output_manager.cleanup_intermediate_files(output_dir)
            
            disk_usage = self.output_manager.get_disk_usage(output_dir)
            
            print("\n" + "="*60)
            print("PROCESAMIENTO EXITOSO")
            print("="*60)
            print(f"\nOrtomosaico: {result.orthophoto_path}")
            print(f"Tamanno:      {disk_usage['orthophoto_mb']:.1f} MB")
            print(f"Directorio:  {output_dir}")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("PROCESAMIENTO FALLIDO")
            print("="*60)
            print(f"\nError: {result.error_message}")
            print(f"\nRevise los logs en: logs/")
            print("="*60)


def main():
    cli = OrthomosaicCLI()
    cli.run()
