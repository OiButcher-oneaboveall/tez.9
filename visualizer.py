
import folium
import requests
import time

ORS_API_KEY = "your_openrouteservice_api_key"

def get_route_coords(coords):
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {"Authorization": ORS_API_KEY}
    body = {"coordinates": coords}

    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        return response.json()["features"][0]["geometry"]["coordinates"]
    else:
        return []

def draw_route_on_map(route, cities_coords, travel_log, animated=False):
    start_point = cities_coords[route[0]]
    fmap = folium.Map(location=start_point[::-1], zoom_start=11)

    for idx, (frm, to) in enumerate(zip(route[:-1], route[1:])):
        coords = [cities_coords[frm], cities_coords[to]]
        route_coords = get_route_coords(coords)
        if route_coords:
            popup_text = ""
            if idx < len(travel_log):
                popup_text = f"{travel_log[idx]['from']} → {travel_log[idx]['to']}<br>"
                popup_text += f"🚚 Süre: {travel_log[idx]['departure']} - {travel_log[idx]['arrival']}"
            folium.PolyLine(
                locations=[(lat, lon) for lon, lat in route_coords],
                color="blue", weight=6, opacity=0.8,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(fmap)
            if animated:
                folium.Marker(
                    location=route_coords[0][::-1],
                    icon=folium.Icon(color="red", icon="play", prefix="fa")
                ).add_to(fmap)
                time.sleep(1)
    return fmap
