import io
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from tkinter import messagebox


def procesar_entrada_arreglo(texto: str):
    """
    Convierte el texto ingresado (cada fila en
    una línea, valores separados por comas) en
    una lista de listas de enteros.
    """
    try:
        filas = texto.strip().split("\n")
        esquema = []
        for fila in filas:
            nums = list(map(int, fila.split(",")))
            esquema.append(nums)
        return esquema
    except ValueError:
        messagebox.showerror(
            "Error",
            "Formato incorrecto. Usa números separados "
            "por comas en cada línea."
        )
        return None


def generar_esquema_banda_personalizado(
    fig, ax,
    esquema,
    altura_modulo,
    largo_banda,
    check_empujadores,
    check_desglose,
    check_indentacion
):
    """
    Dibuja el esquema de la banda sobre la figura 'fig'
    con eje 'ax'. Devuelve un dict con:
      - 'img_memoria': BytesIO con la imagen
      - 'total_filas_modulos': int
      - 'total_filas_empujadores': int
      - 'modulos_izquierdos': Counter
      - 'modulos_derechos': Counter
      - 'modulos_centrales': Counter
      - 'modulos_empujadores_izquierdos': Counter
      - 'modulos_empujadores_derechos': Counter
      - 'modulos_empujadores_centrales': Counter

    Lógica de checks:
      - 'check_empujadores': si True, la primera fila
        se considera empujador y se pinta en lightblue.
      - 'check_indentacion': si True, los extremos de
        la primera fila empujadora se tratan como
        módulos normales y se pintan en lightgreen.
      - 'check_desglose' se maneja luego (no altera
        los colores aquí, solo el conteo).
    """

    if largo_banda % altura_modulo != 0:
        messagebox.showerror(
            "Error",
            "El largo de la banda debe ser múltiplo "
            "de la altura del módulo."
        )
        return None

    # Limpiar el eje
    ax.clear()

    ancho_banda = max(sum(fila) for fila in esquema)
    filas = largo_banda // altura_modulo

    ax.set_xticks(np.arange(0, ancho_banda + 10, 10), minor=True)
    ax.set_yticks(np.arange(0, largo_banda + 10, 10), minor=True)
    ax.grid(
        which='both',
        linestyle='--',
        linewidth=0.5,
        color='gray',
        alpha=0.3
    )

    total_filas_modulos = 0
    total_filas_empujadores = 0

    mod_izq = Counter()
    mod_der = Counter()
    mod_ct = Counter()

    emp_i = Counter()
    emp_d = Counter()
    emp_c = Counter()

    y_actual = 0
    for fila in range(filas):
        x_actual = 0
        fila_esq = esquema[fila % len(esquema)]
        ancho_fila = sum(fila_esq)

        # Definir si esta fila es empujadora
        es_empujador = (
            check_empujadores and (fila % len(esquema) == 0)
        )

        if es_empujador:
            total_filas_empujadores += 1
        else:
            total_filas_modulos += 1

        for i, ancho_mod in enumerate(fila_esq):
            # Color base para la fila empujadora
            if es_empujador:
                facecolor = "lightblue"
            else:
                facecolor = "white"

            # Sobrescribir si check_indentacion y es extremo
            es_extremo = (i == 0 or i == len(fila_esq) - 1)
            if es_empujador and check_indentacion and es_extremo:
                facecolor = "lightgreen"

            # Dibujar el rectángulo
            rect = plt.Rectangle(
                (x_actual, y_actual),
                ancho_mod,
                altura_modulo,
                edgecolor='blue',
                linewidth=2,
                facecolor=facecolor
            )
            ax.add_patch(rect)

            # Centrar el texto con la medida
            ax.text(
                x_actual + ancho_mod / 2,
                y_actual + altura_modulo / 2,
                f"{ancho_mod}",
                color="gray",
                fontsize=6,
                ha="center",
                va="center",
                alpha=0.7,
                weight="bold"
            )

            # Sumar al contador
            if es_empujador:
                # Con indentacion y es extremo => tratarlo
                # como un módulo normal
                if check_indentacion and es_extremo:
                    if i == 0:
                        mod_izq[ancho_mod] += 1
                    else:
                        mod_der[ancho_mod] += 1
                else:
                    # Empujador normal
                    if i == 0:
                        emp_i[ancho_mod] += 1
                    elif i == len(fila_esq) - 1:
                        emp_d[ancho_mod] += 1
                    else:
                        emp_c[ancho_mod] += 1
            else:
                # Fila normal
                if i == 0:
                    mod_izq[ancho_mod] += 1
                elif i == len(fila_esq) - 1:
                    mod_der[ancho_mod] += 1
                else:
                    mod_ct[ancho_mod] += 1

            x_actual += ancho_mod

        # Rellenar en caso de ancho faltante
        if ancho_fila < ancho_banda:
            rect_faltante = plt.Rectangle(
                (x_actual, y_actual),
                ancho_banda - ancho_fila,
                altura_modulo,
                edgecolor='red',
                linewidth=2,
                facecolor='none',
                hatch='x'
            )
            ax.add_patch(rect_faltante)

        y_actual += altura_modulo

    # Ajustes finales del eje
    ax.set_xlim(0, ancho_banda)
    ax.set_ylim(0, largo_banda)
    ax.set_aspect('equal')
    ax.set_title("Esquema de Banda Modular")
    ax.set_xlabel("Ancho (mm)")
    ax.set_ylabel("Largo (mm)")

    # Guardar a imagen en memoria
    img_memoria = io.BytesIO()
    fig.savefig(img_memoria, format='png')
    img_memoria.seek(0)

    return {
        "img_memoria": img_memoria,
        "total_filas_modulos": total_filas_modulos,
        "total_filas_empujadores": total_filas_empujadores,
        "modulos_izquierdos": mod_izq,
        "modulos_derechos": mod_der,
        "modulos_centrales": mod_ct,
        "modulos_empujadores_izquierdos": emp_i,
        "modulos_empujadores_derechos": emp_d,
        "modulos_empujadores_centrales": emp_c,
    }
