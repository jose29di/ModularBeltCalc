import json
import sqlite3
from datetime import datetime


class BandDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Obtener la ruta del ejecutable o del script
            import os
            import sys
            if getattr(sys, 'frozen', False):
                # Ejecutable: usar carpeta donde está el .exe
                base_path = os.path.dirname(sys.executable)
            else:
                # Desarrollo: usar carpeta actual
                base_path = os.path.abspath(".")
            db_path = os.path.join(base_path, "band_schemas.db")
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS band_schemas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                cliente TEXT,
                description TEXT,
                ancho_banda REAL,
                largo_banda REAL,
                serie TEXT,
                tipo TEXT,
                color TEXT,
                altura_modulo REAL,
                grosor_pasador REAL,
                modulos_data TEXT,
                configuracion_data TEXT,
                fecha_creacion TEXT,
                fecha_modificacion TEXT
            )
        ''')

        # Agregar columna cliente si no existe (para bases de datos existentes)
        try:
            cursor.execute('ALTER TABLE band_schemas ADD COLUMN cliente TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            # La columna ya existe
            pass

        conn.commit()
        conn.close()

    def generar_nombre_sugerido(self, serie, tipo, ancho_banda, largo_banda):
        """Genera un nombre sugerido basado en la configuración"""
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        return f"Banda_{serie}_{tipo}_{ancho_banda}mm_L{largo_banda}m_{fecha}"

    def guardar_esquema(self, name, cliente, description, ancho_banda,
                        largo_banda, serie, tipo, color, altura_modulo,
                        grosor_pasador, modulos_data, configuracion_data):
        """Guarda un nuevo esquema de banda"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fecha_actual = datetime.now().isoformat()

        try:
            cursor.execute('''
                INSERT INTO band_schemas
                (name, cliente, description, ancho_banda, largo_banda, serie,
                 tipo, color, altura_modulo, grosor_pasador, modulos_data,
                 configuracion_data, fecha_creacion, fecha_modificacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, cliente, description, ancho_banda, largo_banda, serie,
                  tipo, color, altura_modulo, grosor_pasador,
                  json.dumps(modulos_data),
                  json.dumps(configuracion_data),
                  fecha_actual, fecha_actual))

            conn.commit()
            return True, "Esquema guardado exitosamente"
        except sqlite3.IntegrityError:
            return False, "Ya existe un esquema con ese nombre"
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"
        finally:
            conn.close()

    def actualizar_esquema(self, id, name, cliente, description, ancho_banda,
                           largo_banda, serie, tipo, color, altura_modulo,
                           grosor_pasador, modulos_data, configuracion_data):
        """Actualiza un esquema existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fecha_actual = datetime.now().isoformat()

        try:
            cursor.execute('''
                UPDATE band_schemas
                SET name=?, cliente=?, description=?, ancho_banda=?,
                    largo_banda=?, serie=?, tipo=?, color=?,
                    altura_modulo=?, grosor_pasador=?, modulos_data=?,
                    configuracion_data=?, fecha_modificacion=?
                WHERE id=?
            ''', (name, cliente, description, ancho_banda, largo_banda,
                  serie, tipo, color, altura_modulo, grosor_pasador,
                  json.dumps(modulos_data),
                  json.dumps(configuracion_data),
                  fecha_actual, id))

            conn.commit()
            return True, "Esquema actualizado exitosamente"
        except sqlite3.IntegrityError:
            return False, "Ya existe un esquema con ese nombre"
        except Exception as e:
            return False, f"Error al actualizar: {str(e)}"
        finally:
            conn.close()

    def obtener_esquemas(self):
        """Obtiene todos los esquemas guardados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM band_schemas '
                       'ORDER BY fecha_modificacion DESC')
        rows = cursor.fetchall()

        esquemas = []
        for row in rows:
            esquemas.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'ancho_banda': row[3],
                'largo_banda': row[4],
                'serie': row[5],
                'tipo': row[6],
                'color': row[7],
                'altura_modulo': row[8],
                'grosor_pasador': row[9],
                'modulos_data': json.loads(row[10]) if row[10] else [],
                'configuracion_data': json.loads(row[11]) if row[11] else {},
                'fecha_creacion': row[12],
                'fecha_modificacion': row[13],
                'cliente': row[14] if len(row) > 14 else None
            })

        conn.close()
        return esquemas

    def obtener_esquema_por_id(self, id):
        """Obtiene un esquema específico por ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM band_schemas WHERE id=?', (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            esquema = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'ancho_banda': row[3],
                'largo_banda': row[4],
                'serie': row[5],
                'tipo': row[6],
                'color': row[7],
                'altura_modulo': row[8],
                'grosor_pasador': row[9],
                'modulos_data': json.loads(row[10]) if row[10] else [],
                'configuracion_data': json.loads(row[11]) if row[11] else {},
                'fecha_creacion': row[12],
                'fecha_modificacion': row[13],
                'cliente': row[14] if len(row) > 14 else None
            }
            return esquema
        return None

    def eliminar_esquema(self, id):
        """Elimina un esquema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM band_schemas WHERE id=?', (id,))
            conn.commit()
            return True, "Esquema eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"
        finally:
            conn.close()

    def buscar_esquemas(self, termino):
        """Busca esquemas por nombre, cliente o descripción"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM band_schemas
            WHERE name LIKE ? OR cliente LIKE ? OR description LIKE ?
            ORDER BY fecha_modificacion DESC
        ''', (f'%{termino}%', f'%{termino}%', f'%{termino}%'))

        rows = cursor.fetchall()
        esquemas = []
        for row in rows:
            esquemas.append({
                'id': row[0],
                'name': row[1],
                'cliente': row[2] if len(row) > 2 else '',
                'description': row[3] if len(row) > 3 else row[2],
                'ancho_banda': row[4] if len(row) > 4 else row[3],
                'largo_banda': row[5] if len(row) > 5 else row[4],
                'serie': row[6] if len(row) > 6 else row[5],
                'tipo': row[7] if len(row) > 7 else row[6],
                'color': row[8] if len(row) > 8 else row[7],
                'altura_modulo': row[9] if len(row) > 9 else row[8],
                'grosor_pasador': row[10] if len(row) > 10 else row[9],
                'modulos_data': (json.loads(row[11])
                                 if len(row) > 11 and row[11]
                                 else (json.loads(row[10])
                                       if row[10] else [])),
                'configuracion_data': (json.loads(row[12])
                                       if len(row) > 12 and row[12]
                                       else (json.loads(row[11])
                                             if len(row) > 11 and row[11]
                                             else {})),
                'fecha_creacion': (row[13] if len(row) > 13
                                   else (row[12] if len(row) > 12 else '')),
                'fecha_modificacion': (row[14] if len(row) > 14
                                       else (row[13] if len(row) > 13
                                             else ''))
            })

        conn.close()
        return esquemas
