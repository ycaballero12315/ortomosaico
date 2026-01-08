from generar_ortomosaico import OrthomosaicGenerator
from pathlib import Path

def main():
    
    print("="*60)
    print("GENERADOR DE ORTOMOSAICOS")
    print("="*60)
    
    generador = OrthomosaicGenerator()
    
    # Inputs
    print("\nCONFIGURACION")
    print("-"*60)
    
    carpeta = input("Ruta a carpeta con imagenes: ").strip()
    
    if not carpeta.endswith("images"):
        print(f"\n Buscando carpeta 'images' en {carpeta}...")
        carpeta_con_images = Path(carpeta) / "images"
        if carpeta_con_images.exists():
            carpeta = str(carpeta_con_images)
            print(f" Encontrada: {carpeta}")
        else:
            print(f"No se encontro carpeta 'images'")
            print(f"ODM requiere que las imagenes esten en una carpeta llamada 'images'")
            return
    
    max_imgs_input = input("Maximo de maximo [1000]: ").strip()
    max_imgs = int(max_imgs_input) if max_imgs_input else 1000
    
    print("\nCalidad:")
    print("  1. lowest")
    print("  2. low")
    print("  3. medium")
    print("  4. high")
    print("  5. ultra")
    
    calidad_input = input("\nCalidad [3]: ").strip() or "3"
    calidad_map = {
        "1": "lowest",
        "2": "low",
        "3": "medium",
        "4": "high",
        "5": "ultra"
    }
    calidad = calidad_map.get(calidad_input, "medium")
    
    print(f"\nRESUMEN")
    print("-"*60)
    print(f"   Carpeta: {carpeta}")
    print(f"   Max imagenes: {max_imgs}")
    print(f"   Calidad: {calidad}")
    
    confirmar = input("\nContinuar? [s/n]: ").strip().lower()
    
    if confirmar == 's':
        success = generador.generar(carpeta, max_imgs, calidad)
        
        if success:
            print("\nEjecucion exitosa")
        else:
            print("\nHubo problemas. Revisar los logs.")
    else:
        print("Cancelado")


if __name__ == "__main__":
    main()