from cryptography.fernet import Fernet

# Cargar la clave secreta desde el archivo
def cargar_clave():
    return open("clave_secreta.key", "rb").read()

# Decriptar el archivo conexion_encriptada.txt
def decriptar_archivo():
    clave = cargar_clave()  # Cargar la clave desde el archivo
    fernet = Fernet(clave)  # Crear el objeto Fernet con la clave

    # Leer los datos encriptados desde el archivo conexion_encriptada.txt
    with open("conexion_encriptada.txt", "rb") as archivo_encriptado:
        datos_encriptados = archivo_encriptado.read()

    # Decriptar los datos
    datos_decriptados = fernet.decrypt(datos_encriptados).decode()

    # Imprimir los datos de conexión decriptados
    print("Conexión decriptada:")
    print(datos_decriptados)  # Mostrar la información de conexión decriptada

# Ejecutar el proceso de decriptación
decriptar_archivo()
