from flask import Flask, render_template, request
from scipy.optimize import linprog
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    try:
        # Validar si los datos están presentes en la solicitud
        if not request.form:
            raise ValueError("Formulario vacío. Verifica los datos ingresados.")

        # Obtener si el problema es de minimización o maximización
        problema = request.form.get('problema', 'maximizar')

        # Obtener los datos del formulario
        n = int(request.form.get('variables', 0))
        m = int(request.form.get('constraints', 0))

        if n <= 0 or m <= 0:
            raise ValueError("El número de variables o restricciones debe ser mayor que cero.")

        # Obtener los coeficientes de la función objetivo
        c = [float(request.form[f'objective_{i+1}']) for i in range(n)]

        # Convertir a minimización si el problema es de maximización
        if problema == 'maximizar':
            c = [-ci for ci in c]

        # Obtener restricciones
        A_ub = []
        b_ub = []
        A_eq = []
        b_eq = []

        for i in range(m):
            # Coeficientes de la restricción
            coef = [float(request.form[f'constraint_{i+1}_{j+1}']) for j in range(n)]
            tipo = request.form[f'type_{i+1}']  # Tipo de la restricción (<, >, =)
            b_value = float(request.form[f'limit_{i+1}'])

            if tipo == '<':
                A_ub.append(coef)
                b_ub.append(b_value)
            elif tipo == '>':
                A_ub.append([-ci for ci in coef])
                b_ub.append(-b_value)
            elif tipo == '=':
                A_eq.append(coef)
                b_eq.append(b_value)
            else:
                raise ValueError("Tipo de restricción no válido.")

        # Resolver el problema de programación lineal
        result = linprog(
            c,
            A_ub=np.array(A_ub) if A_ub else None,
            b_ub=np.array(b_ub) if b_ub else None,
            A_eq=np.array(A_eq) if A_eq else None,
            b_eq=np.array(b_eq) if b_eq else None,
            method='highs'
        )

        # Validar si el solver encontró una solución factible
        if result.success:
            # Ajustar signo del resultado si era maximización
            valor_optimo = -result.fun if problema == 'maximizar' else result.fun
            solucion = {
                'valor_optimo': round(valor_optimo, 2),
                'variables': [round(x, 2) for x in result.x]
            }
            return render_template('result.html', solucion=solucion, problema=problema)
        else:
            return render_template('error.html', mensaje="No se pudo encontrar una solución factible. Por favor, revisa las restricciones.")

    except Exception as e:
        return render_template('error.html', mensaje=f"Ocurrió un error: {e}")

if __name__ == '__main__':
    app.run()
    #app.run(debug=True, port=5000)
