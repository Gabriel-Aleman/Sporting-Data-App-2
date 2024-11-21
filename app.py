from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

# Crear la aplicación Dash
app = Dash(__name__)

# Crear un DataFrame de ejemplo
df = pd.DataFrame({
    "Años": [2020, 2021, 2022, 2023, 2024],
    "Ventas": [100, 150, 200, 250, 300]
})

# Crear un gráfico de líneas con Plotly
fig = px.line(df, x="Años", y="Ventas", title="Ventas Anuales")

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Gráfico de Ventas Anuales"),
    dcc.Graph(figure=fig)  # Mostrar el gráfico
])

# Ejecutar el servidor
if __name__ == "__main__":
    app.run_server(debug=True)

