import math
import threading
import tkinter as tk
from decimal import Decimal
from tkinter import PhotoImage, messagebox, ttk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

from controllers.generator import (generar_esquema_banda_personalizado,
                                   procesar_entrada_arreglo)
# Ajusta estas importaciones a tu estructura
from controllers.utils import resource_path
from views.save_schema_dialog import SaveSchemaDialog
from views.schema_manager import SchemaManagerDialog

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE ESTILO Y VARIABLES GLOBALES - TEMA MODERNO
# ---------------------------------------------------------------------
# Paleta de colores moderna
BG_COLOR = "#FFFFFF"  # Fondo blanco limpio
BG_SECONDARY = "#F8F9FA"  # Gris muy claro para contraste
PRIMARY_COLOR = "#1E3A8A"  # Azul oscuro profesional
SECONDARY_COLOR = "#3B82F6"  # Azul moderno vibrante
ACCENT_COLOR = "#10B981"  # Verde esmeralda para acciones positivas
WARNING_COLOR = "#EF4444"  # Rojo moderno para limpiar
INFO_COLOR = "#8B5CF6"  # Púrpura para acciones secundarias
TEXT_PRIMARY = "#1F2937"  # Gris oscuro para texto principal
TEXT_SECONDARY = "#6B7280"  # Gris medio para texto secundario
BORDER_COLOR = "#E5E7EB"  # Borde sutil
HOVER_COLOR = "#DBEAFE"  # Azul claro para hover

FONT_NAME = "Segoe UI"
FONT_TITLE = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 10)
FONT_INPUT = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 10, "bold")

canvas = None
label_modulos = None
status_bar = None
df_unificado = None

# ---------------------------------------------------------------------
# FUNCIÓN: CARGAR Y UNIFICAR DATOS DEL EXCEL
# ---------------------------------------------------------------------


def cargar_datos_unificados(excel_path: str):
    try:
        df_serie = pd.read_excel(excel_path, sheet_name="serie")
        df_tipo = pd.read_excel(excel_path, sheet_name="tipo")
        df_material = pd.read_excel(excel_path, sheet_name="material")
        df_color = pd.read_excel(excel_path, sheet_name="color")
        df_productos = pd.read_excel(excel_path, sheet_name="productos")
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el Excel: {e}")
        return None

    df_merge = df_productos.merge(
        df_serie, left_on="serie_id", right_on="id", suffixes=("", "_serie")
    )
    df_merge = df_merge.merge(
        df_tipo, left_on="tipo_id", right_on="id", suffixes=("", "_tipo")
    )
    df_merge = df_merge.merge(
        df_material,
        left_on="material_id",
        right_on="id",
        suffixes=("", "_material"),
    )
    df_merge = df_merge.merge(
        df_color, left_on="color_id", right_on="id", suffixes=("", "_color")
    )
    df_merge = df_merge[
        [
            "Serie",
            "TipoBanda",
            "Material",
            "ColorBanda",
            "Altura_mm",
            "Pasador_mm",
            "Lateral",
        ]
    ]
    return df_merge


# ---------------------------------------------------------------------
# FUNCIONES: ACTUALIZAR COMBOS DEPENDIENTES
# ---------------------------------------------------------------------


def actualizar_combo_tipo(combo_tipo, df, serie_seleccionada):
    df_filtrado = df[df["Serie"].str.strip() == serie_seleccionada]
    tipos = sorted(df_filtrado["TipoBanda"].unique())
    combo_tipo["values"] = tipos
    if tipos:
        combo_tipo.set(tipos[0])
    else:
        combo_tipo.set("")


def actualizar_combo_material(
    combo_material, df, serie_seleccionada, tipo_seleccionado
):
    # Verificar si la columna Material existe
    if 'Material' not in df.columns:
        combo_material["values"] = []
        combo_material.set("")
        combo_material.config(state="disabled")
        return

    df_filtrado = df[
        (df["Serie"].str.strip() == serie_seleccionada)
        & (df["TipoBanda"] == tipo_seleccionado)
    ]
    materiales = sorted(df_filtrado["Material"].dropna().unique())
    combo_material["values"] = materiales
    combo_material.config(state="readonly")
    if materiales:
        combo_material.set(materiales[0])
    else:
        combo_material.set("")


def actualizar_combo_color(
    combo_color,
    df,
    serie_seleccionada,
    tipo_seleccionado,
    material_seleccionado=""
):
    df_filtrado = df[
        (df["Serie"].str.strip() == serie_seleccionada)
        & (df["TipoBanda"] == tipo_seleccionado)
    ]
    # Filtrar por material solo si la columna existe
    # y hay un valor seleccionado
    if material_seleccionado and 'Material' in df.columns:
        df_filtrado = df_filtrado[
            df_filtrado["Material"] == material_seleccionado
        ]

    colores = sorted(df_filtrado["ColorBanda"].unique())
    combo_color["values"] = colores
    if colores:
        combo_color.set(colores[0])
    else:
        combo_color.set("")


def on_combo_serie_select(
    event,
    combo_series,
    combo_tipo,
    combo_material,
    combo_color,
    variables_check
):
    serie = combo_series.get().strip()
    df_filtrado = df_unificado[df_unificado["Serie"].str.strip() == serie]
    print(f"Serie seleccionada: {serie}\nDatos filtrados:\n{df_filtrado}")

    if not df_filtrado.empty:
        alt = df_filtrado.iloc[0]["Altura_mm"]
        pas = df_filtrado.iloc[0]["Pasador_mm"]
        entry_altura_modulo.config(state="normal")
        entry_altura_modulo.delete(0, tk.END)
        entry_altura_modulo.insert(0, str(alt))
        entry_altura_modulo.config(state="readonly")

        entry_grosor_pasador.config(state="normal")
        entry_grosor_pasador.delete(0, tk.END)
        entry_grosor_pasador.insert(0, str(pas))
        entry_grosor_pasador.config(state="readonly")

        variables_check["check_desglose"].set(
            df_filtrado.iloc[0]["Lateral"] == "S"
        )
    else:
        entry_altura_modulo.config(state="normal")
        entry_altura_modulo.delete(0, tk.END)
        entry_altura_modulo.insert(0, "0")
        entry_altura_modulo.config(state="readonly")

        entry_grosor_pasador.config(state="normal")
        entry_grosor_pasador.delete(0, tk.END)
        entry_grosor_pasador.insert(0, "0")
        entry_grosor_pasador.config(state="readonly")

        variables_check["check_desglose"].set(False)

    actualizar_combo_tipo(combo_tipo, df_unificado, serie)
    if combo_tipo.get():
        actualizar_combo_material(
            combo_material, df_unificado, serie, combo_tipo.get()
        )
        if combo_material.get():
            actualizar_combo_color(
                combo_color,
                df_unificado,
                serie,
                combo_tipo.get(),
                combo_material.get()
            )


def on_combo_tipo_select(
    event, combo_series, combo_tipo, combo_material, combo_color, df
):
    serie = combo_series.get().strip()
    tipo = combo_tipo.get().strip()
    actualizar_combo_material(combo_material, df, serie, tipo)
    if combo_material.get():
        actualizar_combo_color(
            combo_color, df, serie, tipo, combo_material.get()
        )


def on_combo_material_select(
    event, combo_series, combo_tipo, combo_material, combo_color, df
):
    serie = combo_series.get().strip()
    tipo = combo_tipo.get().strip()
    material = combo_material.get().strip()
    actualizar_combo_color(combo_color, df, serie, tipo, material)


# ---------------------------------------------------------------------
# POPUP DE CARGA CON PROGRESO (IND) Y HILO
# ---------------------------------------------------------------------


