
import streamlit as st
from optimizer import run_ga, cities
from visualizer import draw_route_on_map

import pandas as pd
from streamlit_folium import st_folium
from PIL import Image
import os

# Başlık ve Tema
st.set_page_config(page_title="İstanbul Rota Optimizasyonu", layout="wide")
st.title("🛣️ İstanbul Tehlikeli Madde Taşımacılığı Rota Optimizasyonu")

# Sekmeler
tabs = st.tabs(["🚀 Senaryo Oluştur", "⚙️ Parametreler", "📈 Sonuçlar", "🗺️ Harita", "⛽ Bekleme Animasyonu", "🌱 Emisyon ve Enerji", "🕒 Gantt Şeması", "📊 Parametre Analizi", "📂 Senaryo Karşılaştırma"])

# Global koordinatlar (örnek İstanbul noktaları - lon, lat)
city_coords = {
    "Rafineri": [28.7676, 40.9666],
    "Gürpınar": [28.6014, 40.9712],
    "Yenikapı": [28.9540, 41.0040],
    "Selimiye": [29.0212, 41.0035],
    "İçerenköy": [29.1034, 40.9630],
    "Tophane": [28.9838, 41.0275],
    "Alibeyköy": [28.9374, 41.0781],
    "İstinye": [29.0546, 41.1166],
}

with tabs[0]:
    st.subheader("🚚 Yeni Senaryo Bilgileri")
    scenario_name = st.text_input("Senaryo Adı", "Senaryo 1")
    user_name = st.text_input("Kullanıcı Adı", "Misafir")
    st.success(f"👤 {user_name} tarafından oluşturuluyor: **{scenario_name}**")

with tabs[1]:
    st.subheader("⚙️ Genetik Algoritma Parametreleri")
    pop_size = st.slider("Popülasyon Büyüklüğü", 50, 500, 200, 50)
    generations = st.slider("Nesil Sayısı", 100, 2000, 1000, 100)
    max_risk = st.slider("Maksimum Toplam Risk", 0.5, 3.0, 1.5, 0.1)

    if st.button("🧬 Optimizasyonu Başlat"):
        with st.spinner("Rota hesaplanıyor..."):
            best_route, distance, time_min, risk, log = run_ga(pop_size, generations, max_risk)
            if best_route:
                st.session_state["best_route"] = best_route
                st.session_state["log"] = log
                st.session_state["distance"] = distance
                st.session_state["time_min"] = time_min
                st.session_state["risk"] = risk
                st.success("✅ En iyi rota başarıyla hesaplandı.")
            else:
                st.error("❌ Hiçbir geçerli rota bulunamadı. Lütfen risk sınırını veya nesil sayısını artırın.")

with tabs[2]:
    st.subheader("📊 Sonuç Özeti")

    if "best_route" in st.session_state:
        st.metric("Toplam Mesafe (km)", round(st.session_state["distance"], 2))
        st.metric("Toplam Süre (dk)", round(st.session_state["time_min"], 2))
        st.metric("Toplam Risk", round(st.session_state["risk"], 2))

        df = pd.DataFrame(st.session_state["log"])
        st.dataframe(df)

        st.download_button("📥 Çizelgeyi İndir", df.to_csv(index=False), "zaman_cizelgesi.csv")

with tabs[3]:
    st.subheader("🗺️ İstanbul Haritasında Rota")

    if "best_route" in st.session_state and "log" in st.session_state:
        coords = [city_coords[cities[i]] for i in st.session_state["best_route"]]
        fmap = draw_route_on_map(st.session_state["best_route"], coords, st.session_state["log"])
        st_folium(fmap, width=1000, height=600)


with tabs[4]:
    st.subheader("⛽ Bekleme Süresi: İkmal Aracı Animasyonu")

    gif_path = os.path.join("assets", "ikmal_araci.gif")

    if os.path.exists(gif_path):
        try:
            with open(gif_path, "rb") as f:
                st.image(f.read(), caption="İkmal Aracı Bekliyor...", use_column_width=True)
        except Exception as e:
            st.warning("⚠️ İkmal aracı görseli açılamadı veya geçersiz. Lütfen geçerli bir .gif dosyası yerleştirin.")
    else:
        st.warning("🔍 ikmal_araci.gif bulunamadı. Lütfen assets klasöründe olduğundan emin olun.")

