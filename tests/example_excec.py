from pathlib import Path

from core.resource_detector import ResourceDetector
from core.config_builder import ConfigBuilder
from core.odm_engine import ODMEngine

from infrastructure.output_manager import OutputManager
from infrastructure.logger import LoggerFactory


def ejemplo_basico():
    print("="*60)
    print("EJEMPLO 1: Uso Basico")
    print("="*60)
    
    resources = ResourceDetector.detect()
    print(resources)
    
    config = ConfigBuilder.build(resources, quality="medium")
    print(config)
    
    logger = LoggerFactory.create("ejemplo_basico")
    output_manager = OutputManager()
    
    output_dir = output_manager.create_next_output_dir()
    print(f"\nOutput: {output_dir}")
    
    engine = ODMEngine(logger)
    
    result = engine.execute(
        images_path=Path("D:/Personal/project/ortophotos/odm_data_aukerman/images"),
        output_path=output_dir,
        config=config
    )
    
    if result.success:
        print(f"\nExito!")
        print(f"Ortomosaico: {result.orthophoto_path}")

        output_manager.cleanup_intermediate_files(output_dir)
        
        output_manager.save_metadata(output_dir, {
            "proyecto": "ejemplo_basico",
            "calidad": "medium"
        })

        disk = output_manager.get_disk_usage(output_dir)
        print(f"Tamaño ortofoto: {disk['orthophoto_mb']:.1f} MB")
        
    else:
        print(f"\nError: {result.error_message}")


def ejemplo_personalizado():
    print("\n" + "="*60)
    print("EJEMPLO 2: Configuracion Personalizada")
    print("="*60)

    resources = ResourceDetector.detect()

    from core.config_builder import ODMConfig
    
    custom_config = ODMConfig(
        max_concurrency=12,
        feature_quality="high",
        pc_quality="high",
        mesh_size=1000000,
        orthophoto_resolution=1.5,
        dem_resolution=2.0,
        use_gpu=resources.has_gpu,
        generate_dsm=False,
        generate_dtm=False,
        skip_3dmodel=True,
        skip_report=True
    )
    
    print(custom_config)

    logger = LoggerFactory.create("ejemplo_custom")
    output_manager = OutputManager(base_path="./custom_outputs")
    output_dir = output_manager.create_next_output_dir(prefix="high_quality")
    
    engine = ODMEngine(logger)
    
    result = engine.execute(
        images_path=Path("D:/Personal/project/ortophotos/odm_data_aukerman/images"),
        output_path=output_dir,
        config=custom_config,
        max_images=100  # Solo primeras 100 imágenes
    )
    
    if result.success:
        print(f"\nGenerado: {result.orthophoto_path}")


def ejemplo_batch():
    print("\n" + "="*60)
    print("EJEMPLO 3: Procesamiento Batch")
    print("="*60)
    
    datasets = [
        "D:/datasets/proyecto1/images",
        "D:/datasets/proyecto2/images",
        "D:/datasets/proyecto3/images"
    ]
    
    resources = ResourceDetector.detect()
    config = ConfigBuilder.build(resources, quality="low")  # Low para batch

    logger = LoggerFactory.create("batch_processing")
    output_manager = OutputManager(base_path="./batch_outputs")
    engine = ODMEngine(logger)
    
    resultados = []
    
    for idx, dataset_path in enumerate(datasets, 1):
        print(f"\n[{idx}/{len(datasets)}] Procesando: {dataset_path}")
        
        output_dir = output_manager.create_next_output_dir()
        
        result = engine.execute(
            images_path=Path(dataset_path),
            output_path=output_dir,
            config=config,
            max_images=50 
        )
        
        resultados.append({
            "dataset": dataset_path,
            "success": result.success,
            "output": output_dir
        })
        
        if result.success:
            output_manager.cleanup_intermediate_files(output_dir)
    
    print("\n" + "="*60)
    print("RESUMEN BATCH")
    print("="*60)
    exitosos = sum(1 for r in resultados if r["success"])
    print(f"Exitosos: {exitosos}/{len(resultados)}")
    
    for r in resultados:
        status = "✓" if r["success"] else "✗"
        print(f"{status} {r['dataset']}")


def ejemplo_con_callback():
    """Ejemplo con callback de progreso."""
    print("\n" + "="*60)
    print("EJEMPLO 4: Con Callback de Progreso")
    print("="*60)
    
    def progress_handler(line: str):
        keywords = ["Running", "Completed", "Processing", "Done"]
        if any(kw in line for kw in keywords):
            print(f"  → {line}")

    resources = ResourceDetector.detect()
    config = ConfigBuilder.build(resources, quality="medium")
    logger = LoggerFactory.create("con_callback")
    output_manager = OutputManager()
    output_dir = output_manager.create_next_output_dir()
    
    engine = ODMEngine(logger)
    
    result = engine.execute(
        images_path=Path("D:/Personal/project/ortophotos/odm_data_aukerman/images"),
        output_path=output_dir,
        config=config,
        progress_callback=progress_handler 
    )
    
    if result.success:
        print(f"\nCompletado: {result.orthophoto_path}")


def ejemplo_listar_outputs():
    print("\n" + "="*60)
    print("EJEMPLO 5: Listar Outputs Existentes")
    print("="*60)
    
    output_manager = OutputManager()
    
    outputs = output_manager.list_output_dirs()
    
    print(f"Total outputs: {len(outputs)}\n")
    
    for output_dir in outputs:
        print(f"\n{output_dir.name}")
        print("-" * 40)

        metadata = output_manager.load_metadata(output_dir)
        if metadata:
            print(f"  Fecha:     {metadata.get('created_at', 'N/A')}")
            print(f"  Imagenes:  {metadata.get('processed_images', 'N/A')}")
            print(f"  Calidad:   {metadata.get('quality', 'N/A')}")
        
        disk = output_manager.get_disk_usage(output_dir)
        print(f"  Tamanno:    {disk['total_mb']:.1f} MB")
        print(f"  Ortofoto:  {disk['orthophoto_mb']:.1f} MB")
    
    latest = output_manager.get_latest_output_dir()
    if latest:
        print(f"\nUltimo generado: {latest}")


if __name__ == "__main__":
    import sys
    
    ejemplos = {
        "1": ("Basico", ejemplo_basico),
        "2": ("Personalizado", ejemplo_personalizado),
        "3": ("Batch", ejemplo_batch),
        "4": ("Con Callback", ejemplo_con_callback),
        "5": ("Listar Outputs", ejemplo_listar_outputs)
    }
    
    print("\nEJEMPLOS DE USO - Sistema de Ortomosaicos")
    print("="*60)
    for key, (name, _) in ejemplos.items():
        print(f"  {key}. {name}")
    print("  0. Ejecutar todos")
    print("="*60)
    
    choice = input("\nSeleccione ejemplo: ").strip()
    
    if choice == "0":
        for name, func in ejemplos.values():
            try:
                func()
            except Exception as e:
                print(f"\nError en {name}: {e}")
    elif choice in ejemplos:
        name, func = ejemplos[choice]
        try:
            func()
        except Exception as e:
            print(f"\nError: {e}")
    else:
        print("Opcion invalida")