def show_loading_popup(master):
    """
    Crea un Toplevel centrado sobre 'master' con
    un label y una barra de progreso indeterminada.
    Retorna (popup, progressbar).
    """
    popup = tk.Toplevel(master)
    popup.title("Cargando...")
    popup.resizable(False, False)
    popup.transient(master)
    popup.grab_set()

    # Variable para controlar el keep_alive
    popup._keep_running = True

    # Configurar tamaño y posición
    w, h = 300, 120
    master.update_idletasks()
    master_x = master.winfo_rootx()
    master_y = master.winfo_rooty()
    master_width = master.winfo_width()
    master_height = master.winfo_height()
    x = master_x + (master_width // 2) - (w // 2)
    y = master_y + (master_height // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.configure(bg="white")
    # Frame principal
    main_frame = ttk.Frame(popup, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    # Label de texto
    lbl = ttk.Label(
        main_frame,
        text="Cargando, por favor espera...",
        font=("Arial", 10),
        anchor="center",
    )
    lbl.pack(pady=(0, 15))
    # Barra de progreso
    prog = ttk.Progressbar(main_frame, mode="indeterminate", length=250)
    prog.pack(pady=(0, 10))
    prog.start(10)
    # Función para mantener el popup activo

    def keep_alive():
        try:
            if popup.winfo_exists() and getattr(popup, "_keep_running", False):
                popup.update_idletasks()
                popup.after(50, keep_alive)  # Actualizar cada 50ms
        except tk.TclError:
            popup._keep_running = False

    # Iniciar el keep_alive
    popup.after(10, keep_alive)

    return popup, prog


# ---------------------------------------------------------------------
# FUNCIÓN PRINCIPAL: run_app()
# ---------------------------------------------------------------------


def run_app() -> None:
    global df_unificado, entry_altura_modulo, entry_grosor_pasador
    excel_path = resource_path("LISTA_PRODUCTOS.xlsx")
    df_unificado = cargar_datos_unificados(excel_path)
    if df_unificado is None:
        print("No se pudo leer el Excel.")

    root = tk.Tk()
    root.title("Calculadora de Banda Modular")
    root.geometry("1200x800")
    root.configure(bg=BG_COLOR)
    root.iconbitmap(resource_path("assets/Module30px.ico"))

    # Configurar el tema visual moderno
    root.option_add("*TCombobox*Listbox.font", FONT_INPUT)
    root.option_add("*TCombobox*Listbox.selectBackground", SECONDARY_COLOR)

    # Función para cerrar la aplicación completamente
    def on_closing():
        try:
            # Cerrar todas las figuras de matplotlib
            plt.close("all")

            # Terminar todos los hilos daemon
            import threading

            for thread in threading.enumerate():
                if thread != threading.current_thread() and thread.daemon:
                    try:
                        # Los hilos daemon deberían terminar automáticamente
                        pass
                    except Exception:
                        pass

            # Destruir la ventana principal
            root.quit()
            root.destroy()

            # Forzar salida del programa
            import sys

            sys.exit(0)

        except Exception as e:
            print(f"Error al cerrar: {e}")
            import sys

            sys.exit(1)

    # Configurar el protocolo de cierre de ventana
    root.protocol("WM_DELETE_WINDOW", on_closing)

    configurar_estilo()

    # Marco principal con padding optimizado
    marco_principal = ttk.Frame(root, padding=8, style="Main.TFrame")
    marco_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Sección Izquierda
    (
        marco_entradas,
        combo_series,
        combo_tipo,
        combo_material,
        combo_color,
        entry_altura_modulo,
        entry_grosor_pasador,
        entry_largo_banda,
        variables_check,
        text_area_esquema,
        text_sumas,
        entry_filas_grafico,
        entry_tipo_empujador,
        entry_tipo_indentacion,
    ) = crear_seccion_entradas(marco_principal)

    # Inicializar combos
    if df_unificado is not None and not df_unificado.empty:
        combo_series["values"] = sorted(df_unificado["Serie"].unique())
        if df_unificado["Serie"].nunique() > 0:
            default_serie = sorted(df_unificado["Serie"].unique())[0].strip()
            combo_series.set(default_serie)
            on_combo_serie_select(
                None,
                combo_series,
                combo_tipo,
                combo_material,
                combo_color,
                variables_check
            )

    combo_series.bind(
        "<<ComboboxSelected>>",
        lambda event: on_combo_serie_select(
            event,
            combo_series,
            combo_tipo,
            combo_material,
            combo_color,
            variables_check
        ),
    )
    combo_tipo.bind(
        "<<ComboboxSelected>>",
        lambda event: on_combo_tipo_select(
            event,
            combo_series,
            combo_tipo,
            combo_material,
            combo_color,
            df_unificado
        ),
    )
    combo_material.bind(
        "<<ComboboxSelected>>",
        lambda event: on_combo_material_select(
            event,
            combo_series,
            combo_tipo,
            combo_material,
            combo_color,
            df_unificado
        ),
    )

    # Marco de botones
    marco_botones_accion = crear_marco_botones(
        marco_entradas
    )

    # Sección Derecha
    (frame_resumen, label_generando, frame_canvas, listbox_detalles) = (
        crear_seccion_detalles(marco_principal)
    )

    asignar_botones_accion(
        root,
        marco_botones_accion,
        combo_series,
        combo_tipo,
        combo_material,
        combo_color,
        entry_altura_modulo,
        entry_grosor_pasador,
        entry_largo_banda,
        variables_check,
        text_area_esquema,
        text_sumas,
        frame_canvas,
        label_generando,
        listbox_detalles,
        entry_filas_grafico,
        entry_tipo_empujador,
        entry_tipo_indentacion,
    )

    global status_bar
    status_bar = ttk.Label(
        root,
        text=" 🟢 Listo",
        relief=tk.FLAT,
        anchor=tk.W,
        font=(FONT_NAME, 9),
        padding=(10, 5),
        style="StatusBar.TLabel"
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()


# ---------------------------------------------------------------------
# CONFIGURAR ESTILO MODERNO
# ---------------------------------------------------------------------
def configurar_estilo() -> None:
    style = ttk.Style()
    style.theme_use("clam")

    # Configuración de Frame principal
    style.configure("Main.TFrame", background=BG_COLOR)
    style.configure("TFrame", background=BG_COLOR)

    # Labels
    style.configure(
        "TLabel",
        background=BG_COLOR,
        foreground=TEXT_PRIMARY,
        font=FONT_LABEL
    )

    style.configure(
        "Title.TLabel",
        background=BG_COLOR,
        foreground=PRIMARY_COLOR,
        font=FONT_TITLE
    )

    style.configure(
        "StatusBar.TLabel",
        background=BG_SECONDARY,
        foreground=TEXT_SECONDARY,
        font=(FONT_NAME, 9)
    )

    # LabelFrame moderno
    style.configure(
        "TLabelframe",
        background=BG_COLOR,
        borderwidth=2,
        relief="solid",
        bordercolor=BORDER_COLOR
    )
    style.configure(
        "TLabelframe.Label",
        background=BG_COLOR,
        foreground=PRIMARY_COLOR,
        font=FONT_TITLE,
        padding=(5, 0)
    )

    # Entry moderno
    style.configure(
        "TEntry",
        fieldbackground="white",
        borderwidth=1,
        relief="solid",
        padding=8
    )

    # Combobox moderno
    style.configure(
        "TCombobox",
        fieldbackground="white",
        background="white",
        borderwidth=1,
        arrowsize=15,
        padding=8
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "white")],
        selectbackground=[("readonly", "white")],
        selectforeground=[("readonly", TEXT_PRIMARY)]
    )

    # Botones modernos con efectos
    style.configure(
        "Accent.TButton",
        background=SECONDARY_COLOR,
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(15, 10),
        font=FONT_BUTTON,
        relief="flat"
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", PRIMARY_COLOR),
            ("pressed", PRIMARY_COLOR),
            ("!disabled", SECONDARY_COLOR)
        ],
        foreground=[("active", "white"), ("pressed", "white")],
        relief=[("pressed", "flat"), ("!pressed", "flat")]
    )

    # Botón de éxito (Calcular)
    style.configure(
        "Success.TButton",
        background=ACCENT_COLOR,
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(15, 10),
        font=FONT_BUTTON,
        relief="flat"
    )
    style.map(
        "Success.TButton",
        background=[
            ("active", "#059669"),
            ("pressed", "#047857"),
            ("!disabled", ACCENT_COLOR)
        ]
    )

    # Botón de advertencia (Limpiar)
    style.configure(
        "Warning.TButton",
        background=WARNING_COLOR,
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(15, 10),
        font=FONT_BUTTON,
        relief="flat"
    )
    style.map(
        "Warning.TButton",
        background=[
            ("active", "#DC2626"),
            ("pressed", "#B91C1C"),
            ("!disabled", WARNING_COLOR)
        ]
    )

    # Checkbutton moderno
    style.configure(
        "TCheckbutton",
        background=BG_COLOR,
        foreground=TEXT_PRIMARY,
        font=FONT_LABEL,
        padding=(5, 5)
    )

    # Notebook (tabs) moderno
    style.configure(
        "TNotebook",
        background=BG_COLOR,
        borderwidth=0,
        tabmargins=[5, 5, 5, 0]
    )
    style.configure(
        "TNotebook.Tab",
        background=BG_SECONDARY,
        foreground=TEXT_SECONDARY,
        padding=(20, 10),
        borderwidth=0,
        font=FONT_LABEL
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", BG_COLOR),
            ("active", HOVER_COLOR)
        ],
        foreground=[
            ("selected", PRIMARY_COLOR),
            ("active", PRIMARY_COLOR)
        ],
        expand=[("selected", [1, 1, 1, 0])]
    )

    # Scrollbar moderna
    style.configure(
        "Vertical.TScrollbar",
        background=BG_SECONDARY,
        troughcolor=BG_COLOR,
        borderwidth=0,
        arrowsize=14
    )
    style.map(
        "Vertical.TScrollbar",
        background=[
            ("active", TEXT_SECONDARY),
            ("!disabled", BG_SECONDARY)
        ]
    )


