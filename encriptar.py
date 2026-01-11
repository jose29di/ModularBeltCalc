from cryptography.fernet import Fernet

# Generar una clave secreta para encriptar
def generar_clave():
    clave = Fernet.generate_key()  # Genera una nueva clave
    with open("clave_secreta.key", "wb") as archivo_clave:
        archivo_clave.write(clave)  # Guarda la clave en un archivo

# Cargar la clave secreta desde el archivo
def cargar_clave():
    return open("clave_secreta.key", "rb").read()

# Encriptar el archivo conexion.txt y guardarlo como conexion_encriptada.txt
def encriptar_archivo():
    clave = cargar_clave()  # Cargar la clave desde el archivo
    fernet = Fernet(clave)  # Crear el objeto Fernet con la clave

    # Leer los datos de conexion.txt
    with open("conexion.txt", "rb") as archivo:
        datos = archivo.read()  # Leer los datos del archivo

    # Encriptar los datos
    datos_encriptados = fernet.encrypt(datos)

    # Guardar los datos encriptados en un archivo de texto
    with open("conexion_encriptada.txt", "wb") as archivo_encriptado:
        archivo_encriptado.write(datos_encriptados)  # Escribir los datos encriptados en el archivo

# Ejecutar los pasos
# Si es la primera vez que ejecutas el script, descomenta la siguiente línea para generar la clave
# generar_clave()

# Encriptar los datos del archivo conexion.txt
encriptar_archivo()
