"""
Script para construir el ejecutable de la Calculadora de Banda Modular
Incluye todos los recursos necesarios y crea un instalador portable
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(message):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}[PASO] {message}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def check_dependencies():
    """Verifica que PyInstaller esté instalado"""
    print_step("Verificando dependencias")
    
    try:
        import PyInstaller
        print_success(f"PyInstaller encontrado: {PyInstaller.__version__}")
        return True
    except ImportError:
        print_error("PyInstaller no está instalado")
        print("\nInstalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print_success("PyInstaller instalado correctamente")
            return True
        except:
            print_error("No se pudo instalar PyInstaller")
            return False

def clean_build_folders():
    """Limpia carpetas de build anteriores"""
    print_step("Limpiando carpetas de builds anteriores")
    
    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print_success(f"Carpeta '{folder}' eliminada")
            except Exception as e:
                print_warning(f"No se pudo eliminar '{folder}': {e}")
        else:
            print(f"Carpeta '{folder}' no existe (OK)")

def verify_resources():
    """Verifica que todos los recursos necesarios existan"""
    print_step("Verificando recursos necesarios")
    
    required_files = [
        'main.py',
        'LISTA_PRODUCTOS.xlsx',
        'assets/Module30px.ico',
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print_success(f"Encontrado: {file}")
        else:
            print_error(f"Faltante: {file}")
            missing_files.append(file)
    
    if missing_files:
        print_error(f"\nFaltan {len(missing_files)} archivo(s) requerido(s)")
        return False
    
    print_success("\nTodos los recursos necesarios están presentes")
    return True

def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    print_step("Construyendo ejecutable")
    
    try:
        # Comando de PyInstaller
        cmd = [
            'pyinstaller',
            '--clean',  # Limpiar cache
            '--noconfirm',  # No pedir confirmación
            'build_launcher.spec'
        ]
        
        print(f"Ejecutando: {' '.join(cmd)}\n")
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print_success("\nEjecutable construido exitosamente")
            return True
        else:
            print_error("\nError al construir el ejecutable")
            return False
            
    except Exception as e:
        print_error(f"Error durante la construcción: {e}")
        return False

def create_portable_package():
    """Crea un paquete portable con el ejecutable y recursos"""
    print_step("Creando paquete portable")
    
    # Nombre del paquete
    package_name = "CalculadoraBandaModular_Portable"
    package_dir = os.path.join("dist", package_name)
    
    # Crear directorio del paquete
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copiar el ejecutable
    exe_name = "CalculadoraBandaModular.exe"
    exe_source = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, os.path.join(package_dir, exe_name))
        print_success(f"Copiado: {exe_name}")
    else:
        print_error(f"No se encontró el ejecutable: {exe_source}")
        return False
    
    # Copiar archivos externos (se accederán desde el directorio del exe)
    external_files = [
        'LISTA_PRODUCTOS.xlsx',
        'band_schemas.db',
    ]
    
    for file in external_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(package_dir, file))
            print_success(f"Copiado: {file}")
        else:
            if file == 'band_schemas.db':
                # Crear base de datos vacía
                import sqlite3
                db_path = os.path.join(package_dir, file)
                conn = sqlite3.connect(db_path)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS band_schemas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        serie TEXT NOT NULL,
                        tipo TEXT NOT NULL,
                        color TEXT NOT NULL,
                        ancho_banda REAL NOT NULL,
                        largo_banda REAL NOT NULL,
                        altura_modulo REAL NOT NULL,
                        grosor_pasador REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        modulos_data TEXT NOT NULL,
                        configuracion_data TEXT NOT NULL
                    )
                ''')
                conn.commit()
                conn.close()
                print_success(f"Creado: {file} (base de datos vacía)")
            else:
                print_warning(f"No encontrado: {file}")
    
    # Crear archivo README
    readme_content = """# Calculadora de Banda Modular - Versión Portable

## Instrucciones de Uso

1. **Ejecutar la aplicación:**
   - Doble clic en `CalculadoraBandaModular.exe`

2. **Archivos importantes:**
   - `LISTA_PRODUCTOS.xlsx`: Base de datos de productos (NO ELIMINAR)
   - `band_schemas.db`: Base de datos de esquemas guardados

3. **Portable:**
   - Puedes copiar esta carpeta completa a otra ubicación
   - Todos los esquemas guardados permanecerán en `band_schemas.db`
   - Puedes hacer backup de `band_schemas.db` para guardar tus esquemas

4. **Requisitos:**
   - Windows 7 o superior
   - NO requiere instalación
   - NO requiere Python instalado

## Características

- ✅ Cálculo automático de módulos
- ✅ Visualización gráfica de bandas
- ✅ Guardar y cargar esquemas
- ✅ Exportar imágenes
- ✅ Control de filas a graficar
- ✅ Redondeo de empujadores

## Soporte

Para más información, consulte los archivos README_*.md en la carpeta de desarrollo.

---
Versión: 1.0
Fecha: Diciembre 2025
"""
    
    readme_path = os.path.join(package_dir, "LEEME.txt")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print_success("Creado: LEEME.txt")
    
    print_success(f"\nPaquete portable creado en: {package_dir}")
    return True

def create_zip_package():
    """Crea un archivo ZIP del paquete portable"""
    print_step("Creando archivo ZIP")
    
    package_name = "CalculadoraBandaModular_Portable"
    package_dir = os.path.join("dist", package_name)
    
    if not os.path.exists(package_dir):
        print_error("No se encontró el paquete portable")
        return False
    
    try:
        # Crear ZIP
        zip_path = os.path.join("dist", f"{package_name}")
        shutil.make_archive(zip_path, 'zip', package_dir)
        print_success(f"Archivo ZIP creado: {zip_path}.zip")
        
        # Mostrar tamaño
        zip_file = f"{zip_path}.zip"
        size_mb = os.path.getsize(zip_file) / (1024 * 1024)
        print(f"Tamaño: {size_mb:.2f} MB")
        
        return True
    except Exception as e:
        print_error(f"Error al crear ZIP: {e}")
        return False

def main():
    """Función principal"""
    print(f"\n{Colors.GREEN}")
    print("="*60)
    print(" CONSTRUCTOR DE EJECUTABLE - CALCULADORA BANDA MODULAR")
    print("="*60)
    print(f"{Colors.END}\n")
    
    # Paso 1: Verificar dependencias
    if not check_dependencies():
        print_error("\nNo se puede continuar sin PyInstaller")
        return 1
    
    # Paso 2: Verificar recursos
    if not verify_resources():
        print_error("\nNo se puede continuar sin los recursos necesarios")
        return 1
    
    # Paso 3: Limpiar builds anteriores
    clean_build_folders()
    
    # Paso 4: Construir ejecutable
    if not build_executable():
        print_error("\nLa construcción falló")
        return 1
    
    # Paso 5: Crear paquete portable
    if not create_portable_package():
        print_error("\nNo se pudo crear el paquete portable")
        return 1
    
    # Paso 6: Crear ZIP
    create_zip_package()
    
    # Resumen final
    print_step("CONSTRUCCIÓN COMPLETADA")
    print_success("✓ Ejecutable creado exitosamente")
    print_success("✓ Paquete portable creado")
    print_success("✓ Archivo ZIP creado")
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Archivos generados en: dist/{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print("Ubicaciones:")
    print(f"  • Ejecutable: dist/CalculadoraBandaModular.exe")
    print(f"  • Portable: dist/CalculadoraBandaModular_Portable/")
    print(f"  • ZIP: dist/CalculadoraBandaModular_Portable.zip")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n\nProceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