# ---------------------------------------------------------------------
# CREAR SECCIÓN IZQUIERDA (Entradas) - DISEÑO MODERNO CON SCROLL
# ---------------------------------------------------------------------
def crear_seccion_entradas(parent):
    style = ttk.Style()
    style.configure(
        "Input.TLabel",
        background=BG_COLOR,
        foreground=TEXT_PRIMARY,
        font=FONT_LABEL
    )
    style.configure(
        "InputBold.TLabel",
        background=BG_COLOR,
        foreground=PRIMARY_COLOR,
        font=FONT_TITLE
    )

    # Frame contenedor con scroll
    marco_scroll_container = ttk.Frame(parent)
    marco_scroll_container.pack(
        side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10)
    )

    # Canvas para scroll
    canvas_scroll = tk.Canvas(
        marco_scroll_container,
        bg=BG_COLOR,
        highlightthickness=0,
        width=400
    )
    scrollbar_vertical = ttk.Scrollbar(
        marco_scroll_container,
        orient="vertical",
        command=canvas_scroll.yview
    )

    # Frame scrollable que contendrá el marco_entradas
    frame_scrollable = ttk.Frame(canvas_scroll)

    # Configurar el canvas
    frame_scrollable.bind(
        "<Configure>",
        lambda e: canvas_scroll.configure(
            scrollregion=canvas_scroll.bbox("all")
        )
    )

    canvas_scroll.create_window((0, 0), window=frame_scrollable, anchor="nw")
    canvas_scroll.configure(yscrollcommand=scrollbar_vertical.set)

    # Empaquetar canvas y scrollbar
    canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)

    # Habilitar scroll con rueda del mouse
    def _on_mousewheel(event):
        canvas_scroll.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel)

    # Ahora crear el marco_entradas dentro del frame_scrollable
    marco_entradas = ttk.LabelFrame(
        frame_scrollable,
        text="⚙️ Parámetros de Entrada",
        padding=10,
        style="TLabelframe"
    )
    marco_entradas.pack(fill=tk.BOTH, expand=True)

    # Fila 1: Serie
    fila_1 = ttk.Frame(marco_entradas)
    fila_1.pack(fill=tk.X, pady=3)
    lbl_serie = ttk.Label(
        fila_1,
        text="Serie:",
        style="InputBold.TLabel",
        width=20
    )
    lbl_serie.pack(side=tk.LEFT, padx=(0, 10))
    combo_series = ttk.Combobox(
        fila_1, state="readonly", width=18, font=FONT_INPUT
    )
    combo_series.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Fila 2: TipoBanda
    fila_2 = ttk.Frame(marco_entradas)
    fila_2.pack(fill=tk.X, pady=3)
    lbl_tipo = ttk.Label(
        fila_2,
        text="Tipo de Banda:",
        style="Input.TLabel",
        width=20
    )
    lbl_tipo.pack(side=tk.LEFT, padx=(0, 10))
    combo_tipo = ttk.Combobox(
        fila_2, state="readonly", width=18, font=FONT_INPUT
    )
    combo_tipo.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Fila 3: Material
    fila_3 = ttk.Frame(marco_entradas)
    fila_3.pack(fill=tk.X, pady=3)
    lbl_material = ttk.Label(
        fila_3, text="Material:", style="Input.TLabel", width=20
    )
    lbl_material.pack(side=tk.LEFT, padx=(0, 10))
    combo_material = ttk.Combobox(
        fila_3, state="readonly", width=18, font=FONT_INPUT
    )
    combo_material.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Fila 4: ColorBanda
    fila_4 = ttk.Frame(marco_entradas)
    fila_4.pack(fill=tk.X, pady=3)
    # Fila 4: ColorBanda
    fila_4 = ttk.Frame(marco_entradas)
    fila_4.pack(fill=tk.X, pady=3)
    lbl_color = ttk.Label(
        fila_4,
        text="Color de Banda:",
        style="Input.TLabel",
        width=20
    )
    lbl_color.pack(side=tk.LEFT, padx=(0, 10))
    combo_color = ttk.Combobox(
        fila_4, state="readonly", width=18, font=FONT_INPUT
    )
    combo_color.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Se usan los colores que me diste anteriormente para el combobox
    colores = {
        "Maywa": "Morado",
        "Waminsi": "Rosado",
        "Rosado": "Café",
        "Kishpu": "Naranja",
    }
    combo_color["values"] = list(colores.values())

    # Separador visual
    ttk.Separator(marco_entradas, orient="horizontal").pack(fill=tk.X, pady=10)

    # Fila 4: Altura Módulo
    fila_4 = ttk.Frame(marco_entradas)
    fila_4.pack(fill=tk.X, pady=3)
    lbl_altura = ttk.Label(
        fila_4,
        text="Altura del módulo (mm):",
        style="Input.TLabel",
        width=20
    )
    lbl_altura.pack(side=tk.LEFT, padx=(0, 10))
    entry_altura_modulo = ttk.Entry(
        fila_4, width=18, font=FONT_INPUT
    )
    entry_altura_modulo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry_altura_modulo.insert(0, "30")
    entry_altura_modulo.config(state="readonly")

    # Fila 5: Pasador
    fila_5 = ttk.Frame(marco_entradas)
    fila_5.pack(fill=tk.X, pady=3)
    lbl_pasador = ttk.Label(
        fila_5,
        text="Pasador (mm):",
        style="Input.TLabel",
        width=20
    )
    lbl_pasador.pack(side=tk.LEFT, padx=(0, 10))
    entry_grosor_pasador = ttk.Entry(
        fila_5, width=18, font=FONT_INPUT
    )
    entry_grosor_pasador.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry_grosor_pasador.insert(0, "0")
    entry_grosor_pasador.config(state="readonly")

    # Separador visual
    ttk.Separator(marco_entradas, orient="horizontal").pack(
        fill=tk.X, pady=5
    )

    # Fila 6: Largo de banda
    fila_6 = ttk.Frame(marco_entradas)
    fila_6.pack(fill=tk.X, pady=3)
    lbl_largo = ttk.Label(
        fila_6,
        text="Largo de banda (cm):",
        style="Input.TLabel",
        width=20
    )
    lbl_largo.pack(side=tk.LEFT, padx=(0, 10))
    entry_largo_banda = ttk.Entry(
        fila_6, width=18, font=FONT_INPUT
    )
    entry_largo_banda.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry_largo_banda.insert(0, "27.00")

    # Fila 7: Filas a visualizar en gráfico
    fila_7 = ttk.Frame(marco_entradas)
    fila_7.pack(fill=tk.X, pady=3)
    lbl_filas_grafico = ttk.Label(
        fila_7,
        text="Filas a graficar:",
        style="Input.TLabel",
        width=20
    )
    lbl_filas_grafico.pack(side=tk.LEFT, padx=(0, 10))
    entry_filas_grafico = ttk.Entry(
        fila_7, width=18, font=FONT_INPUT
    )
    entry_filas_grafico.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry_filas_grafico.insert(0, "10")

    # Tooltip/ayuda con estilo moderno
    lbl_help_filas = ttk.Label(
        fila_7,
        text=" ℹ️ ",
        cursor="hand2",
        style="Input.TLabel"
    )
    lbl_help_filas.pack(side=tk.LEFT, padx=5)

    def mostrar_ayuda_filas(event=None):
        messagebox.showinfo(
            "Filas a Graficar",
            "Esta opción controla cuántas filas se muestran en el gráfico.\n\n"
            "• Por defecto: 10 filas\n"
            "• Ingrese 0 o deje vacío para mostrar TODAS las filas\n"
            "• Los cálculos SIEMPRE se hacen con todas las filas\n\n"
            "Nota: Esto solo afecta la visualización del gráfico, "
            "no los cálculos de módulos, pasadores o tapas."
        )

    lbl_help_filas.bind("<Button-1>", mostrar_ayuda_filas)

    # Separador antes de opciones
    ttk.Separator(marco_entradas, orient="horizontal").pack(fill=tk.X, pady=5)

    # Título de opciones
    ttk.Label(
        marco_entradas,
        text="Opciones de Configuración",
        style="InputBold.TLabel"
    ).pack(anchor="w", pady=(0, 5))

    # Checks con diseño mejorado
    vars_check = {
        "check_empujadores": tk.BooleanVar(value=False),
        "check_indentacion": tk.BooleanVar(value=False),
        "check_desglose": tk.BooleanVar(value=False),
        "check_redondear_arriba": tk.BooleanVar(value=False),
    }

    # Checkbox de empujadores con combobox de tipo
    fr_chk_empujadores = ttk.Frame(marco_entradas)
    fr_chk_empujadores.pack(fill=tk.X, pady=2)
    chk_empujadores = ttk.Checkbutton(
        fr_chk_empujadores,
        text="✓ Con Empujador/ Modulo",
        variable=vars_check["check_empujadores"],
        style="TCheckbutton"
    )
    chk_empujadores.pack(side=tk.LEFT, anchor="w", padx=5)

    # Entry para tipo de empujador
    entry_tipo_empujador = ttk.Entry(
        fr_chk_empujadores,
        width=12,
        font=FONT_INPUT
    )
    entry_tipo_empujador.insert(0, "E-5")  # Valor por defecto
    entry_tipo_empujador.pack(side=tk.LEFT, padx=5)

    # Checkbox de indentación con entry
    fr_chk_indentacion = ttk.Frame(marco_entradas)
    fr_chk_indentacion.pack(fill=tk.X, pady=2)
    chk_indentacion = ttk.Checkbutton(
        fr_chk_indentacion,
        text="✓ Con Indentación/TM",
        variable=vars_check["check_indentacion"],
        style="TCheckbutton"
    )
    chk_indentacion.pack(side=tk.LEFT, anchor="w", padx=5)

    # Entry para tipo de indentación
    entry_tipo_indentacion = ttk.Entry(
        fr_chk_indentacion,
        width=12,
        font=FONT_INPUT
    )
    entry_tipo_indentacion.insert(0, "I-5")  # Valor por defecto
    entry_tipo_indentacion.pack(side=tk.LEFT, padx=5)

    # Checkbox de módulos laterales
    fr_chk_desglose = ttk.Frame(marco_entradas)
    fr_chk_desglose.pack(fill=tk.X, pady=2)
    chk_desglose = ttk.Checkbutton(
        fr_chk_desglose,
        text="✓ Es con módulos laterales",
        variable=vars_check["check_desglose"],
        style="TCheckbutton"
    )
    chk_desglose.pack(anchor="w", padx=5)

    # Checkbox de redondeo (con ayuda)
    fr_chk_redondeo = ttk.Frame(marco_entradas)
    fr_chk_redondeo.pack(fill=tk.X, pady=2)
    chk_redondeo = ttk.Checkbutton(
        fr_chk_redondeo,
        text="✓ Redondear filas hacia arriba",
        variable=vars_check["check_redondear_arriba"],
        style="TCheckbutton"
    )
    chk_redondeo.pack(anchor="w", padx=5, side=tk.LEFT)

    # Ayuda para redondeo
    lbl_help_redondeo = ttk.Label(
        fr_chk_redondeo,
        text=" ℹ️ ",
        cursor="hand2",
        style="Input.TLabel"
    )
    lbl_help_redondeo.pack(side=tk.LEFT, padx=5)

    def mostrar_ayuda_redondeo(event=None):
        messagebox.showinfo(
            "Redondeo de Filas de Empujadores",
            "⚠️ SOLO APLICA CUANDO 'Con Empujador' ESTÁ MARCADO\n\n"
            "Esta opción redistribuye las filas entre empujadores y módulos\n"
            "SIN cambiar el largo total de la banda.\n\n"
            "✓ ACTIVADO (Redondear hacia arriba):\n"
            "  • Ejemplo: 13.5 empujadores → 14 empujadores\n"
            "  • Se REDUCE el número de módulos para compensar\n"
            "  • Más empujadores, menos módulos\n\n"
            "✗ DESACTIVADO (Redondear hacia abajo):\n"
            "  • Ejemplo: 13.5 empujadores → 13 empujadores\n"
            "  • Se AUMENTA el número de módulos para compensar\n"
            "  • Menos empujadores, más módulos\n\n"
            "Nota: El largo total de la banda NO cambia,\n"
            "solo cambia la proporción empujadores/módulos."
        )

    lbl_help_redondeo.bind("<Button-1>", mostrar_ayuda_redondeo)

    # Separador antes de esquema
    ttk.Separator(marco_entradas, orient="horizontal").pack(fill=tk.X, pady=5)

    # TextArea Esquema con diseño moderno
    ttk.Label(
        marco_entradas,
        text="📐 Esquema de Banda",
        style="InputBold.TLabel",
    ).pack(anchor="w", pady=(0, 3))

    marco_esquema = ttk.Frame(marco_entradas)
    marco_esquema.pack(fill=tk.BOTH, expand=False, pady=(0, 5))
    scrollbar_esq = ttk.Scrollbar(marco_esquema, orient=tk.VERTICAL)
    text_area_esquema = tk.Text(
        marco_esquema,
        height=4,
        width=30,
        yscrollcommand=scrollbar_esq.set,
        font=FONT_INPUT,
        bg="white",
        fg=TEXT_PRIMARY,
        relief="solid",
        borderwidth=1,
        padx=5,
        pady=5
    )
    text_area_esquema.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_esq.config(command=text_area_esquema.yview)
    scrollbar_esq.pack(side=tk.RIGHT, fill=tk.Y)
    text_area_esquema.insert(
        tk.END,
        "50,200,200,200,50\n"
        "200,200,200,100\n"
        "100,200,200,200\n"
        "200,200,200,100",
    )

    # TextArea Cálculos con diseño moderno
    ttk.Label(
        marco_entradas,
        text="🧮 Cálculos por Fila",
        style="InputBold.TLabel"
    ).pack(anchor="w", pady=(0, 3))

    marco_sumas = ttk.Frame(marco_entradas)
    marco_sumas.pack(fill=tk.BOTH, expand=False)
    scrollbar_sumas = ttk.Scrollbar(marco_sumas, orient=tk.VERTICAL)
    text_sumas = tk.Text(
        marco_sumas,
        height=4,
        width=30,
        wrap="word",
        yscrollcommand=scrollbar_sumas.set,
        state=tk.DISABLED,
        font=FONT_INPUT,
        bg=BG_SECONDARY,
        fg=TEXT_PRIMARY,
        relief="solid",
        borderwidth=1,
        padx=5,
        pady=5
    )
    text_sumas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_sumas.config(command=text_sumas.yview)
    scrollbar_sumas.pack(side=tk.RIGHT, fill=tk.Y)

    def recalcular_sumas_filas(event=None):
        texto = text_area_esquema.get("1.0", "end").strip()
        filas = texto.split("\n")
        resultado = []
        for i, fila in enumerate(filas, start=1):
            if not fila.strip():
                continue
            try:
                nums = list(map(int, fila.split(",")))
                suma = sum(nums)
                resultado.append(f"Fila {i}: {suma} mm")
            except ValueError:
                resultado.append(f"Fila {i}: Error (datos inválidos)")
        text_sumas.config(state=tk.NORMAL)
        text_sumas.delete("1.0", tk.END)
        text_sumas.insert(tk.END, "\n".join(resultado))
        text_sumas.config(state=tk.DISABLED)
        text_sumas.yview_moveto(1.0)

    text_area_esquema.bind("<KeyRelease>", recalcular_sumas_filas)
    # Binding para pegado (Ctrl+V o botón derecho pegar)
    text_area_esquema.bind(
        "<<Modified>>",
        lambda e: text_area_esquema.after(10, recalcular_sumas_filas)
    )

    def al_cambiar_combo_serie(event):
        pass

    combo_series.bind("<<ComboboxSelected>>", al_cambiar_combo_serie)

    return (
        marco_entradas,
        combo_series,
        combo_tipo,
        combo_material,
        combo_color,
        entry_altura_modulo,
        entry_grosor_pasador,
        entry_largo_banda,
        vars_check,
        text_area_esquema,
        text_sumas,
        entry_filas_grafico,
        entry_tipo_empujador,
        entry_tipo_indentacion,
    )


