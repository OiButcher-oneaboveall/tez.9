
import streamlit as st
from optimizer import run_ga
from visualizer import plot_gantt, plot_folium_route
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🚛 İstanbul Tehlikeli Madde Taşımacılığı - GA Optimizasyonu")

st.sidebar.header("⚙️ Genetik Algoritma Parametreleri")
pop_size = st.sidebar.slider("Popülasyon Büyüklüğü", 20, 200, 50)
generations = st.sidebar.slider("Nesil Sayısı", 50, 1000, 200)
max_risk = st.sidebar.slider("Maksimum Toplam Risk", 0.5, 3.0, 1.5, step=0.1)

if st.button("🚀 Optimizasyonu Başlat"):
    with st.spinner("Hesaplanıyor..."):
        route, dist, time, risk, log = run_ga(pop_size, generations, max_risk)
        if route:
            st.success("✅ En iyi rota bulundu!")
            st.write("**Toplam Mesafe:**", round(dist, 2), "km")
            st.write("**Toplam Süre:**", round(time, 2), "dk")
            st.write("**Toplam Risk:**", round(risk, 3))
            st.write("**Rota:**", route)
            st.subheader("🕒 Gantt Şeması")
            fig = plot_gantt(log)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🗺️ İstanbul Haritası Üzerinde Güzergah")
            route_names = ["Rafineri"] + [st.session_state.get("cities", [])[i] for i in route[1:-1]] + ["Rafineri"]
            map_obj = plot_folium_route(route_names)
            if map_obj:
                st_folium(map_obj, use_container_width=True)
        else:
            st.error("❌ Hiçbir geçerli rota bulunamadı. Lütfen parametreleri değiştirin.")
