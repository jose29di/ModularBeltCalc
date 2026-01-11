@echo off
chcp 65001 >nul
echo.
echo ========================================
echo  CONSTRUIR EJECUTABLE
echo  Calculadora de Banda Modular
echo ========================================
echo.

echo [1/3] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo.
echo [2/3] Ejecutando script de construcción...
python build_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: La construcción falló
    pause
    exit /b 1
)

echo.
echo [3/3] Construcción completada
echo.
echo ========================================
echo  ARCHIVOS GENERADOS:
echo ========================================
echo   • dist\CalculadoraBandaModular.exe
echo   • dist\CalculadoraBandaModular_Portable\
echo   • dist\CalculadoraBandaModular_Portable.zip
echo ========================================
echo.

echo ¿Desea abrir la carpeta dist? (S/N)
set /p respuesta=
if /i "%respuesta%"=="S" (
    explorer dist
)

pause