# ---------------------------------------------------------------------
# CREAR MARCO DE BOTONES - DISEÑO MODERNO
# ---------------------------------------------------------------------
def crear_marco_botones(marco_entradas):
    # Separador antes de botones
    ttk.Separator(marco_entradas, orient="horizontal").pack(fill=tk.X, pady=5)

    marco_botones = ttk.Frame(marco_entradas)
    marco_botones.pack(pady=5, fill="x")

    # Configurar columnas para expansión uniforme
    marco_botones.columnconfigure(0, weight=1)
    marco_botones.columnconfigure(1, weight=1)

    return marco_botones


# ---------------------------------------------------------------------
# CREAR SECCIÓN DERECHA: NOTEBOOK (Resumen / Detalles) - DISEÑO MODERNO
# ---------------------------------------------------------------------
def crear_seccion_detalles(parent):
    """
    Sección derecha con pestañas para Resumen y Detalles
    """
    global label_modulos
    marco_datos = ttk.LabelFrame(
        parent,
        text="📊 Resultados del Cálculo",
        padding=10,
        style="TLabelframe"
    )
    marco_datos.pack(
        side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0)
    )
    notebook = ttk.Notebook(marco_datos)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Tab Resumen
    tab_resumen = ttk.Frame(notebook)
    notebook.add(tab_resumen, text="📈 Resumen")

    frame_resumen = ttk.Frame(tab_resumen)
    frame_resumen.pack(fill=tk.BOTH, expand=True)

    # PanedWindow vertical
    paned = ttk.PanedWindow(frame_resumen, orient=tk.VERTICAL)
    paned.pack(fill=tk.BOTH, expand=True)

    # Parte superior - Resumen de texto con scroll
    frame_texto = ttk.Frame(paned)
    label_generando = ttk.Label(
        frame_texto,
        text="",
        font=(FONT_NAME, 10, "italic"),
        foreground=INFO_COLOR
    )
    label_generando.pack(pady=5)
    # Frame para el texto con scroll
    frame_texto_scroll = ttk.Frame(frame_texto)
    frame_texto_scroll.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    scrollbar_texto = ttk.Scrollbar(frame_texto_scroll, orient=tk.VERTICAL)
    label_modulos = tk.Text(
        frame_texto_scroll,
        wrap="word",
        font=FONT_LABEL,
        bg=BG_COLOR,
        fg=TEXT_PRIMARY,
        relief="flat",
        borderwidth=0,
        padx=0,
        pady=0,
        yscrollcommand=scrollbar_texto.set,
        state=tk.DISABLED
    )
    label_modulos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_texto.config(command=label_modulos.yview)
    scrollbar_texto.pack(side=tk.RIGHT, fill=tk.Y)

    # Parte inferior - Gráfico
    frame_grafico = ttk.Frame(paned)
    canvas_wrapper = tk.Canvas(frame_grafico,
                               bg=BG_COLOR,
                               highlightthickness=0)
    vsb = ttk.Scrollbar(
        frame_grafico, orient="vertical", command=canvas_wrapper.yview
    )
    canvas_wrapper.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas_wrapper.pack(side="left", fill="both", expand=True)
    frame_canvas = ttk.Frame(canvas_wrapper)
    canvas_wrapper.create_window((0, 0), window=frame_canvas, anchor="nw")

    def on_frame_configure(event):
        canvas_wrapper.configure(scrollregion=canvas_wrapper.bbox("all"))

    frame_canvas.bind("<Configure>", on_frame_configure)

    paned.add(frame_texto, weight=1)
    paned.add(frame_grafico, weight=3)

    # Tab Detalles
    tab_detalles = ttk.Frame(notebook)
    notebook.add(tab_detalles, text="📋 Detalles")

    frame_lista_detalles = ttk.Frame(tab_detalles)
    frame_lista_detalles.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
    scrollbar = ttk.Scrollbar(frame_lista_detalles, orient=tk.VERTICAL)
    listbox_detalles = tk.Listbox(
        frame_lista_detalles,
        font=FONT_LABEL,
        yscrollcommand=scrollbar.set,
        selectmode=tk.EXTENDED,
        bg="white",
        fg=TEXT_PRIMARY,
        selectbackground=SECONDARY_COLOR,
        selectforeground="white",
        relief="solid",
        borderwidth=1,
        highlightthickness=0
    )
    listbox_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox_detalles.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    # Frame para mostrar suma de selección
    frame_suma_seleccion = ttk.LabelFrame(
        tab_detalles,
        text="📊 Resumen de Selección",
        padding=10, style="TLabelframe")
    frame_suma_seleccion.pack(fill=tk.X, padx=10, pady=(5, 10))
    label_suma_seleccion = ttk.Label(
        frame_suma_seleccion,
        text="Seleccione líneas para ver totales",
        font=FONT_LABEL,
        foreground=TEXT_SECONDARY,
        anchor="w"
    )
    label_suma_seleccion.pack(fill=tk.X)

    # Función para actualizar suma cuando cambia la selección
    def actualizar_suma_seleccion(event=None):
        import re
        seleccion = listbox_detalles.curselection()
        if not seleccion:
            label_suma_seleccion.config(
                text="Seleccione líneas para ver totales",
                foreground=TEXT_SECONDARY)
            return
        # Diccionario para agrupar las sumas por tipo
        totales = {}
        total_items = 0
        for idx in seleccion:
            linea = listbox_detalles.get(idx)
            # Buscar patrones de cantidades: "N pzs",
            # "N piezas", "N pieza", "N unidades", "N unidad"
            match_piezas = re.search(
                r'(\d+)\s*(?:pzs|piezas?|unidades?)',
                linea, re.IGNORECASE)
            if match_piezas:
                cantidad = int(match_piezas.group(1))
                # Extraer el tipo de componente
                tipo = linea.split(':')[0].strip() if ':' in linea else "Items"
                if tipo not in totales:
                    totales[tipo] = 0
                totales[tipo] += cantidad
                total_items += cantidad
        if totales:
            # Construir texto de resumen
            resumen_partes = []
            for tipo, cantidad in totales.items():
                resumen_partes.append(f"{tipo}: {cantidad} pzs")
            resumen = " | ".join(resumen_partes)
            # Agregar total general
            if total_items > 0:
                resumen += f" | TOTAL: {total_items} pzs"
            if len(seleccion) > 1:
                resumen = f"{len(seleccion)} líneas → {resumen}"
            label_suma_seleccion.config(text=resumen, foreground=PRIMARY_COLOR)
        else:
            label_suma_seleccion.config(
                text=(f"{len(seleccion)} líneas seleccionadas "
                      f"(sin valores numéricos)"),
                foreground=TEXT_SECONDARY
            )

    # Vincular evento de cambio de selección
    listbox_detalles.bind("<<ListboxSelect>>", actualizar_suma_seleccion)

    menu_copiar = tk.Menu(listbox_detalles, tearoff=0)
    menu_copiar.add_command(
        label="Copiar",
        command=lambda: copiar_seleccion_detalles(listbox_detalles),
    )
    listbox_detalles.bind(
        "<Control-c>", lambda e: copiar_seleccion_detalles(listbox_detalles)
    )
    listbox_detalles.bind(
        "<Button-3>", lambda e: mostrar_menu(e, listbox_detalles, menu_copiar)
    )
    return frame_resumen, label_generando, frame_canvas, listbox_detalles


