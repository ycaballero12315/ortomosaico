"""
Script para verificar que el comando ODM se construye correctamente.
"""

from pathlib import Path
from core.resource_detector import ResourceDetector
from core.config_builder import ConfigBuilder
from core.odm_engine import ODMEngine


def test_command_building():
    """Prueba la construcción del comando sin ejecutarlo."""
    
    print("="*60)
    print("TEST: Construcción de Comando ODM")
    print("="*60)
    
    # Detectar recursos
    resources = ResourceDetector.detect()
    print(f"\nRecursos detectados:")
    print(f"  GPU: {resources.has_gpu}")
    print(f"  CPU: {resources.cpu_cores_physical} cores")
    
    # Crear configuración
    config = ConfigBuilder.build(resources, quality="medium")
    
    # Parámetros ODM
    params = config.to_odm_params()
    print(f"\nParámetros ODM generados:")
    for param in params:
        print(f"  {param}")
    
    # Construir comando completo
    images_path = Path("D:/test/images")
    output_path = Path("D:/test/output")
    
    engine = ODMEngine()
    cmd = engine._build_docker_command(
        images_path,
        output_path,
        config,
        max_images=None
    )
    
    print("\n" + "="*60)
    print("COMANDO DOCKER COMPLETO:")
    print("="*60)
    print("\n" + " \\\n  ".join(cmd))
    
    # Verificar que no hay "false" o "true" como strings separados
    problematic = [p for p in cmd if p.lower() in ('true', 'false')]
    if problematic:
        print(f"\n⚠ ADVERTENCIA: Parámetros problemáticos: {problematic}")
    else:
        print("\n✓ No se encontraron parámetros problemáticos")
    
    # Contar parámetros ODM
    odm_params = [p for p in cmd if p.startswith("--")]
    print(f"\n✓ Total de parámetros ODM: {len(odm_params)}")


if __name__ == "__main__":
    test_command_building()