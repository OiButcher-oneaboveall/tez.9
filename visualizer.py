
import folium
import streamlit as st
import openrouteservice
from openrouteservice import convert

city_coords = {
    "Rafineri": (41.013, 28.979),
    "Gürpınar": (40.9946, 28.6058),
    "Yenikapı": (41.005, 28.951),
    "Selimiye": (41.0038, 29.0272),
    "İçerenköy": (40.9714, 29.1071),
    "Tophane": (41.0294, 28.9734),
    "Alibeyköy": (41.0733, 28.9315),
    "İstinye": (41.1097, 29.0577)
}

def plot_folium_route(route_names):
    coords = [city_coords[city] for city in route_names if city in city_coords]
    if len(coords) < 2:
        st.error("Yeterli koordinat bulunamadı.")
        return None

    m = folium.Map(location=[41.015, 28.979], zoom_start=11)

    try:
        client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
        route = client.directions(coords, profile='driving-car', format='geojson')
        folium.GeoJson(route, name="route").add_to(m)
    except Exception as e:
        st.error("ORS rotası alınamadı: " + str(e))
        return None

    for name, coord in zip(route_names, coords):
        folium.Marker(coord, tooltip=name).add_to(m)

    folium.LayerControl().add_to(m)
    return m


import plotly.express as px
import pandas as pd

def plot_gantt(log):
    if not log:
        return None
    df = []
    for task in log:
        start_h, start_m = map(int, task["arrival"].split(":"))
        end_h, end_m = map(int, task["departure"].split(":"))
        df.append({
            "Görev": f'{task["from"]} → {task["to"]}',
            "Başlangıç": f"2023-01-01 {start_h:02}:{start_m:02}",
            "Bitiş": f"2023-01-01 {end_h:02}:{end_m:02}",
            "Açıklama": f'Hizmet: {task["service"]}dk, Bekleme: {task["wait"]}dk'
        })
    df = pd.DataFrame(df)
    fig = px.timeline(df, x_start="Başlangıç", x_end="Bitiş", y="Görev", color="Açıklama")
    fig.update_yaxes(autorange="reversed")
    return fig
