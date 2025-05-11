
import streamlit as st
from optimizer import run_ga
from visualizer import plot_gantt

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
            st.subheader("🕒 Gantt Şeması (Zaman Çizelgesi)")
            fig = plot_gantt(log)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Hiçbir geçerli rota bulunamadı. Lütfen parametreleri değiştirin.")
