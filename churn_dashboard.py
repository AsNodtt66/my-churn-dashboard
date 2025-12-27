import streamlit as st
import pandas as pd
import plotly.express as px

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Analisis Loyalitas Pelanggan", layout="wide")

st.title("🛒 Dashboard Pemantauan Pelanggan")
st.markdown("Gunakan dashboard ini untuk melihat siapa pelanggan yang akan berhenti belanja dan mana yang setia.")

# --- MUAT & BERSIHKAN DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv('churn_results.csv', sep=';')
    df.columns = df.columns.str.strip()
    
    # 1. MAPPING NEGARA (Ubah kode angka jadi nama)
    # Sesuaikan angka ini dengan hasil encoding di notebook kamu jika berbeda
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
    
    # 3. SEGMENTASI BAHASA AWAM
    def segmentasi_simpel(row):
        if row['Predicted_Churn'] == 1 and row['Recency'] > 100:
            return "🚨 Berisiko Berhenti (Urgent)"
        elif row['Predicted_Churn'] == 0 and row['Recency'] < 30:
            return "🌟 Pelanggan Setia (Aktif)"
        elif row['Recency'] <= 14:
            return "🆕 Pelanggan Baru/Baru Belanja"
        else:
            return "💤 Pelanggan Pasif"

    df['Status_Pelanggan'] = df.apply(segmentasi_simpel, axis=1)
    
    # Hitung Skor Risiko (0-100) untuk pengurutan
    # Semakin lama tidak belanja (Recency) dan diprediksi Churn, skor makin tinggi
    df['Skor_Risiko'] = (df['Recency'] / df['Recency'].max() * 100).round(1)
    return df

df = load_data()

# --- SIDEBAR (FILTER & SORTIR) ---
st.sidebar.header("⚙️ Pengaturan Tampilan")
pilihan_sortir = st.sidebar.radio(
    "Urutkan Daftar Pelanggan:",
    ["Risiko Tertinggi (Bahaya)", "Risiko Terendah (Aman)"]
)

# --- RINGKASAN UTAMA ---
c1, c2, c3 = st.columns(3)
total_churn = df[df['Predicted_Churn'] == 1].shape[0]
c1.metric("Total Pelanggan", f"{len(df)} orang")
c2.metric("Perlu Perhatian Khusus", f"{total_churn} orang", delta="Risiko Churn", delta_color="inverse")
c3.metric("Rata-rata Belanja", f"${df['TotalPrice'].mean():,.2f}")

st.divider()

# --- TAMPILAN TAB ---
tab1, tab2 = st.tabs(["📊 Analisis Kelompok", "📋 Daftar Detail Pelanggan"])

with tab1:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.write("### Komposisi Pelanggan")
        fig_pie = px.pie(df, names='Status_Pelanggan', hole=0.4, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_right:
        st.write("### Negara dengan Risiko Tertinggi")
        negara_risk = df[df['Predicted_Churn'] == 1]['Country'].value_counts().head(5)
        fig_bar = px.bar(negara_risk, orientation='h', labels={'value':'Jumlah Orang', 'index':'Negara'},
                         color_discrete_sequence=['#ef553b'])
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.write("### Data Pelanggan")
    st.info("💡 Gunakan fitur sortir di menu samping (kiri) untuk mengubah urutan data.")
    
    # Logika Sortir
    if pilihan_sortir == "Risiko Tertinggi (Bahaya)":
        df_display = df.sort_values(by=['Predicted_Churn', 'Skor_Risiko'], ascending=False)
    else:
        df_display = df.sort_values(by=['Predicted_Churn', 'Skor_Risiko'], ascending=True)
    
    # Tampilkan Tabel
    st.dataframe(
        df_display[['CustomerID', 'Country', 'Status_Pelanggan', 'Recency', 'TotalPrice', 'Skor_Risiko']],
        use_container_width=True,
        column_config={
            "Skor_Risiko": st.column_config.ProgressColumn(
                "Tingkat Bahaya (%)",
                min_value=0, max_value=100, format="%.1f%%"
            ),
            "TotalPrice": "Total Belanja ($)",
            "Recency": "Hari Sejak Belanja Terakhir"
        },
        hide_index=True
    )

    # Tombol Download
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Laporan Ini (CSV)", csv, "laporan_pelanggan.csv", "text/csv")

st.caption("Dashboard ini otomatis mengurutkan pelanggan berdasarkan algoritma prediksi churn.")