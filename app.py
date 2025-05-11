cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]

import streamlit as st
import os, json
from optimizer import run_ga
from visualizer import plot_gantt, plot_folium_route, plot_scenario_comparison, plot_emission_energy_comparison
from streamlit_folium import st_folium

SCENARIO_DIR = "scenarios"
os.makedirs(SCENARIO_DIR, exist_ok=True)

st.set_page_config(layout="wide")
st.title("🚛 GA Tabanlı Rota + Sürdürülebilirlik Optimizasyonu")

tab1, tab2 = st.tabs(["🚀 Yeni Optimizasyon", "📊 Senaryo Karşılaştırma"])

with tab1:
    st.sidebar.header("⚙️ Genetik Algoritma Parametreleri")
    pop_size = st.sidebar.slider("Popülasyon Büyüklüğü", 20, 200, 50)
    generations = st.sidebar.slider("Nesil Sayısı", 50, 1000, 200)
    max_risk = st.sidebar.slider("Maksimum Risk", 0.5, 3.0, 1.5, step=0.1)

    if st.button("🚀 Hesapla"):
        with st.spinner("Hesaplanıyor..."):
            route, dist, time, risk, log = run_ga(pop_size, generations, max_risk)
            if route:
                st.success("✅ En iyi rota bulundu!")
                st.write("**Mesafe:**", round(dist,2), "km  |  **Süre:**", round(time,1), "dk  |  **Risk:**", round(risk,3))
                city_names = [cities[i] for i in route]
                st.write("**Rota:**", " → ".join(city_names))
                st.subheader("🕒 Gantt Şeması")
                st.plotly_chart(plot_gantt(log), use_container_width=True)
                st.subheader("🗺️ Harita")
                route_names = [cities[i] for i in route]
                map_obj = plot_folium_route(route_names)
                if map_obj:
                    st_folium(map_obj, use_container_width=True)

                scenario_name = st.text_input("📁 Senaryoya isim verin:", value="senaryo_1")
                if st.button("💾 Senaryoyu Kaydet"):
                    result = {"name": scenario_name, "route": route, "dist": dist, "time": time, "risk": risk}
                    with open(os.path.join(SCENARIO_DIR, scenario_name + ".json"), "w") as f:
                        json.dump(result, f)
                    st.success(f"✅ {scenario_name} başarıyla kaydedildi.")
            else:
                st.error("❌ Geçerli rota bulunamadı.")

with tab2:
    files = [f for f in os.listdir(SCENARIO_DIR) if f.endswith(".json")]
    selected = st.multiselect("📂 Karşılaştırmak istediğiniz senaryoları seçin:", files, default=files[:2])
    if selected:
        loaded = []
        for fname in selected:
            with open(os.path.join(SCENARIO_DIR, fname)) as f:
                data = json.load(f)
                data["name"] = fname.replace(".json", "")
                loaded.append(data)
        st.subheader("📊 Risk / Süre / Mesafe Karşılaştırması")
        st.plotly_chart(plot_scenario_comparison(loaded), use_container_width=True)
        st.subheader("🌱 Emisyon ve Enerji Analizi")
        st.plotly_chart(plot_emission_energy_comparison(loaded), use_container_width=True)
