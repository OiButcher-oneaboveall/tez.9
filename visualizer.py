
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
