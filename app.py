import subprocess
import sys

# ------------------------------------------------
# 强行安装依赖包（专治各种不服）
# ------------------------------------------------
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import joblib
except ImportError:
    print("正在暴力安装 joblib...")
    install('joblib')
    import joblib

try:
    import sklearn
except ImportError:
    print("正在暴力安装 scikit-learn...")
    install('scikit-learn')

try:
    import plotly
except ImportError:
    print("正在暴力安装 plotly...")
    install('plotly')

# ------------------------------------------------
# 下面是你原来的代码
# ------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
# ... (保留你原来剩下的代码) ...
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import os

# ==========================================
# 1. 工程配置
# ==========================================
st.set_page_config(page_title="深圳房产 AI 指挥舱", page_icon="🏙️", layout="wide")

# 强制定位到当前文件夹 (防止找不到文件)
current_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_folder)

# 赛博朋克 CSS
st.markdown("""
<style>
    .stApp {background-color: #0E1117;}
    section[data-testid="stSidebar"] {background-color: #161B22;}
    .stMarkdown, .stText, h1, h2, h3, p {color: #E0E0E0 !important;}
    div[data-testid="metric-container"] {
        background-color: #1F2630; border: 1px solid #4B4B4B;
        padding: 10px; border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.05);
    }
    .stButton>button {
        color: #0E1117; background: linear-gradient(90deg, #00ADB5 0%, #00FFF5 100%);
        border: none; border-radius: 20px; font-weight: bold; width: 100%; height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 加载资源
# ==========================================
@st.cache_data
def load_data():
    # 自动寻找 csv
    import glob
    csv_files = glob.glob("*.csv")
    if not csv_files:
        st.error("❌ 找不到 CSV 数据文件！请检查文件夹。")
        st.stop()
    df = pd.read_csv(csv_files[0])
    
    # 加载模型
    try:
        model = joblib.load('shenzhen_house_model.pkl')
        cols = joblib.load('model_columns.pkl')
    except:
        st.error("❌ 找不到模型文件 (.pkl)！请先运行 setup.py 或 train.py。")
        st.stop()
        
    # 真实坐标字典
    coords = {
        '科技园': [22.5415, 113.9517], '蛇口': [22.4839, 113.9163], '前海': [22.5226, 113.9029],
        '香蜜湖': [22.5489, 114.0374], '福田中心区': [22.5431, 114.0579], '梅林': [22.5683, 114.0538],
        '宝安中心区': [22.5533, 113.8831], '龙岗中心城': [22.7209, 114.2478], '龙华中心': [22.6550, 114.0292]
    }
    dist_centers = {
        '南山': [22.5333, 113.9303], '福田': [22.5429, 114.0596], '罗湖': [22.5468, 114.1315],
        '宝安': [22.5533, 113.8831], '龙岗': [22.7209, 114.2478]
    }
    return df, model, cols, coords, dist_centers

df, model, model_cols, street_coords, dist_coords = load_data()

# ==========================================
# 3. 界面逻辑
# ==========================================
st.sidebar.title("🚀 SZ-AI 指挥台")
sel_dist = st.sidebar.selectbox("📍 行政区", df['district'].unique())
avail_streets = df[df['district'] == sel_dist]['subdistrict'].unique()
sel_street = st.sidebar.selectbox("🛣️ 片区", avail_streets)

st.sidebar.write("---")
with st.sidebar.form("input_form"):
    area = st.number_input("面积 (㎡)", 10.0, 800.0, 89.0)
    c1, c2 = st.columns(2)
    room = c1.number_input("室", 1, 9, 3)
    hall = c2.number_input("厅", 0, 5, 2)
    metro = st.slider("距地铁 (米)", 0, 3000, 500)
    submit = st.form_submit_button("开始估价 ➤")

# 主界面
tab1, tab2 = st.tabs(["🗺️ 全域沙盘", "📈 趋势分析"])

with tab1:
    st.subheader(f"📡 实时热力: {sel_street}")
    center = street_coords.get(sel_street, dist_coords.get(sel_dist, [22.5431, 114.0579]))
    
    # 地图数据
    map_df = df[df['subdistrict'] == sel_street].copy()
    if len(map_df) < 5: map_df = df[df['district'] == sel_dist].copy()
    if len(map_df) > 500: map_df = map_df.sample(500)
    
    # 模拟分布
    map_df['lat'] = center[0] + np.random.normal(0, 0.006, len(map_df))
    map_df['lon'] = center[1] + np.random.normal(0, 0.006, len(map_df))
    
    fig = px.scatter_mapbox(
        map_df, lat="lat", lon="lon", color="unit_price", size="area_sqm",
        color_continuous_scale="Viridis", size_max=10, zoom=12,
        center={"lat": center[0], "lon": center[1]},
        mapbox_style="carto-darkmatter", height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    if submit:
        # 预测
        input_data = pd.DataFrame([{'rooms': room, 'halls': hall, 'area_sqm': area, 'metro_distance_m': metro}])
        for col in model_cols:
            if col not in input_data.columns:
                input_data[col] = 1 if col == f'district_{sel_dist}' else 0
        
        pred_total = model.predict(input_data[model_cols])[0]
        pred_unit = (pred_total * 10000) / area
        
        c1, c2 = st.columns(2)
        c1.metric("预估总价", f"{pred_total:.0f} 万")
        c2.metric("预估单价", f"{pred_unit:.0f} 元/㎡")

with tab2:
    st.subheader("📉 价值走势模拟")
    dates = pd.date_range(start="2025-02-01", periods=12, freq="M")
    base = df[df['district'] == sel_dist]['unit_price'].mean()
    trend = [base * (1 + 0.02 * i + np.random.normal(0, 0.02)) for i in range(12)]
    fig_trend = px.line(x=dates, y=trend, title="未来12个月预测")
    fig_trend.update_layout(paper_bgcolor="#1F2630", plot_bgcolor="#0E1117", font_color="#E0E0E0")

    st.plotly_chart(fig_trend, use_container_width=True)
