import tkinter as tk
from tkinter import messagebox, ttk

from models.database import BandDatabase


class SchemaManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = BandDatabase()
        self.esquemas = []
        self.esquema_seleccionado = None

        self.title("Gestor de Esquemas de Bandas")
        self.geometry("1100x650")
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#F0F0F0")

        self.setup_ui()
        self.cargar_esquemas()
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
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="📋 Gestor de Esquemas de Bandas",
            font=("Segoe UI", 14, "bold"),
        )
        title_label.pack(pady=(0, 15))

        # Barra de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="🔍 Buscar:", font=("Segoe UI", 10)).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filtrar_esquemas)

        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, font=("Segoe UI", 10)
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_limpiar = ttk.Button(
            search_frame, text="✖", width=3, command=self.limpiar_busqueda
        )
        btn_limpiar.pack(side=tk.LEFT, padx=(5, 0))

        # Frame para la tabla con scrollbar
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Tabla (Treeview)
        columns = (
            "ID",
            "Nombre",
            "Cliente",
            "Serie",
            "Tipo",
            "Ancho",
            "Largo",
            "Módulos",
            "Fecha Mod.",
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Serie", text="Serie")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Ancho", text="Ancho (mm)")
        self.tree.heading("Largo", text="Largo (m)")
        self.tree.heading("Módulos", text="Módulos")
        self.tree.heading("Fecha Mod.", text="Fecha Modificación")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Nombre", width=180, anchor="w")
        self.tree.column("Cliente", width=150, anchor="w")
        self.tree.column("Serie", width=70, anchor="center")
        self.tree.column("Tipo", width=90, anchor="center")
        self.tree.column("Ancho", width=75, anchor="center")
        self.tree.column("Largo", width=75, anchor="center")
        self.tree.column("Módulos", width=70, anchor="center")
        self.tree.column("Fecha Mod.", width=130, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Doble clic para cargar
        self.tree.bind("<Double-1>",
                       lambda e: self.cargar_esquema_seleccionado())

        # Botones de acción
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        style = ttk.Style()
        style.configure("Success.TButton", foreground="green")
        style.configure("Danger.TButton", foreground="red")

        btn_cargar = ttk.Button(
            buttons_frame,
            text="✔ Cargar Esquema",
            command=self.cargar_esquema_seleccionado,
            style="Success.TButton",
        )
        btn_cargar.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        btn_ver = ttk.Button(
            buttons_frame, text="👁 Ver Detalle", command=self.ver_detalle
        )
        btn_ver.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        btn_editar = ttk.Button(
            buttons_frame, text="✏ Editar", command=self.editar_esquema
        )
        btn_editar.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        btn_eliminar = ttk.Button(
            buttons_frame,
            text="🗑 Eliminar",
            command=self.eliminar_esquema,
            style="Danger.TButton",
        )
        btn_eliminar.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        btn_actualizar = ttk.Button(
            buttons_frame, text="🔄 Actualizar", command=self.cargar_esquemas
        )
        btn_actualizar.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        btn_cerrar = ttk.Button(buttons_frame,
                                text="Cerrar", command=self.destroy)
        btn_cerrar.pack(side=tk.RIGHT, padx=5, ipadx=10, ipady=5)

    def cargar_esquemas(self):
        """Carga todos los esquemas de la base de datos"""
        self.esquemas = self.db.obtener_esquemas()
        self.mostrar_esquemas(self.esquemas)

    def mostrar_esquemas(self, esquemas):
        """Muestra los esquemas en la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar datos
        for esquema in esquemas:
            fecha = (esquema["fecha_modificacion"].split("T")[0]
                     if esquema.get("fecha_modificacion") else "")
            cliente = esquema.get("cliente", "") or "Sin cliente"
            self.tree.insert(
                "",
                "end",
                values=(
                    esquema["id"],
                    esquema["name"],
                    cliente,
                    esquema["serie"],
                    esquema["tipo"],
                    esquema["ancho_banda"],
                    esquema["largo_banda"],
                    len(esquema["modulos_data"]),
                    fecha,
                ),
            )

    def filtrar_esquemas(self, *args):
        """Filtra esquemas por el texto de búsqueda"""
        termino = self.search_var.get().lower()
        if not termino:
            self.mostrar_esquemas(self.esquemas)
            return

        filtrados = [
            e
            for e in self.esquemas
            if termino in e["name"].lower()
            or termino in e["serie"].lower()
            or termino in e["tipo"].lower()
            or (e.get("cliente") and termino in e["cliente"].lower())
            or (e["description"] and termino in e["description"].lower())
        ]
        self.mostrar_esquemas(filtrados)

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda"""
        self.search_var.set("")

    def get_esquema_seleccionado(self):
        """Obtiene el esquema seleccionado en la tabla"""
        selection = self.tree.selection()
        if not selection:
            return None

        item = self.tree.item(selection[0])
        esquema_id = item["values"][0]

        for esquema in self.esquemas:
            if esquema["id"] == esquema_id:
                return esquema
        return None

    def cargar_esquema_seleccionado(self):
        """Carga el esquema seleccionado"""
        esquema = self.get_esquema_seleccionado()
        if not esquema:
            messagebox.showwarning(
                "Advertencia", "Debe seleccionar un esquema de la lista"
            )
            return

        self.esquema_seleccionado = esquema
        self.destroy()

    def ver_detalle(self):
        """Muestra el detalle del esquema seleccionado"""
        esquema = self.get_esquema_seleccionado()
        if not esquema:
            messagebox.showwarning(
                "Advertencia", "Debe seleccionar un esquema de la lista"
            )
            return

        SchemaDetailDialog(self, esquema)

    def editar_esquema(self):
        """Edita el nombre y descripción del esquema"""
        esquema = self.get_esquema_seleccionado()
        if not esquema:
            messagebox.showwarning(
                "Advertencia", "Debe seleccionar un esquema de la lista"
            )
            return

        dialog = EditSchemaDialog(self, esquema)
        self.wait_window(dialog)

        if dialog.resultado:
            self.cargar_esquemas()

    def eliminar_esquema(self):
        """Elimina el esquema seleccionado"""
        esquema = self.get_esquema_seleccionado()
        if not esquema:
            messagebox.showwarning(
                "Advertencia", "Debe seleccionar un esquema de la lista"
            )
            return

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el esquema '{esquema['name']}'?\n\n"
            f"Esta acción no se puede deshacer.",
            icon="warning",
        )

        if respuesta:
            success, message = self.db.eliminar_esquema(esquema["id"])
            if success:
                messagebox.showinfo("Éxito", message)
                self.cargar_esquemas()
            else:
                messagebox.showerror("Error", message)

    def get_resultado(self):
        """Retorna el esquema seleccionado para cargar"""
        return self.esquema_seleccionado


