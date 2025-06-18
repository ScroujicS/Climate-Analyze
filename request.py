import csv
import os
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "86f62b6444e867fd4b6b9a009b62e3c5"
CSV_FILE_PATH = "mock_climate_data.csv"

CITIES = [
    "Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Nizhny Novgorod",
    "Kazan", "Chelyabinsk", "Omsk", "Rostov-on-Don", "Ufa",
    "Volgograd", "Krasnoyarsk", "Saratov", "Tyumen", "Togliatti",
    "Izhevsk", "Barnaul", "Khabarovsk", "Vladivostok", "Kaliningrad"
]

CSV_FIELDS = ["city", "timestamp", "temperature", "feels_like", "pressure", "humidity", "wind_speed", "weather_description"]

def get_climate_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},RU",
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        climate_info = {
            "city": data["name"],
            "timestamp": datetime.utcfromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "weather_description": data["weather"][0]["description"]
        }
        return climate_info
    else:
        logger.warning(f"Error retrieving data for {city}: {response.status_code}")
        return None

def update_csv_with_weather_data():
    logger.info("Starting CSV weather data update...")

    # Загрузка текущих данных, если CSV существует
    existing_rows = []
    if os.path.isfile(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_rows = list(reader)

    # Получаем новые данные
    new_rows = []
    for city in CITIES:
        data = get_climate_data(city)
        if data:
            new_rows.append(data)

    # Конкатенация старых и новых данных
    combined_rows = existing_rows + new_rows

    # (Опционально) Можно добавить логику исключения дубликатов по city+timestamp

    # Запись всех данных обратно в файл
    try:
        with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(combined_rows)
        logger.info(f"CSV file '{CSV_FILE_PATH}' updated with total {len(combined_rows)} records.")
    except Exception as e:
        logger.error(f"Failed to update CSV file: {e}")

if __name__ == "__main__":
    update_csv_with_weather_data()
