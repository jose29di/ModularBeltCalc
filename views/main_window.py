import math
import tkinter as tk
from tkinter import (
    ttk, messagebox, filedialog, PhotoImage
)
import matplotlib.pyplot as plt

from models.series import series_modulos
from controllers.utils import resource_path
from controllers.generator import (
    generar_esquema_banda_personalizado,
    procesar_entrada_arreglo,
)
from controllers.clipboard import copiar_datos, copiar_imagen
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)

canvas = None
label_modulos = None
img_memoria = None


def run_app() -> None:
    global canvas, label_modulos, img_memoria

    root = tk.Tk()
    root.title("Generador de Esquema & Calculo de Banda Modular")
    root.geometry("960x700")

    # Icono si existe
    root.iconbitmap(resource_path("assets/Module30px.ico"))

    # Estilo de botones
    style = ttk.Style()
    style.theme_use("clam")
    style.layout(
        "Modern.TButton",
        [
            (
                "Button.border",
                {
                    "children": [
                        (
                            "Button.padding",
                            {
                                "children": [
                                    ("Button.label", {"sticky": "nswe"})
                                ]
                            },
                        )
                    ],
                    "sticky": "nswe",
                },
            )
        ],
    )
    style.configure(
        "Modern.TButton",
        font=("Arial", 10, "bold"),
        background="#5DADE2",
        foreground="black",
        padding=10,
        borderwidth=2,
        relief="raised",
    )
    style.map(
        "Modern.TButton",
        background=[("active", "#3498DB")],
        relief=[("pressed", "ridge")],
    )

    def cargar_imagen(ruta: str):
        try:
            return PhotoImage(file=resource_path(ruta))
        except Exception:
            return None

    icon_generar = cargar_imagen("assets/icon_generar.png")
    icon_guardar = cargar_imagen("assets/icon_guardar.png")
    icon_reset = cargar_imagen("assets/icon_reset.png")

    frame_main = ttk.Frame(root, padding=10)
    frame_main.pack(fill=tk.BOTH, expand=True)

    # Sección izquierda
    frame_inputs = ttk.LabelFrame(
        frame_main, text="Parámetros de Entrada", padding=10
    )
    frame_inputs.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    lbl_serie = ttk.Label(
        frame_inputs,
        text="Serie del módulo:",
        font=("Arial", 10, "bold")
    )
    lbl_serie.pack(anchor="w")

    combo_series = ttk.Combobox(
        frame_inputs,
        values=list(series_modulos.keys()),
        state="readonly"
    )
    combo_series.pack()
    combo_series.set("E30")

    lbl_altura = ttk.Label(frame_inputs, text="Altura del módulo (mm):")
    lbl_altura.pack(anchor="w")
    entry_altura_modulo = ttk.Entry(frame_inputs, width=10)
    entry_altura_modulo.pack()
    entry_altura_modulo.insert(0, "30")

    lbl_largo = ttk.Label(frame_inputs, text="Largo de banda (cm):")
    lbl_largo.pack(anchor="w")
    entry_largo_banda = ttk.Entry(frame_inputs, width=10)
    entry_largo_banda.pack()
    entry_largo_banda.insert(0, "27.00")

    # Check unificado: Con empujadores
    check_empujadores = tk.BooleanVar(value=False)
    chk_empujadores = ttk.Checkbutton(
        frame_inputs,
        text="Con empujadores",
        variable=check_empujadores
    )
    chk_empujadores.pack(anchor="w", pady=5)

    # Check: Con indentación
    check_indentacion = tk.BooleanVar(value=False)
    chk_indentacion = ttk.Checkbutton(
        frame_inputs,
        text="Con indentación",
        variable=check_indentacion
    )
    chk_indentacion.pack(anchor="w", pady=5)

    # Check: Desglosar módulos laterales
    check_desglose = tk.BooleanVar(value=False)
    chk_desglose = ttk.Checkbutton(
        frame_inputs,
        text="Desglosar módulos laterales",
        variable=check_desglose
    )
    chk_desglose.pack(anchor="w", pady=5)

    # Text area con suma en tiempo real
    text_area = tk.Text(frame_inputs, height=12, width=30)
    text_area.pack(pady=5)
    text_area.insert(
        tk.END,
        "50,200,200,200,50\n200,200,200,100\n"
        "100,200,200,200\n200,200,200,100"
    )

    def recalcular_sumas_filas(event=None):
        texto = text_area.get("1.0", "end").strip()
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
        label_sumas.config(text="\n".join(resultado))

    label_sumas = ttk.Label(frame_inputs, text="", justify="left")
    label_sumas.pack(pady=5, anchor="w")

    text_area.bind("<KeyRelease>", recalcular_sumas_filas)

    def resetear_formulario():
        combo_series.set("E30")
        entry_altura_modulo.config(state="normal")
        entry_altura_modulo.delete(0, tk.END)
        entry_altura_modulo.insert(0, "30")
        entry_altura_modulo.config(state="readonly")

        entry_largo_banda.delete(0, tk.END)
        entry_largo_banda.insert(0, "27.000")

        check_empujadores.set(False)
        check_indentacion.set(False)
        check_desglose.set(False)

        text_area.delete("1.0", tk.END)
        text_area.insert(
            tk.END,
            "50,200,200,200,50\n200,200,200,100\n"
            "100,200,200,200\n200,200,200,100"
        )
        label_sumas.config(text="")
        label_modulos.config(text="")
        for widget in frame_canvas.winfo_children():
            widget.destroy()

    def on_combo_change(event):
        serie = combo_series.get()
        if serie in series_modulos:
            if serie == "Otras":
                entry_altura_modulo.config(state="normal")
                entry_altura_modulo.delete(0, tk.END)
            else:
                entry_altura_modulo.config(state="normal")
                entry_altura_modulo.delete(0, tk.END)
                alt = series_modulos[serie]["altura"]
                entry_altura_modulo.insert(0, str(alt))
                entry_altura_modulo.config(state="readonly")

            if series_modulos[serie]["Lateral"] == "S":
                check_desglose.set(True)
            else:
                check_desglose.set(False)

    combo_series.bind("<<ComboboxSelected>>", on_combo_change)

    frame_botones = ttk.Frame(frame_inputs)
    frame_botones.pack(pady=5, fill="x")

    fig, ax = plt.subplots(figsize=(6, 4))
    label_generando = None

    def ejecutar_script():
        global img_memoria, canvas
        try:
            alt_mod = int(entry_altura_modulo.get())
            largo_mm = round(float(entry_largo_banda.get()) * 10)
            txt = text_area.get("1.0", tk.END)
            esquema = procesar_entrada_arreglo(txt)
            if esquema is None:
                return

            label_generando.config(text="Generando Cálculos y esquema...")
            label_generando.update_idletasks()

            result = generar_esquema_banda_personalizado(
                fig, ax,
                esquema,
                alt_mod,
                largo_mm,
                check_empujadores.get(),
                check_desglose.get(),
                check_indentacion.get()
            )
            label_generando.config(text="")

            if not result:
                return

            global img_memoria
            img_memoria = result["img_memoria"]
            total_mod = result["total_filas_modulos"]
            total_emp = result["total_filas_empujadores"]

            # Recuperamos los Counters de módulos
            m_izq = result["modulos_izquieros"] \
                if "modulos_izquieros" in result else \
                result["modulos_izquierdos"]
            m_der = result["modulos_derechos"]
            m_ct = result["modulos_centrales"]

            m_ei = result["modulos_empujadores_izquierdos"]
            m_ed = result["modulos_empujadores_derechos"]
            m_ec = result["modulos_empujadores_centrales"]

            for widget in frame_canvas.winfo_children():
                widget.destroy()

            canvas_local = FigureCanvasTkAgg(fig, master=frame_canvas)
            canvas_widget = canvas_local.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            canvas_local.draw()

            canvas = canvas_local

            tb_frame = ttk.Frame(frame_canvas)
            tb_frame.pack(fill=tk.X)
            tb = NavigationToolbar2Tk(canvas_local, tb_frame)
            tb.update()

            btn_copiar_imagen.config(state=tk.NORMAL)

            txt_mod = (
                f"Total de Filas de Empujadores: {total_emp}\n"
                f"Total de Filas de Módulos: {total_mod}\n"
                "-----------------\n"
            )

            # Calcular ancho y largo total (m)
            ancho_m = sum(esquema[0]) / 1000.0
            total_filas = total_emp + total_mod
            largo_m = (total_filas * alt_mod) / 1000.0

            # ======================
            # (NUEVO) PASADORES
            # ======================
            # 1) Cuántos pasadores se pueden sacar de 1 varilla (2.5 m)
            if ancho_m > 0:
                pasadores_por_var = math.floor(2.5 / ancho_m)
            else:
                pasadores_por_var = 0

            # Cada fila necesita 1 pasador => total_filas
            # Convertimos la cantidad de varillas
            if pasadores_por_var == 0:
                # Si ancho > 2.5 => 1 varilla por pasador
                pasadores_totales = total_filas + 5
                pasadores_req = total_filas + 5
            else:
                pasadores_req = total_filas + 5
                pasadores_totales = (
                    math.ceil(total_filas / pasadores_por_var)
                )

            # ======================
            # (NUEVO) TAPAS
            # ======================
            # Sin empujador => base = total_filas * 2
            # Empujador sin indent => base = total_filas * 2
            # Empujador con indent => base = 2
            # Se suman 10 obsequio
            if not check_empujadores.get():
                base_tapas = total_filas * 2
            elif check_empujadores.get() and not check_indentacion.get():
                base_tapas = total_filas * 2
            else:
                # Empujador + indentación
                base_tapas = ((total_filas * 2) - total_emp*2)

            tapas_totales = base_tapas + 10

            # Empujadores en Resumen
            if check_empujadores.get():
                txt_mod += "Empujadores:\n"
                all_m = sorted(
                    set(m_ei.keys()).union(m_ed.keys()).union(m_ec.keys())
                )
                if check_desglose.get():
                    txt_mod += "(Izquierdo / Central / Derecho):\n"
                    for med in all_m:
                        iz = m_ei.get(med, 0)
                        ce = m_ec.get(med, 0)
                        de = m_ed.get(med, 0)
                        txt_mod += f"{med} mm: {iz} / {ce} / {de} piezas\n"
                else:
                    total_e = m_ei + m_ec + m_ed
                    for med, cant in total_e.items():
                        txt_mod += f"{med} mm: {cant} piezas\n"
                txt_mod += "-----------------\n"

            # Módulos laterales
            if check_desglose.get():
                txt_mod += "Módulos Laterales (Izq / Der):\n"
                all_l = sorted(
                    set(m_izq.keys()).union(m_der.keys())
                )
                for med in all_l:
                    i_ = m_izq.get(med, 0)
                    d_ = m_der.get(med, 0)
                    txt_mod += f"{med} mm: {i_} / {d_} piezas\n"
            else:
                txt_mod += "Módulos Laterales Totales:\n"
                mod_tot = m_izq + m_der
                for med, cant in mod_tot.items():
                    txt_mod += f"{med} mm: {cant} piezas\n"

            txt_mod += "-----------------\nMódulos Centrales:\n"
            for med, cant in m_ct.items():
                txt_mod += f"{med} mm: {cant} piezas\n"
            txt_mod += "-----------------\n"

            # (NUEVO) Pasadores y Tapas en Resumen
            txt_mod += (
                f"Pasadores Necesarios: {pasadores_req}  de {ancho_m} cm"
                " (incluyendo 5 de obsequio)\n"
                f"Se necesitan: {pasadores_totales} varillas (2.5 m c/u)\n"
                f"Tapas: {tapas_totales} (incluye 10 obsequio )\n"
                "-----------------\n"
            )

            label_modulos.config(text=txt_mod)

            # ===== DETALLES =====
            listbox_detalles.delete(0, tk.END)

            listbox_detalles.insert(
                tk.END,
                f"Banda S-{combo_series.get()} de {ancho_m:.2f} m "
                f"ancho x {largo_m:.2f} m largo"
            )
            listbox_detalles.insert(
                tk.END, f"Filas de Empujadores: {total_emp}"
            )
            listbox_detalles.insert(
                tk.END, f"Filas de Módulos: {total_mod}"
            )
            listbox_detalles.insert(
                tk.END, f"Total de Filas: {total_filas}"
            )
            listbox_detalles.insert(
                tk.END, "----------------------------------"
            )

            if check_empujadores.get():
                listbox_detalles.insert(tk.END, "==== EMPUJADORES ====")
                all_m2 = sorted(
                    set(m_ei.keys()).union(m_ed.keys()).union(m_ec.keys())
                )
                for med in all_m2:
                    iz = m_ei.get(med, 0)
                    ce = m_ec.get(med, 0)
                    de = m_ed.get(med, 0)
                    if check_desglose.get():
                        if iz > 0:
                            listbox_detalles.insert(
                                tk.END,
                                f"{med} mm: {iz} piezas izq"
                            )
                        if ce > 0:
                            listbox_detalles.insert(
                                tk.END,
                                f"{med} mm: {ce} piezas cent"
                            )
                        if de > 0:
                            listbox_detalles.insert(
                                tk.END,
                                f"{med} mm: {de} piezas der"
                            )
                    else:
                        total_emp_ = iz + ce + de
                        if total_emp_ > 0:
                            listbox_detalles.insert(
                                tk.END,
                                f"{med} mm: {total_emp_} piezas"
                            )
                listbox_detalles.insert(
                    tk.END, "----------------------------------"
                )

            listbox_detalles.insert(
                tk.END, "\n\n==== MÓDULOS LATERALES ===="
            )
            if check_desglose.get():
                all_l2 = sorted(
                    set(m_izq.keys()).union(m_der.keys())
                )
                for med in all_l2:
                    i_ = m_izq.get(med, 0)
                    d_ = m_der.get(med, 0)
                    if i_ > 0:
                        listbox_detalles.insert(
                            tk.END,
                            f"{med} mm: {i_} piezas izq"
                        )
                    if d_ > 0:
                        listbox_detalles.insert(
                            tk.END,
                            f"{med} mm: {d_} piezas der"
                        )
            else:
                comb = m_izq + m_der
                for med, cant in comb.items():
                    if cant > 0:
                        listbox_detalles.insert(
                            tk.END,
                            f"{med} mm: {cant} piezas totales"
                        )
            listbox_detalles.insert(
                tk.END, "----------------------------------"
            )

            listbox_detalles.insert(
                tk.END, "--------- MÓDULOS CT ----------"
            )
            for med, cant in m_ct.items():
                if cant > 0:
                    listbox_detalles.insert(
                        tk.END, f"{med} mm: {cant} piezas"
                    )
            listbox_detalles.insert(
                tk.END, "----------------------------------"
            )

            # (NUEVO) Pasadores y Tapas en Detalles
            listbox_detalles.insert(
                tk.END,
                f"Pasadores Necesarios: {pasadores_req} de {ancho_m} cm\n"
                f"Se necesitan: {pasadores_totales} varillas (2.5 m c/u) "
                f"(obsequian 5 de {ancho_m} incluidos)\n"
            )
            listbox_detalles.insert(
                tk.END,
                f"Tapas Totales: {tapas_totales} "
                "(ya incluye obsequio 10)"
            )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Por favor, ingresa valores numéricos válidos "
                "para el largo en cm."
            )

    btn_calc = ttk.Button(
        frame_botones,
        text="Calcular Banda",
        command=ejecutar_script,
        style="Modern.TButton",
        image=icon_generar,
        compound="left"
    )
    btn_calc.pack(fill="x", padx=5, pady=5)

    frame_fila1 = ttk.Frame(frame_botones)
    frame_fila1.pack(fill="x", pady=2)

    def on_copiar_imagen():
        copiar_imagen(img_memoria)

    btn_reset = ttk.Button(
        frame_fila1,
        text="Limpiar Datos",
        command=resetear_formulario,
        style="Modern.TButton",
        image=icon_reset,
        compound="left"
    )
    btn_reset.pack(side="left", expand=True, fill="x", padx=5)

    btn_copiar_imagen = ttk.Button(
        frame_fila1,
        text="Copiar Imagen",
        command=on_copiar_imagen,
        style="Modern.TButton",
        state=tk.DISABLED
    )
    btn_copiar_imagen.pack(side="left", expand=True, fill="x", padx=5)

    frame_fila2 = ttk.Frame(frame_botones)
    frame_fila2.pack(fill="x", pady=2)

    def on_copiar_datos():
        copiar_datos(label_modulos.cget("text"))

    btn_copiar_datos = ttk.Button(
        frame_fila2,
        text="Copiar Datos",
        command=on_copiar_datos,
        style="Modern.TButton"
    )
    btn_copiar_datos.pack(side="left", expand=True, fill="x", padx=5)

    def guardar_imagen():
        global canvas
        if not canvas:
            messagebox.showerror("Error", "No hay imagen generada.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All Files", "*.*")]
        )
        if file_path and canvas.figure:
            canvas.figure.savefig(file_path, dpi=300)
            messagebox.showinfo("Guardado", "Imagen guardada.")

    btn_guardar = ttk.Button(
        frame_fila2,
        text="Guardar Imagen",
        command=guardar_imagen,
        style="Modern.TButton",
        image=icon_guardar,
        compound="left"
    )
    btn_guardar.pack(side="left", expand=True, fill="x", padx=5)

    frame_datos = ttk.LabelFrame(
        frame_main, text="Detalles de los Módulos", padding=10
    )
    frame_datos.pack(
        side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
    )

    notebook = ttk.Notebook(frame_datos)
    notebook.pack(fill=tk.BOTH, expand=True)

    # TAB 1: Resumen
    tab_resumen = ttk.Frame(notebook)
    notebook.add(tab_resumen, text="Resumen")

    frame_resumen = ttk.Frame(tab_resumen)
    frame_resumen.pack(fill=tk.BOTH, expand=True)

    label_generando = ttk.Label(
        frame_resumen,
        text="",
        font=("Arial", 10, "italic"),
        foreground="red"
    )
    label_generando.pack()

    global label_modulos
    label_modulos = ttk.Label(
        frame_resumen,
        text="",
        justify="left",
        font=("Arial", 10),
        anchor="nw"
    )
    label_modulos.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    frame_canvas = ttk.Frame(frame_resumen, padding=10)
    frame_canvas.pack(fill=tk.BOTH, expand=True)

    # TAB 2: Detalles de Módulos
    tab_detalles = ttk.Frame(notebook)
    notebook.add(tab_detalles, text="Detalles de Módulos")

    frame_lista_detalles = ttk.Frame(tab_detalles)
    frame_lista_detalles.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame_lista_detalles, orient=tk.VERTICAL)
    listbox_detalles = tk.Listbox(
        frame_lista_detalles,
        font=("Arial", 10),
        yscrollcommand=scrollbar.set,
        selectmode=tk.EXTENDED
    )
    listbox_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox_detalles.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    menu_copiar = tk.Menu(root, tearoff=0)

    def copiar_seleccion():
        sel = listbox_detalles.curselection()
        if not sel:
            messagebox.showwarning(
                "Advertencia", "No hay texto seleccionado."
            )
            return
        texto_copiado = "\n".join(listbox_detalles.get(i) for i in sel)
        root.clipboard_clear()
        root.clipboard_append(texto_copiado)
        root.update()

    menu_copiar.add_command(label="Copiar", command=copiar_seleccion)

    def copiar_con_teclado(event=None):
        copiar_seleccion()

    listbox_detalles.bind("<Control-c>", copiar_con_teclado)

    def mostrar_menu(event):
        if not listbox_detalles.curselection():
            listbox_detalles.selection_clear(0, tk.END)
            idx = listbox_detalles.nearest(event.y)
            if idx >= 0:
                listbox_detalles.selection_set(idx)
        menu_copiar.post(event.x_root, event.y_root)

    listbox_detalles.bind("<Button-3>", mostrar_menu)

    root.mainloop()
