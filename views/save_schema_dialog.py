import tkinter as tk
from tkinter import messagebox, ttk

from models.database import BandDatabase


class SaveSchemaDialog(tk.Toplevel):
    def __init__(
        self,
        parent,
        serie,
        tipo,
        color,
        ancho_banda,
        largo_banda,
        altura_modulo,
        grosor_pasador,
        modulos_data,
        configuracion_data,
        nombre_sugerido=None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.serie = serie
        self.tipo = tipo
        self.color = color
        self.ancho_banda = ancho_banda
        self.largo_banda = largo_banda
        self.altura_modulo = altura_modulo
        self.grosor_pasador = grosor_pasador
        self.modulos_data = modulos_data
        self.configuracion_data = configuracion_data
        self.nombre_sugerido = nombre_sugerido
        self.db = BandDatabase()
        self.resultado = None

        self.title("Guardar Esquema de Banda")
        self.geometry("550x650")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.configure(bg="#F0F0F0")
        self.setup_ui()
        self.sugerir_nombre()
        self.center_window()

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="💾 Guardar Esquema de Banda",
            font=("Segoe UI", 14, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Opciones de guardado (RadioButtons)
        opciones_frame = ttk.LabelFrame(main_frame,
                                        text="Modo de Guardado",
                                        padding=10)
        opciones_frame.pack(fill=tk.X, pady=(0, 10))

        self.modo_var = tk.StringVar(value="nuevo")

        ttk.Radiobutton(
            opciones_frame,
            text="📝 Guardar como Nuevo",
            variable=self.modo_var,
            value="nuevo",
            command=self.on_modo_change
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            opciones_frame,
            text="🔄 Sobrescribir Existente",
            variable=self.modo_var,
            value="sobrescribir",
            command=self.on_modo_change
        ).pack(anchor=tk.W, pady=2)

        # Combobox para seleccionar esquema existente
        # (solo visible si se elige sobrescribir)
        self.combo_frame = ttk.Frame(opciones_frame)
        self.combo_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(
            self.combo_frame,
            text="Seleccione el esquema a sobrescribir:",
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W)

        # Cargar esquemas existentes
        esquemas = self.db.obtener_esquemas()
        esquemas_nombres = [
            f"{e['name']} - {e.get('cliente', 'Sin cliente')}"
            for e in esquemas
        ]
        self.esquemas_dict = {
            f"{e['name']} - {e.get('cliente', 'Sin cliente')}": e
            for e in esquemas
        }

        self.combo_esquemas = ttk.Combobox(
            self.combo_frame,
            values=esquemas_nombres,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.combo_esquemas.pack(fill=tk.X, pady=(5, 0))
        if esquemas_nombres:
            self.combo_esquemas.current(0)

        # Ocultar por defecto
        self.combo_frame.pack_forget()

        # Nombre del esquema
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            name_frame, text="Nombre del esquema:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)

        self.name_entry = ttk.Entry(name_frame, font=("Segoe UI", 10))
        self.name_entry.pack(fill=tk.X, pady=(5, 0))

        # Cliente
        cliente_frame = ttk.Frame(main_frame)
        cliente_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            cliente_frame, text="Cliente:", font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)

        self.cliente_entry = ttk.Entry(cliente_frame, font=("Segoe UI", 10))
        self.cliente_entry.pack(fill=tk.X, pady=(5, 0))

        # Descripción
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(
            desc_frame, text="Descripción (opcional):",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)

        self.desc_text = tk.Text(
            desc_frame, height=3, font=("Segoe UI", 9), wrap=tk.WORD
        )
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Información del esquema
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding=10)
        info_frame.pack(fill=tk.X, pady=10)

        info_text = f"""Serie: {self.serie}  |
        Tipo: {self.tipo}  |  Color: {self.color}
Ancho: {self.ancho_banda} mm  |  Largo: {self.largo_banda} m
Altura módulo: {self.altura_modulo} mm  |
Grosor pasador: {self.grosor_pasador} mm
Módulos configurados: {len(self.modulos_data)}"""

        info_label = ttk.Label(
            info_frame, text=info_text, font=("Segoe UI", 9), justify=tk.LEFT
        )
        info_label.pack()

        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))

        style = ttk.Style()
        style.configure("Success.TButton", foreground="green")

        btn_save = ttk.Button(
            buttons_frame,
            text="💾 Guardar",
            command=self.guardar,
            style="Success.TButton",
        )
        btn_save.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        btn_cancel = ttk.Button(
            buttons_frame, text="Cancelar", command=self.destroy
        )
        btn_cancel.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

    def on_modo_change(self):
        """Maneja el cambio de modo de guardado"""
        if self.modo_var.get() == "sobrescribir":
            self.combo_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.combo_frame.pack_forget()

    def sugerir_nombre(self):
        """Genera y sugiere un nombre para el esquema"""
        # Si se pasó un nombre sugerido, usarlo
        if self.nombre_sugerido:
            nombre = self.nombre_sugerido
        else:
            # Si no, usar el método de la base de datos
            nombre = self.db.generar_nombre_sugerido(
                self.serie, self.tipo, self.ancho_banda, self.largo_banda
            )
        self.name_entry.insert(0, nombre)
        self.name_entry.select_range(0, tk.END)
        self.name_entry.focus()

    def guardar(self):
        """Guarda el esquema en la base de datos"""
        modo = self.modo_var.get()
        cliente = self.cliente_entry.get().strip()
        descripcion = self.desc_text.get("1.0", tk.END).strip()

        if modo == "nuevo":
            # Guardar como nuevo
            nombre = self.name_entry.get().strip()

            if not nombre:
                messagebox.showwarning(
                    "Advertencia", "Debe ingresar un nombre para el esquema"
                )
                self.name_entry.focus()
                return

            success, message = self.db.guardar_esquema(
                nombre,
                cliente,
                descripcion,
                self.ancho_banda,
                self.largo_banda,
                self.serie,
                self.tipo,
                self.color,
                self.altura_modulo,
                self.grosor_pasador,
                self.modulos_data,
                self.configuracion_data,
            )

            if success:
                messagebox.showinfo("Éxito", message)
                self.resultado = True
                self.destroy()
            else:
                messagebox.showerror("Error", message)
                self.name_entry.focus()
                self.name_entry.select_range(0, tk.END)

        else:  # sobrescribir
            # Obtener el esquema seleccionado del combobox
            seleccion = self.combo_esquemas.get()
            if not seleccion:
                messagebox.showwarning(
                    "Advertencia",
                    "Debe seleccionar un esquema para sobrescribir"
                )
                return

            esquema_seleccionado = self.esquemas_dict.get(seleccion)
            if not esquema_seleccionado:
                messagebox.showerror(
                    "Error",
                    "No se pudo obtener el esquema seleccionado"
                )
                return

            # Confirmar sobrescritura
            respuesta = messagebox.askyesno(
                "Confirmar Sobrescritura",
                f"¿Está seguro de sobrescribir el esquema?\n\n"
                f"Nombre: {esquema_seleccionado['name']}\n"
                f"Cliente: {esquema_seleccionado.get('cliente', 'N/A')}\n\n"
                f"Esta acción no se puede deshacer.",
                icon="warning"
            )

            if not respuesta:
                return

            # Actualizar el esquema existente
            success, message = self.db.actualizar_esquema(
                esquema_seleccionado['id'],
                esquema_seleccionado['name'],  # Mantener el nombre original
                cliente,
                descripcion,
                self.ancho_banda,
                self.largo_banda,
                self.serie,
                self.tipo,
                self.color,
                self.altura_modulo,
                self.grosor_pasador,
                self.modulos_data,
                self.configuracion_data,
            )

            if success:
                messagebox.showinfo("Éxito", message)
                self.resultado = True
                self.destroy()
            else:
                messagebox.showerror("Error", message)

    def get_resultado(self):
        """Retorna si se guardó exitosamente"""
        return self.resultado
