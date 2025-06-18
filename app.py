import pandas as pd
from flask import Flask, render_template_string
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from request import update_csv_with_weather_data

update_csv_with_weather_data()

# Чтение CSV-файла с климатическими данными
df = pd.read_csv("mock_climate_data.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Создание Flask-приложения
server = Flask(__name__)

# Создание Dash-приложения, встроенного во Flask
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Макет страницы Dash
app.layout = html.Div([
    html.H1("🌦 Климатический дашборд", style={"textAlign": "center"}),

    html.Label("Выберите город:"),
    dcc.Dropdown(
        options=[{"label": city, "value": city} for city in df["city"].unique()],
        value=df["city"].unique()[0],
        id="city-dropdown"
    ),

    html.Div(id="graphs-output")
])

# Обновление графика при выборе города
@app.callback(
    Output("graphs-output", "children"),
    Input("city-dropdown", "value")
)
def update_graphs(selected_city):
    filtered_df = df[df["city"] == selected_city]

    # Температура
    fig_temp = px.line(
        filtered_df,
        x="timestamp",
        y="temperature",
        title="🌡 Температура (°C)",
        labels={"timestamp": "Дата и время", "temperature": "Температура (°C)"},
        markers=True,
        line_shape="spline"
    )
    fig_temp.update_traces(line=dict(color='orangered'))

    # Ощущаемая температура
    fig_feels = px.line(
        filtered_df,
        x="timestamp",
        y="feels_like",
        title="🌡 Ощущается как (°C)",
        labels={"timestamp": "Дата и время", "feels_like": "Ощущается как (°C)"},
        markers=True,
        line_shape="spline"
    )
    fig_feels.update_traces(line=dict(color='orange'))

    # Влажность
    fig_hum = px.line(
        filtered_df,
        x="timestamp",
        y="humidity",
        title="💧 Влажность (%)",
        labels={"timestamp": "Дата и время", "humidity": "Влажность (%)"},
        markers=True,
        line_shape="spline"
    )
    fig_hum.update_traces(line=dict(color='dodgerblue'))

    # Давление
    fig_pressure = px.line(
        filtered_df,
        x="timestamp",
        y="pressure",
        title="🧭 Давление (гПа)",
        labels={"timestamp": "Дата и время", "pressure": "Давление (гПа)"},
        markers=True,
        line_shape="spline"
    )
    fig_pressure.update_traces(line=dict(color='darkgreen'))

    # Скорость ветра
    fig_wind = px.line(
        filtered_df,
        x="timestamp",
        y="wind_speed",
        title="🌬 Скорость ветра (м/с)",
        labels={"timestamp": "Дата и время", "wind_speed": "Скорость ветра (м/с)"},
        markers=True,
        line_shape="spline"
    )
    fig_wind.update_traces(line=dict(color='purple'))

    # Последнее описание погоды
    latest = filtered_df.sort_values("timestamp").iloc[-1]
    description = latest["weather_description"].capitalize()
    weather_text = html.H3(f"📝 Последнее наблюдение в {selected_city}: {description}", style={"textAlign": "center"})

    return [
        weather_text,
        dcc.Graph(figure=fig_temp),
        dcc.Graph(figure=fig_feels),
        dcc.Graph(figure=fig_hum),
        dcc.Graph(figure=fig_pressure),
        dcc.Graph(figure=fig_wind)
    ]

# Главная страница (Flask)
@server.route("/")
def index():
    return render_template_string("""
    <html>
    <head>
        <title>Климатический мониторинг</title>
        <style>
            body {
                background: linear-gradient(to bottom, #e0f7fa, #ffffff);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                text-align: center;
                padding-top: 100px;
                color: #333;
            }
            h1 {
                font-size: 40px;
                margin-bottom: 20px;
            }
            p {
                font-size: 18px;
            }
            a {
                text-decoration: none;
                color: white;
                background-color: #00796b;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            a:hover {
                background-color: #004d40;
            }
        </style>
    </head>
    <body>
        <h1>🌍 Климатический мониторинг</h1>
        <p>Система визуализации и анализа климатических данных</p>
        <p><a href="/dashboard/">Перейти к дашборду</a></p>
    </body>
    </html>
    """)

# Запуск сервера
if __name__ == '__main__':
    server.run(debug=True)