import io
from tkinter import messagebox
from PIL import Image, ImageGrab
import pyperclip


def copiar_datos(texto_modulos: str) -> None:
    """
    Copia el texto de los módulos al portapapeles.
    """
    if not texto_modulos:
        messagebox.showwarning("Aviso", "No hay datos para copiar.")
        return
    pyperclip.copy(texto_modulos)
    messagebox.showinfo("Copiado", "Datos copiados al portapapeles.")


def copiar_imagen(img_memoria) -> None:
    """
    Copia la imagen al portapapeles en formato BMP,
    usando un stream de BytesIO.
    """
    if img_memoria is None:
        messagebox.showerror(
            "Error",
            "La imagen no está disponible. Genera la banda antes de copiarla."
        )
        return

    try:
        img = Image.open(img_memoria)
        output = io.BytesIO()
        img.convert("RGB").save(output, format="BMP")
        data = output.getvalue()[14:]
        output.close()

        clipboard_img = io.BytesIO(data)
        ImageGrab.grabclipboard = lambda: Image.open(clipboard_img)

        messagebox.showinfo(
            "Copiado",
            "Imagen copiada correctamente al portapapeles."
        )
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar la imagen: {e}")