# ---------------------------------------------------------------------
# ASIGNAR BOTONES DE ACCIÓN
# ---------------------------------------------------------------------


def asignar_botones_accion(
    root,
    marco_botones,
    combo_series,
    combo_tipo,
    combo_material,
    combo_color,
    entry_altura_modulo,
    entry_grosor_pasador,
    entry_largo_banda,
    vars_check,
    text_area_esquema,
    text_sumas,
    frame_canvas,
    label_generando,
    listbox_detalles,
    entry_filas_grafico,
    entry_tipo_empujador,
    entry_tipo_indentacion,
):
    global label_modulos, canvas, df_unificado

    def cargar_icono(ruta):
        try:
            return PhotoImage(file=resource_path(ruta))
        except Exception:
            return None

    # Los iconos ya no se usan con los botones modernos
    # icon_generar = cargar_icono("assets/icon_generar.png")
    # icon_guardar = cargar_icono("assets/icon_guardar.png")
    # icon_reset = cargar_icono("assets/icon_reset.png")

    def calcular_banda():
        # Obtener valores antes del hilo para evitar problemas de threading
        serie_sel = combo_series.get().strip()
        color_sel = combo_color.get().strip()
        tipo_sel = combo_tipo.get().strip()
        material_sel = combo_material.get().strip()
        largo_txt = entry_largo_banda.get().strip()
        # Validaciones previas
        if not serie_sel:
            messagebox.showwarning(
                "Advertencia", "Debe seleccionar una serie antes de calcular."
            )
            return
        if not color_sel:
            messagebox.showwarning(
                "Advertencia", "Seleccione un color antes de calcular."
            )
            return
        if not tipo_sel:
            messagebox.showwarning(
                "Advertencia", "Seleccione un tipo de banda antes de calcular."
            )
            return
        if not largo_txt:
            messagebox.showwarning(
                "Advertencia",
                "Debe ingresar un valor para el Largo de Banda (cm).",
            )
            return

        # Variable para controlar el popup
        loading_popup = None

        def cerrar_loading_popup():
            nonlocal loading_popup
            try:
                if loading_popup and loading_popup.winfo_exists():
                    # Detener el keep_alive del popup
                    loading_popup._keep_running = False
                    loading_popup.grab_release()
                    loading_popup.destroy()
                    loading_popup = None
            except tk.TclError:
                loading_popup = None

        def worker():
            try:
                # Obtener parámetros del DataFrame
                df_filtrado = df_unificado[
                    (df_unificado["Serie"].str.strip() == serie_sel)
                    & (df_unificado["TipoBanda"] == tipo_sel)
                    & (df_unificado["ColorBanda"] == color_sel)
                ]
                if not df_filtrado.empty:
                    alt_mod = int(df_filtrado.iloc[0]["Altura_mm"])
                    mm_pasador = Decimal(
                        str(df_filtrado.iloc[0]["Pasador_mm"]).replace(
                            ",", "."
                        )
                    )
                else:
                    alt_mod = int(entry_altura_modulo.get())
                    mm_pasador = Decimal(
                        entry_grosor_pasador.get().strip().replace(",", ".")
                    )

                largo_mm = round(float(largo_txt) * 10)
                txt_esquema = text_area_esquema.get("1.0", tk.END)
                esquema = procesar_entrada_arreglo(txt_esquema)
                if esquema is None:
                    root.after(0, cerrar_loading_popup)
                    return

                # Obtener valores de checkboxes
                check_empujadores = vars_check["check_empujadores"].get()
                check_indentacion = vars_check["check_indentacion"].get()
                check_desglose = vars_check["check_desglose"].get()
                check_redondear_arriba = vars_check[
                    "check_redondear_arriba"
                ].get()

                # Obtener tipo de empujador
                tipo_empujador_sel = (
                    entry_tipo_empujador.get().strip()
                    if entry_tipo_empujador.get() else "E-5"
                )

                # Obtener tipo de indentación
                tipo_indentacion_sel = (
                    entry_tipo_indentacion.get().strip()
                    if entry_tipo_indentacion.get() else "I-5"
                )

                # Actualizar label de progreso
                root.after(
                    0,
                    lambda: label_generando.config(
                        text=(
                            f"Generando esquema con Serie={serie_sel}, "
                            f"Color={color_sel}, Tipo={tipo_sel}..."
                        )
                    ),
                )

                # Obtener filas a graficar
                try:
                    filas_graf_txt = entry_filas_grafico.get().strip()
                    if filas_graf_txt:
                        filas_graf = int(filas_graf_txt)
                    else:
                        filas_graf = 0  # 0 = todas las filas
                except ValueError:
                    filas_graf = 10  # Valor por defecto si hay error

                # Preparar datos para el hilo principal
                datos_calculo = {
                    "esquema": esquema,
                    "alt_mod": alt_mod,
                    "largo_mm": largo_mm,
                    "mm_pasador": mm_pasador,
                    "check_empujadores": check_empujadores,
                    "check_indentacion": check_indentacion,
                    "check_desglose": check_desglose,
                    "check_redondear_arriba": check_redondear_arriba,
                    "serie_sel": serie_sel,
                    "color_sel": color_sel,
                    "tipo_sel": tipo_sel,
                    "material_sel": material_sel,
                    "filas_graficar": filas_graf,
                    "tipo_empujador_sel": tipo_empujador_sel,
                    "tipo_indentacion_sel": tipo_indentacion_sel,
                }

                # Ejecutar creación del gráfico en hilo principal
                def ejecutar_ui_update():
                    crear_grafico_y_actualizar_ui(datos_calculo)

                root.after(0, ejecutar_ui_update)

            except ValueError:

                def show_error():
                    messagebox.showerror("Error", "Error en valores numéricos")

                root.after(0, show_error)
                root.after(0, cerrar_loading_popup)
            except Exception:

                def show_error():
                    messagebox.showerror("Error", "Error inesperado")

                root.after(0, show_error)
                root.after(0, cerrar_loading_popup)
            finally:
                # Asegurar que el popup se cierre siempre
                root.after(0, cerrar_loading_popup)

        def crear_grafico_y_actualizar_ui(datos):
            try:
                global canvas
                # Crear figura EN EL HILO PRINCIPAL
                fig, ax = plt.subplots(figsize=(10, 6))
                # Llamar función con parámetros corregidos
                result = generar_esquema_banda_personalizado(
                    fig,
                    ax,
                    datos["esquema"],
                    datos["alt_mod"],
                    datos["largo_mm"],
                    datos["check_empujadores"],
                    datos["check_desglose"],
                    datos["check_indentacion"],
                    datos["filas_graficar"],
                    datos["check_redondear_arriba"],
                )
                if not result:
                    cerrar_loading_popup()
                    return

                # Verificar cuántos valores devuelve result y extraer
                if isinstance(result, dict):
                    total_emp = result.get("total_filas_empujadores", 0)
                    total_mod = result.get("total_filas_modulos", 0)
                    m_izq = result.get("modulos_izquierdos", {})
                    m_der = result.get("modulos_derechos", {})
                    m_ct = result.get("modulos_centrales", {})
                    m_ei = result.get("modulos_empujadores_izquierdos", {})
                    m_ed = result.get("modulos_empujadores_derechos", {})
                    m_ec = result.get("modulos_empujadores_centrales", {})
                else:
                    if len(result) >= 8:
                        (
                            total_emp,
                            total_mod,
                            m_izq,
                            m_der,
                            m_ct,
                            m_ei,
                            m_ed,
                            m_ec,
                        ) = result[:8]
                    else:
                        valores = list(result) + [{}] * (8 - len(result))
                        (
                            total_emp,
                            total_mod,
                            m_izq,
                            m_der,
                            m_ct,
                            m_ei,
                            m_ed,
                            m_ec,
                        ) = valores[:8]

                # Limpiar canvas previo
                for w in frame_canvas.winfo_children():
                    w.destroy()
                # Crear nuevo canvas
                canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                canvas.draw()
                # Crear toolbar
                tb_frame = ttk.Frame(frame_canvas)
                tb_frame.pack(fill=tk.X)
                tb = NavigationToolbar2Tk(canvas, tb_frame)
                tb.update()
                # Construir texto resumen
                resumen_texto = construir_texto_resumen(
                    datos["esquema"],
                    datos["alt_mod"],
                    datos["mm_pasador"],
                    total_emp,
                    total_mod,
                    m_izq,
                    m_der,
                    m_ct,
                    m_ei,
                    m_ed,
                    m_ec,
                    datos["check_empujadores"],
                    datos["check_indentacion"],
                    datos["check_desglose"],
                )
                label_modulos.config(state=tk.NORMAL)
                label_modulos.delete("1.0", tk.END)
                label_modulos.insert("1.0", resumen_texto)
                label_modulos.config(state=tk.DISABLED)
                # Llenar listbox detalles
                listbox_detalles.delete(0, tk.END)
                llenar_listbox_detalles(
                    listbox_detalles,
                    datos["esquema"],
                    datos["alt_mod"],
                    datos["mm_pasador"],
                    total_emp,
                    total_mod,
                    m_izq,
                    m_der,
                    m_ct,
                    m_ei,
                    m_ed,
                    m_ec,
                    datos["check_empujadores"],
                    datos["check_indentacion"],
                    datos["check_desglose"],
                    datos["serie_sel"],
                    datos["tipo_sel"],
                    datos.get("material_sel", ""),
                    datos["color_sel"],
                    datos.get("tipo_empujador_sel", "OG"),
                    datos.get("tipo_indentacion_sel", "OG"),
                )
                # Limpiar mensaje de carga
                label_generando.config(text="")
                # Cerrar popup
                cerrar_loading_popup()

            except Exception:

                def show_error():
                    messagebox.showerror("Error", "Error al crear gráfico")

                show_error()
                cerrar_loading_popup()

        # Crear popup de loading
        try:
            loading_popup, prog = show_loading_popup(root)
            # Crear hilo con nombre para mejor control
            worker_thread = threading.Thread(
                target=worker, daemon=True, name="CalculoBandaWorker"
            )
            worker_thread.start()
        except Exception:

            def show_error():
                messagebox.showerror(
                    "Error", "Error al mostrar ventana de carga"
                )

            show_error()

    def resetear_formulario():
        combo_series.set("")
        combo_color.set("")
        combo_tipo.set("")
        entry_altura_modulo.config(state="normal")
        entry_altura_modulo.delete(0, tk.END)
        entry_altura_modulo.insert(tk.END, "30")
        entry_altura_modulo.config(state="readonly")

        entry_grosor_pasador.config(state="normal")
        entry_grosor_pasador.delete(0, tk.END)
        entry_grosor_pasador.insert(0, "0")
        entry_grosor_pasador.config(state="readonly")

        vars_check["check_empujadores"].set(False)
        vars_check["check_indentacion"].set(False)
        vars_check["check_desglose"].set(False)
        vars_check["check_redondear_arriba"].set(False)

        entry_largo_banda.delete(0, tk.END)
        entry_largo_banda.insert(tk.END, "27.000")

        text_area_esquema.delete("1.0", tk.END)
        text_area_esquema.insert(
            tk.END,
            "50,200,200,200,50\n"
            "200,200,200,100\n"
            "100,200,200,200\n"
            "200,200,200,100",
        )

        # Recalcular sumas después de limpiar
        texto = text_area_esquema.get("1.0", "end").strip()
        filas = texto.split("\n")
        resultado = []
        for i, fila in enumerate(filas, start=1):
            if not fila.strip():
                continue
            try:
                nums = list(map(int, fila.split(",")))
                suma = sum(nums)
                resultado.append(f"Fila {i}: {suma} mm")
            except ValueError:
                resultado.append(f"Fila {i}: Error (datos inválidos)")

        text_sumas.delete("1.0", tk.END)
        text_sumas.insert(tk.END, "\n".join(resultado))
        text_sumas.config(state=tk.DISABLED)
        text_sumas.yview_moveto(1.0)

        label_modulos.config(state=tk.NORMAL)
        label_modulos.delete("1.0", tk.END)
        label_modulos.config(state=tk.DISABLED)

        for w in frame_canvas.winfo_children():
            w.destroy()

    # Crear botones en cuadrícula 2x2 con estilos modernos
    btn_calcular = ttk.Button(
        marco_botones,
        text="▶️  Calcular Banda",
        command=calcular_banda,
        style="Success.TButton",
        width=20
    )
    btn_calcular.grid(row=0, column=0, padx=3, pady=3, sticky="ew")

    btn_limpiar = ttk.Button(
        marco_botones,
        text="🗑️  Limpiar Formulario",
        command=resetear_formulario,
        style="Warning.TButton",
        width=20
    )
    btn_limpiar.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

    def guardar_esquema():
        """Guarda el esquema actual en la base de datos"""
        serie_sel = combo_series.get().strip()
        tipo_sel = combo_tipo.get().strip()
        color_sel = combo_color.get().strip()
        material_sel = combo_material.get().strip()

        if not serie_sel or not tipo_sel or not color_sel:
            messagebox.showwarning(
                "Advertencia",
                "Debe seleccionar Serie, Tipo y Color antes de guardar."
            )
            return

        try:
            esquema_array = procesar_entrada_arreglo(
                text_area_esquema.get("1.0", tk.END)
            )
            ancho_banda = float(sum(esquema_array[0]))
            largo_banda = float(entry_largo_banda.get().strip())
            altura_modulo = float(entry_altura_modulo.get())
            grosor_pasador = float(entry_grosor_pasador.get())
        except Exception:
            messagebox.showerror(
                "Error",
                "Error al obtener los valores numéricos del esquema."
            )
            return

        # Construir el nombre sugerido del esquema
        # (mismo formato que tab Detalle)
        ancho_m = ancho_banda / 1000.0

        # Calcular total de filas para el largo
        filas_esquema = len(esquema_array)
        largo_m = (filas_esquema * altura_modulo) / 1000.0

        nombre_sugerido = f"Banda S-{serie_sel} {tipo_sel}"
        if material_sel:
            nombre_sugerido += f" {material_sel}"
        nombre_sugerido += f" {color_sel} de {ancho_m:.2f}m ancho"

        # Agregar info de empujador si está activado
        check_empujadores = vars_check['check_empujadores'].get()
        if check_empujadores:
            tipo_empujador = entry_tipo_empujador.get().strip() or "OG"
            distancia_cm = (filas_esquema * altura_modulo) / 10
            nombre_sugerido += f" {tipo_empujador} c/{distancia_cm:.0f}cm"

        # Agregar info de indentación si está activada
        check_indentacion = vars_check['check_indentacion'].get()
        if check_indentacion:
            tipo_indentacion = entry_tipo_indentacion.get().strip() or "OG"
            nombre_sugerido += f" {tipo_indentacion}"

        nombre_sugerido += f" x {largo_m:.2f}m largo"

        # Obtener datos de módulos del esquema
        texto_esquema = text_area_esquema.get("1.0", tk.END)

        modulos_data = []
        for i, fila in enumerate(esquema_array, 1):
            for j, ancho in enumerate(fila, 1):
                modulos_data.append({
                    'fila': i,
                    'posicion': j,
                    'ancho': ancho
                })

        configuracion_data = {
            'esquema_texto': texto_esquema,
            'check_empujadores': check_empujadores,
            'check_indentacion': check_indentacion,
            'check_desglose': vars_check['check_desglose'].get(),
            'check_redondear_arriba': (
                vars_check['check_redondear_arriba'].get()
            ),
            'tipo_empujador': entry_tipo_empujador.get().strip(),
            'tipo_indentacion': entry_tipo_indentacion.get().strip(),
        }

        dialog = SaveSchemaDialog(
            root,
            serie_sel,
            tipo_sel,
            color_sel,
            ancho_banda,
            largo_banda,
            altura_modulo,
            grosor_pasador,
            modulos_data,
            configuracion_data,
            nombre_sugerido  # Pasar el nombre sugerido
        )
        root.wait_window(dialog)

    def cargar_esquema():
        """Carga un esquema desde la base de datos"""
        dialog = SchemaManagerDialog(root)
        root.wait_window(dialog)

        esquema = dialog.get_resultado()
        if esquema:
            # Cargar los valores en los controles
            combo_series.set(esquema['serie'])
            on_combo_serie_select(
                None,
                combo_series,
                combo_tipo,
                combo_material,
                combo_color,
                vars_check
            )

            combo_tipo.set(esquema['tipo'])
            on_combo_tipo_select(
                None,
                combo_series,
                combo_tipo,
                combo_material,
                combo_color,
                df_unificado
            )

            # Cargar material si está disponible en el esquema
            if 'material' in esquema and esquema['material']:
                combo_material.set(esquema['material'])
                on_combo_material_select(
                    None, combo_series,
                    combo_tipo, combo_material,
                    combo_color, df_unificado
                )

            combo_color.set(esquema['color'])

            entry_largo_banda.delete(0, tk.END)
            entry_largo_banda.insert(0, str(esquema['largo_banda']))

            # Cargar el esquema de texto
            if 'esquema_texto' in esquema['configuracion_data']:
                text_area_esquema.delete("1.0", tk.END)
                text_area_esquema.insert(
                    tk.END,
                    esquema['configuracion_data']['esquema_texto']
                )
                # Recalcular sumas después de cargar
                texto = text_area_esquema.get("1.0", "end").strip()
                filas = texto.split("\n")
                resultado = []
                for i, fila in enumerate(filas, start=1):
                    if not fila.strip():
                        continue
                    try:
                        nums = list(map(int, fila.split(",")))
                        suma = sum(nums)
                        resultado.append(f"Fila {i}: {suma} mm")
                    except ValueError:
                        resultado.append(f"Fila {i}: Error (datos inválidos)")
                text_sumas.config(state=tk.NORMAL)
                text_sumas.delete("1.0", tk.END)
                text_sumas.insert(tk.END, "\n".join(resultado))
                text_sumas.config(state=tk.DISABLED)
                text_sumas.yview_moveto(1.0)

            # Cargar checkboxes
            if 'check_empujadores' in esquema['configuracion_data']:
                vars_check['check_empujadores'].set(
                    esquema['configuracion_data']['check_empujadores']
                )
            if 'check_indentacion' in esquema['configuracion_data']:
                vars_check['check_indentacion'].set(
                    esquema['configuracion_data']['check_indentacion']
                )
            if 'check_desglose' in esquema['configuracion_data']:
                vars_check['check_desglose'].set(
                    esquema['configuracion_data']['check_desglose']
                )
            if 'check_redondear_arriba' in esquema['configuracion_data']:
                vars_check['check_redondear_arriba'].set(
                    esquema['configuracion_data']['check_redondear_arriba']
                )

            # Cargar tipo de empujador
            if 'tipo_empujador' in esquema['configuracion_data']:
                entry_tipo_empujador.delete(0, tk.END)
                entry_tipo_empujador.insert(
                    0, esquema['configuracion_data']['tipo_empujador']
                )
            else:
                entry_tipo_empujador.delete(0, tk.END)
                entry_tipo_empujador.insert(0, "OG")  # Valor por defecto

            # Cargar tipo de indentación
            if 'tipo_indentacion' in esquema['configuracion_data']:
                entry_tipo_indentacion.delete(0, tk.END)
                entry_tipo_indentacion.insert(
                    0, esquema['configuracion_data']['tipo_indentacion']
                )
            else:
                entry_tipo_indentacion.delete(0, tk.END)
                entry_tipo_indentacion.insert(0, "OG")  # Valor por defecto

            messagebox.showinfo(
                "Éxito",
                f"Esquema '{esquema['name']}' cargado correctamente."
            )

    # Botones de esquemas en grid con estilos modernos
    btn_guardar_esquema = ttk.Button(
        marco_botones,
        text="💾  Guardar Esquema",
        command=guardar_esquema,
        style="Accent.TButton",
        width=20
    )
    btn_guardar_esquema.grid(row=1, column=0, padx=3, pady=3, sticky="ew")

    btn_cargar_esquema = ttk.Button(
        marco_botones,
        text="📂  Cargar Esquema",
        command=cargar_esquema,
        style="Accent.TButton",
        width=20
    )
    btn_cargar_esquema.grid(row=1, column=1, padx=3, pady=3, sticky="ew")


