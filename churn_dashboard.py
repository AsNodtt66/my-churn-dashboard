import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PENGATURAN HALAMAN & TEMA ---
st.set_page_config(
    page_title="Analisis Loyalitas Pelanggan",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for styling
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Cards styling */
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: none;
    }
    
    /* Metric cards */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4b6cb7 0%, #182848 100%);
        color: white;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 176, 155, 0.4);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Progress bars in dataframe */
    [data-testid="stProgress"] {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌟 Dashboard Loyalitas Pelanggan")
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
<h3 style="color: white; margin: 0;">🎯 Identifikasi & Retensi Pelanggan</h3>
<p style="margin: 10px 0 0 0; opacity: 0.9;">Dashboard ini membantu Anda mengidentifikasi pelanggan berisiko churn dan 
mempertahankan pelanggan setia dengan strategi yang tepat.</p>
</div>
""", unsafe_allow_html=True)

# --- MUAT & BERSIHKAN DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv('churn_results.csv', sep=';')
    df.columns = df.columns.str.strip()
    
    # 1. MAPPING NEGARA
    peta_negara = {
        1: "United Kingdom", 11: "France", 13: "Germany", 14: "EIRE", 
        22: "Spain", 24: "Portugal", 2: "Australia", 3: "Austria",
        32: "Sweden", 31: "Switzerland", 10: "Finland", 17: "Italy"
    }
    df['Country'] = df['Country'].map(peta_negara).fillna(df['Country'].astype(str))

    # 2. BERSIHKAN HARGA
    def clean_price(x):
        if isinstance(x, str):
            return float(x.replace('$', '').replace('.', '').replace(',', '.').strip())
        return float(x)
    
    df['TotalPrice'] = df['TotalPrice'].apply(clean_price)
    df['CustomerID'] = df['CustomerID'].astype(str)
    
    # 3. SEGMENTASI BAHASA AWAM dengan warna
    def segmentasi_simpel(row):
        if row['Predicted_Churn'] == 1 and row['Recency'] > 100:
            return "🚨 Berisiko Tinggi"
        elif row['Predicted_Churn'] == 1 and row['Recency'] <= 100:
            return "⚠️ Berisiko Sedang"
        elif row['Predicted_Churn'] == 0 and row['Recency'] < 30:
            return "🌟 Pelanggan Setia"
        elif row['Recency'] <= 14:
            return "🆕 Pelanggan Baru"
        else:
            return "💤 Pelanggan Pasif"

    df['Status_Pelanggan'] = df.apply(segmentasi_simpel, axis=1)
    
    # Hitung Skor Risiko dengan warna gradient
    df['Skor_Risiko'] = (df['Recency'] / df['Recency'].max() * 100).round(1)
    
    # Tambahkan kategori warna untuk visual
    def get_color_category(score):
        if score > 70:
            return "#ef5350"  # Red
        elif score > 40:
            return "#ffa726"  # Orange
        elif score > 20:
            return "#42a5f5"  # Blue
        else:
            return "#66bb6a"  # Green
    
    df['Warna_Risiko'] = df['Skor_Risiko'].apply(get_color_category)
    
    return df

df = load_data()

# --- SIDEBAR (FILTER & SORTIR) ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: white; margin: 0;">⚙️ Kontrol</h2>
        <p style="color: rgba(255,255,255,0.8);">Atur tampilan data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filter Negara
    semua_negara = ["Semua"] + sorted(df['Country'].unique().tolist())
    selected_country = st.selectbox("🌍 Filter Negara", semua_negara)
    
    # Filter Status
    semua_status = ["Semua"] + sorted(df['Status_Pelanggan'].unique().tolist())
    selected_status = st.selectbox("🎯 Filter Status", semua_status)
    
    # Sortir
    st.markdown("---")
    st.markdown("### 📊 Sortir Data")
    pilihan_sortir = st.radio(
        "Urutkan berdasarkan:",
        ["Risiko Tertinggi", "Risiko Terendah", "Belanja Tertinggi", "Terbaru Belanja"],
        label_visibility="collapsed"
    )
    
    # Statistik Cepat
    st.markdown("---")
    st.markdown("### 📈 Statistik Cepat")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Total", f"{len(df)}", help="Total pelanggan")
    with col_s2:
        st.metric("Churn", f"{df['Predicted_Churn'].sum()}", 
                 delta=f"{df['Predicted_Churn'].mean()*100:.1f}%",
                 delta_color="inverse")

# Filter data berdasarkan pilihan sidebar
df_filtered = df.copy()
if selected_country != "Semua":
    df_filtered = df_filtered[df_filtered['Country'] == selected_country]
if selected_status != "Semua":
    df_filtered = df_filtered[df_filtered['Status_Pelanggan'] == selected_status]

# --- RINGKASAN UTAMA DENGAN KARTU BERGAYA ---
st.markdown("### 📊 Ringkasan Performa")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card" style="border-left: 5px solid #667eea;">
        <h4 style="color: #667eea; margin: 0 0 10px 0;">👥 Total Pelanggan</h4>
        <h2 style="color: #2c3e50; margin: 0;">{len(df_filtered):,}</h2>
        <p style="color: #7f8c8d; margin: 5px 0 0 0;">Orang</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    churn_count = df_filtered[df_filtered['Predicted_Churn'] == 1].shape[0]
    churn_rate = (churn_count / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
    st.markdown(f"""
    <div class="card" style="border-left: 5px solid #ef5350;">
        <h4 style="color: #ef5350; margin: 0 0 10px 0;">🚨 Berisiko Churn</h4>
        <h2 style="color: #2c3e50; margin: 0;">{churn_count}</h2>
        <p style="color: #7f8c8d; margin: 5px 0 0 0;">{churn_rate:.1f}% dari total</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    avg_spend = df_filtered['TotalPrice'].mean()
    st.markdown(f"""
    <div class="card" style="border-left: 5px solid #42a5f5;">
        <h4 style="color: #42a5f5; margin: 0 0 10px 0;">💰 Rata-rata Belanja</h4>
        <h2 style="color: #2c3e50; margin: 0;">${avg_spend:,.2f}</h2>
        <p style="color: #7f8c8d; margin: 5px 0 0 0;">Per pelanggan</p>
    </div>
    """, unsafe_allow_html=True)

with c4:
    loyal_count = df_filtered[df_filtered['Status_Pelanggan'] == '🌟 Pelanggan Setia'].shape[0]
    st.markdown(f"""
    <div class="card" style="border-left: 5px solid #66bb6a;">
        <h4 style="color: #66bb6a; margin: 0 0 10px 0;">🌟 Pelanggan Setia</h4>
        <h2 style="color: #2c3e50; margin: 0;">{loyal_count}</h2>
        <p style="color: #7f8c8d; margin: 5px 0 0 0;">Aktif & loyal</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- TAMPILAN TAB ---
tab1, tab2, tab3 = st.tabs(["📊 Visualisasi", "📋 Data Detail", "🎯 Rekomendasi"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Distribusi Status Pelanggan")
        
        # Pie chart dengan warna yang lebih hidup
        status_counts = df_filtered['Status_Pelanggan'].value_counts()
        
        # Warna khusus untuk setiap status
        color_map = {
            "🚨 Berisiko Tinggi": "#ef5350",
            "⚠️ Berisiko Sedang": "#ffa726",
            "🌟 Pelanggan Setia": "#66bb6a",
            "🆕 Pelanggan Baru": "#42a5f5",
            "💤 Pelanggan Pasif": "#bdbdbd"
        }
        
        colors = [color_map.get(status, "#42a5f5") for status in status_counts.index]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.5,
            marker=dict(colors=colors),
            textinfo='label+percent',
            insidetextorientation='radial'
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            height=400,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌍 Top 5 Negara Berisiko")
        
        # Bar chart horizontal dengan gradient
        negara_risk = df_filtered[df_filtered['Predicted_Churn'] == 1]['Country'].value_counts().head(5)
        
        fig_bar = go.Figure(data=[go.Bar(
            y=negara_risk.index,
            x=negara_risk.values,
            orientation='h',
            marker=dict(
                color=negara_risk.values,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Jumlah")
            ),
            text=negara_risk.values,
            textposition='auto'
        )])
        
        fig_bar.update_layout(
            xaxis_title="Jumlah Pelanggan Berisiko",
            yaxis_title="Negara",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Line chart untuk trend recency
    st.markdown("#### 📈 Tren Lama Tidak Belanja (Recency)")
    
    # Buat bins untuk recency
    df_filtered['Recency_Group'] = pd.cut(df_filtered['Recency'], 
                                         bins=[0, 30, 60, 90, 120, 150, 180, df_filtered['Recency'].max()],
                                         labels=['<30', '30-60', '60-90', '90-120', '120-150', '150-180', '>180'])
    
    recency_dist = df_filtered.groupby('Recency_Group').size()
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=recency_dist.index,
        y=recency_dist.values,
        mode='lines+markers',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#764ba2'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    fig_line.update_layout(
        xaxis_title="Hari Sejak Belanja Terakhir",
        yaxis_title="Jumlah Pelanggan",
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.markdown("#### 📋 Daftar Pelanggan")
    
    # Sortir berdasarkan pilihan
    if pilihan_sortir == "Risiko Tertinggi":
        df_display = df_filtered.sort_values(by=['Predicted_Churn', 'Skor_Risiko'], ascending=False)
    elif pilihan_sortir == "Risiko Terendah":
        df_display = df_filtered.sort_values(by=['Predicted_Churn', 'Skor_Risiko'], ascending=True)
    elif pilihan_sortir == "Belanja Tertinggi":
        df_display = df_filtered.sort_values(by='TotalPrice', ascending=False)
    else:  # Terbaru Belanja
        df_display = df_filtered.sort_values(by='Recency', ascending=True)
    
    # Tampilkan dengan styling
    st.dataframe(
        df_display[['CustomerID', 'Country', 'Status_Pelanggan', 'Recency', 'TotalPrice', 'Skor_Risiko']],
        use_container_width=True,
        column_config={
            "Skor_Risiko": st.column_config.ProgressColumn(
                "Tingkat Risiko",
                min_value=0,
                max_value=100,
                format="%.1f%%",
                help="Semakin tinggi, semakin berisiko"
            ),
            "TotalPrice": st.column_config.NumberColumn(
                "Total Belanja ($)",
                format="$%.2f",
                help="Total belanja keseluruhan"
            ),
            "Recency": st.column_config.NumberColumn(
                "Hari Sejak Belanja",
                help="Semakin tinggi, semakin lama tidak belanja"
            ),
            "Status_Pelanggan": st.column_config.TextColumn(
                "Status",
                help="Kategori pelanggan"
            )
        },
        hide_index=True,
        height=500
    )
    
    # Tombol Download dengan styling
    csv = df_display.to_csv(index=False).encode('utf-8')
    col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
    with col_d2:
        st.download_button(
            label="📥 Download Data sebagai CSV",
            data=csv,
            file_name="laporan_pelanggan_detail.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab3:
    st.markdown("#### 🎯 Strategi Retensi Berdasarkan Segment")
    
    recommendations = {
        "🚨 Berisiko Tinggi": {
            "color": "#ef5350",
            "actions": [
                "Hubungi segera via telepon/email pribadi",
                "Tawarkan diskon eksklusif 25-30%",
                "Kirim survey kepuasan pelanggan",
                "Assign ke tim retensi khusus"
            ]
        },
        "⚠️ Berisiko Sedang": {
            "color": "#ffa726",
            "actions": [
                "Email marketing personalisasi",
                "Tawarkan diskon 15-20% untuk pembelian berikutnya",
                "Ingatkan produk yang pernah dibeli",
                "Program loyalitas point 2x"
            ]
        },
        "🌟 Pelanggan Setia": {
            "color": "#66bb6a",
            "actions": [
                "Program VIP/priority customer",
                "Early access ke produk baru",
                "Free shipping permanen",
                "Birthday rewards khusus"
            ]
        },
        "🆕 Pelanggan Baru": {
            "color": "#42a5f5",
            "actions": [
                "Welcome package & tutorial",
                "Diskon untuk pembelian kedua",
                "Email onboarding series",
                "Survei pengalaman pertama"
            ]
        },
        "💤 Pelanggan Pasif": {
            "color": "#bdbdbd",
            "actions": [
                "Re-engagement campaign",
                "Flash sale notification",
                "We miss you campaign",
                "Product recommendations based on history"
            ]
        }
    }
    
    # Tampilkan rekomendasi dalam columns
    cols = st.columns(len(recommendations))
    
    for idx, (segment, data) in enumerate(recommendations.items()):
        count = df_filtered[df_filtered['Status_Pelanggan'] == segment].shape[0]
        with cols[idx]:
            st.markdown(f"""
            <div style="background: white; border-radius: 10px; padding: 15px; 
                        border-left: 5px solid {data['color']}; margin-bottom: 15px;">
                <h4 style="color: {data['color']}; margin: 0 0 10px 0;">{segment}</h4>
                <p style="font-size: 24px; font-weight: bold; color: #2c3e50; margin: 0;">{count}</p>
                <p style="color: #7f8c8d; margin: 0 0 10px 0;">pelanggan</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Aksi yang disarankan:**")
            for action in data['actions']:
                st.markdown(f"✓ {action}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p>📊 Dashboard Loyalitas Pelanggan | Terakhir diperbarui: Otomatis</p>
    <p>💡 Tips: Fokus pada pelanggan berisiko tinggi untuk meningkatkan retensi</p>
</div>
""", unsafe_allow_html=True)
