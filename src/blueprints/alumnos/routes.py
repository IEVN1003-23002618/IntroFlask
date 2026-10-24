from flask import Blueprint, jsonify, request
from database import mysql

alumnos_bp = Blueprint(
    'alumnos',
    __name__, 
    url_prefix='/api/alumnos'
)

def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))

@alumnos_bp.route('/', methods=['GET'])
def lista_alumnos():
    try:
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()

        alumnos = []
        for fila in datos:
            alumno = {
                "matricula": fila[0],
                "nombre": fila[1],
                "apaterno": fila[2],
                "amaterno": fila[3],
                "correo": fila[4]
            }
            alumnos.append(alumno)

        return jsonify({
            'alumnos': alumnos,
            'mensaje': "Lista de alumnos",
            'exito': True
        })

    except Exception as ex:
        return jsonify({
            'mensaje': str(ex),
            'exito': False
        }), 500

@alumnos_bp.route("/<string:matricula>", methods=['GET'])
def leer_alumno_bd(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM alumnos WHERE matricula=%s", (matricula,))
        fila = cursor.fetchone()
        
        if fila is None:
            return jsonify({
                'mensaje': 'Alumno no encontrado',
                'exito': False
            }), 404
            
        alumno = fila_a_diccionario(cursor, fila)
        return jsonify({
            'alumno': alumno,
            'exito': True
        }), 200
        
    except Exception as ex:
        return jsonify({
            'mensaje': f'Error al consultar alumno: {str(ex)}',
            'exito': False
        }), 500
        
    finally:
        if cursor is not None:
            cursor.close()

@alumnos_bp.route("/", methods=['POST'])
def registrar_alumno():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400

    campos = ['matricula', 'nombre', 'apaterno', 'amaterno', 'correo']

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
        cursor = mysql.connection.cursor()  # Cambiado 'con' por 'mysql'
        cursor.execute(
            "SELECT matricula FROM alumnos WHERE matricula = %s",
            (datos['matricula'].strip(),)
        )
        if cursor.fetchone() is not None:
            return jsonify({
                'mensaje': 'La matrícula ya existe',
                'exito': False
            }), 409

        cursor.execute(
            """INSERT INTO alumnos (`matricula`, `nombre`, `apellido paterno`, `apellido materno`, `correo`)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                datos['matricula'].strip(),
                datos['nombre'].strip(),
                datos['apaterno'].strip(),
                datos['amaterno'].strip(),
                datos['correo'].strip()
            )
        )

        mysql.connection.commit()  # Cambiado 'con' por 'mysql'

        return jsonify({
            'mensaje': 'Alumno registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        if mysql.connection:  # Cambiado 'con' por 'mysql'
            mysql.connection.rollback()

        return jsonify({
            'mensaje': f'Error al registrar alumno: {str(ex)}',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

@alumnos_bp.route("/<string:matricula>", methods=["PUT"])
def modificar_alumno(matricula):
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
            "SELECT matricula FROM alumnos WHERE matricula = %s",
            (matricula,)
        )
        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                "mensaje": "Alumno no encontrado",
                "exito": False
            }), 404

        sql = """
            UPDATE alumnos
            SET `nombre` = %s,
                `apellido paterno` = %s,
                `apellido materno` = %s,
                `correo` = %s
            WHERE `matricula` = %s
        """

        cursor.execute(sql, (
            nombre.strip(),
            apaterno.strip(),
            amaterno.strip(),
            correo.strip(),
            matricula
        ))

        mysql.connection.commit()

        return jsonify({
            "mensaje": "Alumno modificado correctamente",
            "matricula": matricula,
            "exito": True
        }), 200

    except Exception as ex:
        if mysql.connection:
            mysql.connection.rollback()

        return jsonify({
            "mensaje": f"Error al modificar alumno: {str(ex)}",
            "exito": False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

@alumnos_bp.route("/<string:matricula>", methods=["DELETE"])
def eliminar_alumno(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT matricula FROM alumnos WHERE matricula = %s",
            (matricula,)
        )
        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                "mensaje": "Alumno no encontrado",
                "exito": False
            }), 404

        cursor.execute(
            "DELETE FROM alumnos WHERE matricula = %s",
            (matricula,)
        )

        mysql.connection.commit()

        return jsonify({
            "mensaje": "Alumno eliminado correctamente",
            "exito": True
        }), 200

    except Exception as ex:
        if mysql.connection:
            mysql.connection.rollback()

        return jsonify({
            "mensaje": f"Error al eliminar alumno: {str(ex)}",
            "exito": False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()