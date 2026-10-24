from flask import Blueprint, jsonify, request
from database import mysql

maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)

def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))

# 1. Obtener todos los maestros
@maestros_bp.route('/', methods=['GET'])
def lista_maestros():
    try:
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM maestros"
        cursor.execute(sql)
        datos = cursor.fetchall()

        maestros = []
        for fila in datos:
            maestro = {
                "idmaestro": fila[0],
                "nombre": fila[1],
                "apaterno": fila[2],
                "amaterno": fila[3],
                "correo": fila[4]
            }
            maestros.append(maestro)

        return jsonify({
            'maestros': maestros,
            'mensaje': "Lista de maestros",
            'exito': True
        })

    except Exception as ex:
        return jsonify({
            'mensaje': str(ex),
            'exito': False
        }), 500


# 2. Obtener un maestro por ID
@maestros_bp.route("/<int:idmaestro>", methods=['GET'])
def leer_maestro_bd(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM maestros WHERE idmaestro = %s", (idmaestro,))
        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                'mensaje': 'Maestro no encontrado',
                'exito': False
            }), 404

        maestro = fila_a_diccionario(cursor, fila)
        return jsonify({
            'maestro': maestro,
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': f'Error al consultar maestro: {str(ex)}',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# 3. Registrar un nuevo maestro
@maestros_bp.route("/", methods=['POST'])
def registrar_maestro():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400

    campos = ['nombre', 'apaterno', 'amaterno', 'correo']

    if any(
        campo not in datos
        or not isinstance(datos[campo], str)
        or not datos[campo].strip()
        for campo in campos
    ):
        return jsonify({
            'mensaje': 'Faltan campos obligatorios',
            'exito': False
        }), 400

    cursor = None
    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            """INSERT INTO maestros (`nombre`, `apellido paterno`, `apellido materno`, `correo`)
               VALUES (%s, %s, %s, %s)""",
            (
                datos['nombre'].strip(),
                datos['apaterno'].strip(),
                datos['amaterno'].strip(),
                datos['correo'].strip()
            )
        )

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        if mysql.connection:
            mysql.connection.rollback()

        return jsonify({
            'mensaje': f'Error al registrar maestro: {str(ex)}',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# 4. Modificar un maestro existente
@maestros_bp.route("/<int:idmaestro>", methods=["PUT"])
def modificar_maestro(idmaestro):
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({
            "mensaje": "No se recibieron datos para modificar",
            "exito": False
        }), 400

    nombre = datos.get('nombre')
    apaterno = datos.get('apaterno') or datos.get('apellido paterno')
    amaterno = datos.get('amaterno') or datos.get('apellido materno') or ""
    correo = datos.get('correo')

    if not nombre or not apaterno or not correo:
        return jsonify({
            "mensaje": "Nombre, apellido paterno y correo son obligatorios",
            "exito": False
        }), 400

    cursor = None
    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )
        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                "mensaje": "Maestro no encontrado",
                "exito": False
            }), 404

        sql = """
            UPDATE maestros
            SET `nombre` = %s,
                `apellido paterno` = %s,
                `apellido materno` = %s,
                `correo` = %s
            WHERE `idmaestro` = %s
        """

        cursor.execute(sql, (
            nombre.strip(),
            apaterno.strip(),
            amaterno.strip(),
            correo.strip(),
            idmaestro
        ))

        mysql.connection.commit()

        return jsonify({
            "mensaje": "Maestro modificado correctamente",
            "idmaestro": idmaestro,
            "exito": True
        }), 200

    except Exception as ex:
        if mysql.connection:
            mysql.connection.rollback()

        return jsonify({
            "mensaje": f"Error al modificar maestro: {str(ex)}",
            "exito": False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# 5. Eliminar un maestro
@maestros_bp.route("/<int:idmaestro>", methods=["DELETE"])
def eliminar_maestro(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )
        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                "mensaje": "Maestro no encontrado",
                "exito": False
            }), 404

        cursor.execute(
            "DELETE FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )

        mysql.connection.commit()

        return jsonify({
            "mensaje": "Maestro eliminado correctamente",
            "exito": True
        }), 200

    except Exception as ex:
        if mysql.connection:
            mysql.connection.rollback()

        return jsonify({
            "mensaje": f"Error al eliminar maestro: {str(ex)}",
            "exito": False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()