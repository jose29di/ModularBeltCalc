# views/loading_view.py
import tkinter as tk
from tkinter import ttk


class LoadingModal(tk.Toplevel):
    def __init__(self, parent, title="Espere",
                 message="Generando, por favor espere...", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title(title)
        self.transient(parent)  # Se mantiene encima de la ventana principal
        self.grab_set()         # Bloquea la interacción con la principal

        # Dimensiones deseadas para la ventana modal
        w_modal = 300
        h_modal = 120

        # Forzar a que 'parent' actualice su geometría
        parent.update_idletasks()

        # Calcular la posición para centrar el modal
        x = parent.winfo_rootx()
        + (parent.winfo_width() // 2) - (w_modal // 2)
        y = parent.winfo_rooty()
        + (parent.winfo_height() // 2) - (h_modal // 2)

        self.geometry(f"{w_modal}x{h_modal}+{x}+{y}")

        # Configuración de widgets del modal
        self.label = ttk.Label(
            self,
            text=message,
            font=("Arial", 10, "italic"),
            foreground="red"
        )
        self.label.pack(pady=10)

        self.progressbar = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=250
        )
        self.progressbar.pack(pady=10)
        self.progressbar.start(10)  # Inicia la animación

    def stop(self):
        self.progressbar.stop()
        self.destroy()