# ---------------------------------------------------------------------
# CONSTRUIR TEXTO RESUMEN
# ---------------------------------------------------------------------


def construir_texto_resumen(
    esquema,
    altura_modulo,
    mm_pasador,
    total_emp,
    total_mod,
    m_izq,
    m_der,
    m_ct,
    m_ei,
    m_ed,
    m_ec,
    check_empujadores,
    check_indentacion,
    check_desglose,
):
    txt_mod = (
        f"Total de Filas de Empujadores: {total_emp}\n"
        f"Total de Filas de Módulos: {total_mod}\n"
        "-----------------\n"
    )
    ancho_m = sum(esquema[0]) / 1000.0 if esquema else 0
    total_filas = total_emp + total_mod

    if ancho_m > 0:
        pasadores_por_var = math.floor(2.5 / ancho_m)
    else:
        pasadores_por_var = 0

    if pasadores_por_var == 0:
        pasadores_req = total_filas + 5
        pasadores_totales = total_filas + 5
    else:
        pasadores_req = total_filas + 5
        pasadores_totales = math.ceil(pasadores_req / pasadores_por_var)

    if not check_empujadores:
        base_tapas = total_filas * 2
    elif check_empujadores and not check_indentacion:
        base_tapas = total_filas * 2
    else:
        base_tapas = (total_filas * 2) - (total_emp * 2)
    tapas_totales = base_tapas + 10

    if check_empujadores:
        txt_mod += "Empujadores:\n"
        todas_medidas = sorted(
            set(m_ei.keys()).union(m_ed.keys()).union(m_ec.keys())
        )
        if check_desglose:
            txt_mod += "(Izquierdo / Central / Derecho):\n"
            for med in todas_medidas:
                iz = m_ei.get(med, 0)
                ce = m_ec.get(med, 0)
                de = m_ed.get(med, 0)
                txt_mod += f"{med} mm: {iz} / {ce} / {de} piezas\n"
        else:
            total_e = m_ei + m_ec + m_ed
            for med, cant in total_e.items():
                txt_mod += f"{med} mm: {cant} piezas\n"
        txt_mod += "-----------------\n"

    if check_desglose:
        txt_mod += "Módulos Laterales (Izq / Der):\n"
        laterales = sorted(set(m_izq.keys()).union(m_der.keys()))
        for med in laterales:
            i_ = m_izq.get(med, 0)
            d_ = m_der.get(med, 0)
            txt_mod += f"{med} mm: {i_} / {d_} piezas\n"
    else:
        txt_mod += "Módulos Laterales Totales:\n"
        mod_totales = m_izq + m_der
        for med, cant in mod_totales.items():
            txt_mod += f"{med} mm: {cant} piezas\n"

    txt_mod += "-----------------\nMódulos Centrales:\n"
    for med, cant in m_ct.items():
        txt_mod += f"{med} mm: {cant} piezas\n"

    txt_mod += (
        "-----------------\n"
        f"Pasadores Necesarios: {pasadores_req} de {mm_pasador}mm "
        "(incl. 5 de obsequio)\n"
        f"Se necesitan: {pasadores_totales} und de varillas (2.5 m)\n"
        f"Tapas: {tapas_totales} (incluye 10 obsequio)\n"
        "-----------------\n"
    )
    return txt_mod