with tabs[5]:
    st.subheader("🌱 Enerji Tüketimi ve Karbon Emisyonu")

    if "distance" in st.session_state:
        mesafe_km = st.session_state["distance"]
        tuketim_litre_per_100km = 30  # ağır vasıta ortalama tüketimi
        co2_per_litre = 2.68  # kg CO2 / litre

        toplam_litre = (mesafe_km / 100) * tuketim_litre_per_100km
        toplam_emisyon = toplam_litre * co2_per_litre
        toplam_enerji_mj = toplam_litre * 36  # 1 litre dizel ≈ 36 MJ

        st.metric("🚛 Yakıt Tüketimi", f"{toplam_litre:.2f} litre")
        st.metric("💨 Karbon Emisyonu", f"{toplam_emisyon:.2f} kg CO₂")
        st.metric("⚡ Enerji Tüketimi", f"{toplam_enerji_mj:.2f} MJ")

        st.bar_chart({
            "Değerler": [toplam_litre, toplam_emisyon, toplam_enerji_mj]
        })
    else:
        st.info("Önce bir rota hesaplamanız gerekiyor.")

from datetime import datetime, timedelta
import plotly.express as px

with tabs[6]:
    st.subheader("🕒 Gantt Zamanlama Şeması")

    if "log" in st.session_state:
        gantt_data = []
        start_time = datetime.strptime("06:00", "%H:%M")
        for entry in st.session_state["log"]:
            arr = datetime.strptime(entry["arrival"], "%H:%M")
            dep = datetime.strptime(entry["departure"], "%H:%M")
            if arr < dep:
                gantt_data.append({
                    "Görev": f"{entry['from']} → {entry['to']}",
                    "Başlangıç": start_time + timedelta(hours=arr.hour, minutes=arr.minute),
                    "Bitiş": start_time + timedelta(hours=dep.hour, minutes=dep.minute),
                    "Tip": "Servis"
                })

        fig = px.timeline(gantt_data, x_start="Başlangıç", x_end="Bitiş", y="Görev", color="Tip")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Gantt şeması oluşturmak için önce bir rota hesaplayın.")

import matplotlib.pyplot as plt

with tabs[7]:
    st.subheader("📊 Parametre Etki Analizi")

    if "distance" in st.session_state and "time_min" in st.session_state and "risk" in st.session_state:
        fig, ax = plt.subplots(figsize=(10, 4))
        metrics = {
            "Toplam Mesafe (km)": st.session_state["distance"],
            "Toplam Süre (dk)": st.session_state["time_min"],
            "Toplam Risk": st.session_state["risk"],
            "Popülasyon": pop_size,
            "Nesil Sayısı": generations,
            "Maks. Risk": max_risk
        }
        ax.bar(metrics.keys(), metrics.values(), color="skyblue")
        plt.xticks(rotation=45)
        plt.title("Optimizasyon Parametrelerinin Etkisi")
        st.pyplot(fig)
    else:
        st.info("Lütfen önce bir rota hesaplayın.")

import json

with tabs[8]:
    st.subheader("📂 Senaryo Karşılaştırma")

    st.markdown("### 💾 Kayıtlı Senaryoları Yükle")
    uploaded_files = st.file_uploader("Birden fazla senaryo dosyası yükleyin (.json)", type="json", accept_multiple_files=True)

    if uploaded_files:
        scenario_data = []
        for file in uploaded_files:
            data = json.load(file)
            scenario_data.append({
                "Ad": file.name.replace(".json", ""),
                "Mesafe": data.get("distance", 0),
                "Süre": data.get("time_min", 0),
                "Risk": data.get("risk", 0)
            })

        df = pd.DataFrame(scenario_data)
        st.dataframe(df)

        st.bar_chart(df.set_index("Ad"))
    else:
        st.info("Karşılaştırmak için lütfen en az 2 senaryo yükleyin.")
