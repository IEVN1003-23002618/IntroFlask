import math
from flask import Flask, render_template,request

app = Flask(__name__)

@app.route("/") # decorador o ruta
def index():
    titulo="Pagina de Inicio"
    listado = ['Phyton', 'Flask', 'Jinja2', 'HTML', 'CSS']
    return render_template("index.html", titulo=titulo, listado=listado)




@app.route("/operasbas", methods=["GET", "POST"])
def operasbas():
    n1 = 0
    n2 = 0
    res = 0
    operacion = ""
    if request.method == "POST":
        n1 = request.form.get("n1")
        n2 = request.form.get("n2")
        if request.form.get("operacion") == "sumar":
            if n1 and n2: 
                res = float(n1) + float(n2)
        elif request.form.get("operacion") == "restar":
            if n1 and n2:
                res = float(n1) - float(n2)
        elif request.form.get("operacion") == "multiplicar":
            if n1 and n2:
                res = float(n1) * float(n2)
    return render_template("operasbas.html", n1=n1, n2=n2, res=res)




@app.route("/distancia", methods=["GET", "POST"])
def distancia():
    x1 = ""
    y1 = ""
    x2 = ""
    y2 = ""
    distancia_resultado = None

    if request.method == "POST":
        x1 = request.form.get("x1", "")
        y1 = request.form.get("y1", "")
        x2 = request.form.get("x2", "")
        y2 = request.form.get("y2", "")

       
        if x1 != "" and y1 != "" and x2 != "" and y2 != "":
            try:
                numX1 = float(x1)
                numY1 = float(y1)
                numX2 = float(x2)
                numY2 = float(y2)

                
                operacionX = (numX2 - numX1) ** 2
                operacionY = (numY2 - numY1) ** 2
                distancia_resultado = math.sqrt(operacionX + operacionY)
            except ValueError:
                distancia_resultado = "Error: Ingresa números válidos."

    return render_template(
        "distancia.html",
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        distancia=distancia_resultado
    )


@app.route("/hola") # decorador o ruta
def hola():
    return "<h1> Hola PWA - IEVN1003</h1>"

# CÓMO PASAR PARÁMETROS POR URL

@app.route("/user/<string:nom>") # decorador o ruta
def user(nom):
    return f"<h1> Hola User: {nom} </h1>"

@app.route("/numero/<int:n>") # decorador o ruta
def numero(n):
    return f"Numero: {n}"

@app.route("/user/<int:id>/<string:username>") # decorador o ruta
def user_detail(id, username):
    return f"ID: {id} nombre: {username}"

@app.route("/suma/<float:n1>/<float:n2>") # decorador o ruta
def suma(n1, n2): 
    return f"La suma es: {n1 + n2}"

if __name__ == "__main__":
    app.run(debug=True)