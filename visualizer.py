
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


def plot_scenario_comparison(scenarios):
    import plotly.graph_objects as go
    names = [s["name"] for s in scenarios]
    dists = [s["dist"] for s in scenarios]
    times = [s["time"] for s in scenarios]
    risks = [s["risk"] for s in scenarios]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Mesafe (km)", x=names, y=dists))
    fig.add_trace(go.Bar(name="Süre (dk)", x=names, y=times))
    fig.add_trace(go.Bar(name="Risk", x=names, y=risks))
    fig.update_layout(barmode='group', title="📊 Senaryo Karşılaştırması")
    return fig


def compute_emission_kwh(dist_km, avg_speed_kmh=60):
    co2_per_km = 0.2  # kg/km
    kwh_per_km = 0.25  # elektrikli tüketim (örnek)
    return dist_km * co2_per_km, dist_km * kwh_per_km

def plot_emission_energy_comparison(scenarios):
    import plotly.graph_objects as go
    names = [s["name"] for s in scenarios]
    emissions = []
    energies = []
    for s in scenarios:
        co2, kwh = compute_emission_kwh(s["dist"])
        emissions.append(co2)
        energies.append(kwh)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="CO₂ Emisyonu (kg)", x=names, y=emissions))
    fig.add_trace(go.Bar(name="Enerji Tüketimi (kWh)", x=names, y=energies))
    fig.update_layout(barmode='group', title="🌱 Emisyon ve Enerji Tüketimi Karşılaştırması")
    return fig
