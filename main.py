from fastapi import FastAPI
import requests
import csv
from io import StringIO
import json
from math import radians, sin, cos, sqrt, atan2


# Crear una instancia de la aplicación
app = FastAPI()
url = "https://sinca.mma.gob.cl/index.php/json/listadomapa2k19"
payload = {}
headers = {}

# Definir una ruta y su operación


@app.get("/names")
def get_names():
    data = []
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    for i in response:
        data.append(i['nombre'])
    return {"estaciones": data}


@app.get("/locations")
def get_location():
    data1 = []
    data = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    for i in response:
        data[i['nombre']] = []
        data[i['nombre']].append({
            'latitude': i['latitud'],
            'longitud': i['longitud']
        })
    return data


@app.get("/nearest_station")
def get_nearest_station(latitude: float, longitude: float):
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371.0  # Radio promedio de la Tierra en kilómetros

        # Convierte las coordenadas de grados decimales a radianes
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        # Diferencias en latitud y longitud
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula de la distancia haversine
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Calcula la distancia
        distance = R * c

        return distance

    min_distance = float('inf')
    nearest_station = None
    data1 = []
    data = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    for i in response:
        data[i['nombre']] = []
        data[i['nombre']].append({
            'latitude': i['latitud'],
            'longitud': i['longitud']
        })
    stations1 = data

    for station, coords in stations1.items():
        for coord in coords:
            station_lat = coord["latitude"]
            station_lon = coord["longitud"]

            # Calcula la distancia entre la ubicación proporcionada y la estación actual
            distance = calculate_distance(
                latitude, longitude, station_lat, station_lon)

            # Actualiza la estación más cercana si encontramos una distancia menor
            if distance < min_distance:
                min_distance = distance
                nearest_station = {
                    "nombre": station,
                    "latitud": station_lat,
                    "longitud": station_lon,
                    "distancia": distance
                }

    return nearest_station


@app.get("/station/{station_name}")
def get_station_data(station_name: str):
    data1 = []
    data = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    for i in response:
        data[i['nombre']] = []
        data[i['nombre']].append({
            'key': i['key'],
            'latitude': i['latitud'],
            'longitud': i['longitud'],
            'comuna': i['comuna'],
            'region': i['region'],
        })
        for j in i['realtime']:
            try:
                data[i['nombre']].append({
                    'sensor': j['name'],
                    'valor': j['tableRow']['value'],
                    'color': j['tableRow']['color'],
                    'status': j['tableRow']['status'],
                    'fecha': j['tableRow']['datetime']
                })
            except:
                pass
    stations = data
    # Verifica si la estación existe en los datos
    if station_name in stations:
        station_data = stations[station_name]
        return {station_name: station_data}
    else:
        return {"error": "Estación no encontrada"}