# ---------------------------------------------------------------------
# LLENAR LISTBOX DETALLES
# ---------------------------------------------------------------------


def llenar_listbox_detalles(
    listbox_detalles,
    esquema,
    altura_modulo,
    mm_pasador,
    total_emp,
    total_mod,
    m_izq,
    m_der,
    m_ct,
    m_ei,
    m_ed,
    m_ec,
    check_empujadores,
    check_indentacion,
    check_desglose,
    serie_actual,
    tipo_actual,
    material_actual,
    color_actual,
    tipo_empujador="OG",
    tipo_indentacion="OG",
):
    ancho_m = sum(esquema[0]) / 1000.0 if esquema else 0
    total_filas = total_emp + total_mod
    largo_m = (total_filas * altura_modulo) / 1000.0

    # Construir texto base con todos los datos
    texto_banda = f"Banda S-{serie_actual} {tipo_actual}"
    if material_actual:
        texto_banda += f" {material_actual}"
    texto_banda += f" {color_actual} de {ancho_m:.2f}m ancho"

    # Si hay empujadores, agregar información de
    # distancia con el tipo personalizado
    if check_empujadores and total_emp > 0:
        # Cálcular distancia entre empujadores en cm
        filas_esquema = len(esquema)
        if filas_esquema > 0:
            # Distancia = (filas entre empujadores) *
            # altura_modulo / 10 para convertir a cm
            distancia_cm = (filas_esquema * altura_modulo) / 10
            texto_banda += f" {tipo_empujador} c/{distancia_cm:.0f}cm"

    # Si hay indentación, agregar información después del empujador
    if check_indentacion:
        texto_banda += f" {tipo_indentacion}"

    texto_banda += f" x {largo_m:.2f}m largo"

    listbox_detalles.insert(tk.END, texto_banda)
    listbox_detalles.insert(tk.END, f"Filas de Empujadores: {total_emp}")
    listbox_detalles.insert(tk.END, f"Filas de Módulos: {total_mod}")
    listbox_detalles.insert(tk.END, f"Total de Filas: {total_filas}")
    listbox_detalles.insert(tk.END, "----------------------------------")

    if check_empujadores:
        listbox_detalles.insert(tk.END, "==== EMPUJADORES ====")
        todas_e = sorted(
            set(m_ei.keys()).union(m_ec.keys()).union(m_ed.keys())
        )
        for med in todas_e:
            iz = m_ei.get(med, 0)
            ce = m_ec.get(med, 0)
            de = m_ed.get(med, 0)
            if check_desglose:
                if iz > 0:
                    listbox_detalles.insert(
                        tk.END, f"{med} mm: {iz} piezas izq"
                    )
                if ce > 0:
                    listbox_detalles.insert(
                        tk.END, f"{med} mm: {ce} piezas cent"
                    )
                if de > 0:
                    listbox_detalles.insert(
                        tk.END, f"{med} mm: {de} piezas der"
                    )
            else:
                total_emp_ = iz + ce + de
                if total_emp_ > 0:
                    listbox_detalles.insert(
                        tk.END, f"{med} mm: {total_emp_} piezas"
                    )
        listbox_detalles.insert(tk.END, "----------------------------------")

    listbox_detalles.insert(tk.END, "\n\n==== MÓDULOS LATERALES ====")
    if check_desglose:
        all_lat = sorted(set(m_izq.keys()).union(m_der.keys()))
        for med in all_lat:
            i_ = m_izq.get(med, 0)
            d_ = m_der.get(med, 0)
            if i_ > 0:
                listbox_detalles.insert(tk.END, f"{med} mm: {i_} piezas izq")
            if d_ > 0:
                listbox_detalles.insert(tk.END, f"{med} mm: {d_} piezas der")
    else:
        comb = m_izq + m_der
        for med, cant in comb.items():
            if cant > 0:
                listbox_detalles.insert(
                    tk.END, f"{med} mm: {cant} piezas totales"
                )

    listbox_detalles.insert(tk.END, "----------------------------------")
    listbox_detalles.insert(tk.END, "--------- MÓDULOS CENTRALES ----------")
    for med, cant in m_ct.items():
        if cant > 0:
            listbox_detalles.insert(tk.END, f"{med} mm: {cant} piezas")
    listbox_detalles.insert(tk.END, "----------------------------------")

    if ancho_m > 0:
        pasadores_por_var = math.floor(2.5 / ancho_m)
    else:
        pasadores_por_var = 0

    if pasadores_por_var == 0:
        pasadores_req = total_filas + 5
        pasadores_totales = total_filas + 5
    else:
        pasadores_req = total_filas + 5
        pasadores_totales = math.ceil(pasadores_req / pasadores_por_var)

    if not check_empujadores:
        base_tapas = total_filas * 2
    elif check_empujadores and not check_indentacion:
        base_tapas = total_filas * 2
    else:
        base_tapas = (total_filas * 2) - (total_emp * 2)
    tapas_totales = base_tapas + 10

    listbox_detalles.insert(
        tk.END,
        (
            f"Pasadores Necesarios: {pasadores_req} und de {mm_pasador}mm "
            f"por {ancho_m:.2f} m"
        ),
    )
    listbox_detalles.insert(
        tk.END,
        (
            f"Se necesitan: {pasadores_totales} und de varillas "
            "(2.5 m c/u)"
        ),
    )
    listbox_detalles.insert(
        tk.END, f"Tapas Totales: {tapas_totales} (incluye 10 obsequio)"
    )


# ---------------------------------------------------------------------
# COPIAR SELECCIÓN DETALLES
# ---------------------------------------------------------------------


def copiar_seleccion_detalles(listbox_detalles):
    sel = listbox_detalles.curselection()
    if not sel:
        messagebox.showwarning("Advertencia", "No hay texto seleccionado.")
        return
    texto_copiado = "\n".join(listbox_detalles.get(i) for i in sel)
    listbox_detalles.clipboard_clear()
    listbox_detalles.clipboard_append(texto_copiado)
    listbox_detalles.update()

# ---------------------------------------------------------------------
# MOSTRAR MENÚ CONTEXTUAL
# ---------------------------------------------------------------------


def mostrar_menu(event, listbox_detalles, menu_copiar):
    if not listbox_detalles.curselection():
        listbox_detalles.selection_clear(0, tk.END)
        idx = listbox_detalles.nearest(event.y)
        if idx >= 0:
            listbox_detalles.selection_set(idx)
    menu_copiar.post(event.x_root, event.y_root)