class EditSchemaDialog(tk.Toplevel):
    def __init__(self, parent, esquema):
        super().__init__(parent)
        self.parent = parent
        self.esquema = esquema
        self.resultado = False

        self.title("Editar Esquema")
        self.geometry("550x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#F0F0F0")

        self.setup_ui()
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
            main_frame, text="✏ Editar Esquema", font=("Segoe UI", 12, "bold")
        )
        title_label.pack(pady=(0, 15))

        # Nombre
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            name_frame, text="Nombre:", font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)

        self.name_entry = ttk.Entry(name_frame, font=("Segoe UI", 10))
        self.name_entry.pack(fill=tk.X, pady=(5, 0))
        self.name_entry.insert(0, self.esquema["name"])

        # Cliente
        cliente_frame = ttk.Frame(main_frame)
        cliente_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            cliente_frame, text="Cliente:", font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)

        self.cliente_entry = ttk.Entry(cliente_frame, font=("Segoe UI", 10))
        self.cliente_entry.pack(fill=tk.X, pady=(5, 0))
        cliente_valor = self.esquema.get("cliente", "") or ""
        if cliente_valor:
            self.cliente_entry.insert(0, str(cliente_valor))

        # Descripción
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            desc_frame, text="Descripción:", font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)

        self.desc_text = tk.Text(
            desc_frame, height=3, font=("Segoe UI", 9), wrap=tk.WORD
        )
        self.desc_text.pack(fill=tk.X, pady=(5, 0))

        descripcion = self.esquema.get("description", "")
        if descripcion:
            self.desc_text.insert("1.0", str(descripcion))

        # Info no editable
        info_frame = ttk.LabelFrame(main_frame,
                                    text="Información (no editable)",
                                    padding=10)
        info_frame.pack(fill=tk.X, pady=10)

        info_text = f"""
        Serie: {self.esquema['serie']}  |
        Tipo: {self.esquema['tipo']}
        Ancho: {self.esquema['ancho_banda']} mm  |
        Largo: {self.esquema['largo_banda']} m"""

        info_label = ttk.Label(
            info_frame, text=info_text, font=("Segoe UI", 9), justify=tk.LEFT
        )
        info_label.pack()

        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))

        btn_save = ttk.Button(
            buttons_frame, text="💾 Guardar", command=self.guardar
        )
        btn_save.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        btn_cancel = ttk.Button(
            buttons_frame, text="Cancelar", command=self.destroy
        )
        btn_cancel.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

    def guardar(self):
        """Guarda los cambios"""
        nombre = self.name_entry.get().strip()

        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre")
            self.name_entry.focus()
            return

        cliente = self.cliente_entry.get().strip()
        descripcion = self.desc_text.get("1.0", tk.END).strip()

        db = BandDatabase()
        success, message = db.actualizar_esquema(
            self.esquema["id"],
            nombre,
            cliente,
            descripcion,
            self.esquema["ancho_banda"],
            self.esquema["largo_banda"],
            self.esquema["serie"],
            self.esquema["tipo"],
            self.esquema["color"],
            self.esquema["altura_modulo"],
            self.esquema["grosor_pasador"],
            self.esquema["modulos_data"],
            self.esquema["configuracion_data"],
        )

        if success:
            messagebox.showinfo("Éxito", message)
            self.resultado = True
            self.destroy()
        else:
            messagebox.showerror("Error", message)
            self.name_entry.focus()


class SchemaDetailDialog(tk.Toplevel):
    def __init__(self, parent, esquema):
        super().__init__(parent)
        self.parent = parent
        self.esquema = esquema

        self.title(f"Detalle: {esquema['name']}")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#F0F0F0")

        self.setup_ui()
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
            text=f"📄 {self.esquema['name']}",
            font=("Segoe UI", 12, "bold"),
        )
        title_label.pack(pady=(0, 15))

        # Frame con scroll para los detalles
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(
            canvas_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenido del detalle
        content_frame = ttk.Frame(scrollable_frame, padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Información general
        self.add_section(content_frame, "Información General")
        self.add_field(content_frame, "Nombre", self.esquema["name"])
        self.add_field(content_frame, "Serie", self.esquema["serie"])
        self.add_field(content_frame, "Tipo", self.esquema["tipo"])
        self.add_field(content_frame, "Color", self.esquema["color"])

        # Dimensiones
        self.add_section(content_frame, "Dimensiones")
        self.add_field(
            content_frame, "Ancho de banda",
            f"{self.esquema['ancho_banda']} mm"
        )
        self.add_field(
            content_frame, "Largo de banda",
            f"{self.esquema['largo_banda']} m"
        )
        self.add_field(
            content_frame, "Altura módulo",
            f"{self.esquema['altura_modulo']} mm"
        )
        self.add_field(
            content_frame, "Grosor pasador",
            f"{self.esquema['grosor_pasador']} mm"
        )

        # Descripción
        if self.esquema["description"]:
            self.add_section(content_frame, "Descripción")
            desc_label = ttk.Label(
                content_frame,
                text=self.esquema["description"],
                font=("Segoe UI", 9),
                wraplength=500,
                justify=tk.LEFT,
            )
            desc_label.pack(anchor=tk.W, pady=(0, 10))

        # Módulos
        self.add_section(content_frame, "Módulos Configurados")
        modulos_text = tk.Text(
            content_frame, height=10, font=("Courier New", 9), wrap=tk.WORD
        )
        modulos_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        for i, modulo in enumerate(self.esquema["modulos_data"], 1):
            modulo_info = f"{i}. "
            if isinstance(modulo, dict):
                for key, value in modulo.items():
                    modulo_info += f"{key}: {value}, "
                modulo_info = modulo_info.rstrip(", ")
            else:
                modulo_info += str(modulo)
            modulos_text.insert(tk.END, modulo_info + "\n")

        modulos_text.config(state="disabled")

        # Fechas
        self.add_section(content_frame, "Fechas")
        fecha_creacion = self.esquema["fecha_creacion"].split("T")[0]
        fecha_mod = self.esquema["fecha_modificacion"].split("T")[0]
        self.add_field(content_frame, "Fecha de creación", fecha_creacion)
        self.add_field(content_frame, "Última modificación", fecha_mod)

        # Botón cerrar
        btn_close = ttk.Button(main_frame, text="Cerrar", command=self.destroy)
        btn_close.pack(pady=(10, 0))

        self.bind("<Escape>", lambda e: self.destroy())

    def add_section(self, parent, title):
        """Añade un título de sección"""
        section_label = ttk.Label(
            parent, text=title, font=("Segoe UI", 10, "bold")
        )
        section_label.pack(anchor=tk.W, pady=(10, 5))

        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill=tk.X, pady=(0, 5))

    def add_field(self, parent, label, value):
        """Añade un campo de información"""
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill=tk.X, pady=2)

        ttk.Label(
            field_frame, text=f"{label}:",
            font=("Segoe UI", 9, "bold"), width=20
        ).pack(side=tk.LEFT)

        ttk.Label(field_frame, text=str(value),
                  font=("Segoe UI", 9)).pack(
            side=tk.LEFT
        )
