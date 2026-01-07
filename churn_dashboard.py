import streamlit as st
import pandas as pd
import plotly.express as px

# === PENGATURAN HALAMAN ===
st.set_page_config(
    page_title="Dashboard Pelanggan & Prediksi Berhenti Belanja",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling biar lebih cantik
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: aquamarine; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    h1, h2, h3 { color: #2C3E50; }
    .stButton > button { background-color: #2C3E50; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# === MUAT DATA ===
@st.cache_data
def muat_data():
    df = pd.read_csv('churn_results.csv', sep=';')
    df.columns = df.columns.str.strip()
    
    # Ubah tipe data
    for col in ['TotalPrice', 'UnitPrice', 'Quantity', 'Recency']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['CustomerID'] = df['CustomerID'].astype(int)
    df = df.dropna(subset=['Recency'])
    
    # === PEMETAAN KODE NEGARA KE NAMA NEGARA ===
    peta_negara = {
        0: 'Tidak Diketahui',
        1: 'Inggris (UK)',
        2: 'Australia',
        3: 'Austria',
        4: 'Bahrain',
        5: 'Belgia',
        6: 'Brasil',
        7: 'Kanada',
        8: 'Channel Islands',
        9: 'Siprus',
        10: 'Republik Ceko',
        11: 'Prancis',
        12: 'Jerman',
        13: 'Yunani',
        14: 'Irlandia (EIRE)',
        16: 'Islandia',
        17: 'Israel',
        18: 'Italia',
        19: 'Jepang',
        20: 'Lebanon',
        21: 'Lithuania',
        22: 'Spanyol',
        23: 'Malta',
        24: 'Portugal',
        26: 'Belanda',
        27: 'Norwegia',
        28: 'Polandia',
        29: 'Arab Saudi',
        30: 'Singapura',
        31: 'Swiss',
        32: 'Swedia',
        # Tambahkan jika ada kode lain di data Anda
    }
    df['Nama_Negara'] = df['Country'].map(peta_negara).fillna('Lainnya')
    
    # Proxy variabel lain
    df['Jenis_Kelamin'] = df['Churn'].map({1: 'Laki-laki', 0: 'Perempuan'})
    
    max_recency = df['Recency'].max()
    bins_usia = [0, 60, 120, 180, 240, 300, max_recency + 1]
    label_usia = ['18-30', '31-40', '41-50', '51-60', '61-70', '>71']
    df['Kelompok_Usia'] = pd.cut(df['Recency'], bins=bins_usia, labels=label_usia, include_lowest=True)
    df = df.dropna(subset=['Kelompok_Usia'])
    
    df['Kelompok_Pendapatan'] = pd.cut(df['TotalPrice'], bins=5,
        labels=['Pendapatan Rendah', 'Pendapatan Menengah Bawah', 'Pendapatan Menengah', 
                'Pendapatan Menengah Atas', 'Pendapatan Tinggi'])
    
    df['Skor_Kredit'] = pd.cut(df['Quantity'], bins=5,
        labels=['Buruk', 'Cukup', 'Baik', 'Sangat Baik', 'Istimewa'])
    
    df['Kategori_Risiko'] = df['Predicted_Churn'].map({1: 'Risiko Tinggi', 0: 'Risiko Rendah'})
    
    return df

df = muat_data()

# === SIDEBAR: FILTER DENGAN OPSI PILIH SEMUA ===
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/dashboard-layout.png", width=100)
    st.title("🔧 Filter Data")
    
    # Filter negara dengan opsi Pilih Semua
    daftar_negara = sorted(df['Nama_Negara'].unique())
    pilih_semua_negara = st.checkbox("Pilih Semua Negara", value=True)
    if pilih_semua_negara:
        pilih_negara = daftar_negara
    else:
        pilih_negara = st.multiselect("Pilih Negara", daftar_negara, default=daftar_negara[:5] if len(daftar_negara) > 5 else daftar_negara)
    
    # Filter kelompok usia dengan opsi Pilih Semua
    kelompok_usia = sorted(df['Kelompok_Usia'].unique())
    pilih_semua_usia = st.checkbox("Pilih Semua Kelompok Usia", value=True)
    if pilih_semua_usia:
        pilih_usia = kelompok_usia
    else:
        pilih_usia = st.multiselect("Pilih Kelompok Usia", kelompok_usia, default=kelompok_usia)
    
    # Filter kategori risiko dengan opsi Pilih Semua
    daftar_risiko = ['Risiko Tinggi', 'Risiko Rendah']
    pilih_semua_risiko = st.checkbox("Pilih Semua Kategori Risiko", value=True)
    if pilih_semua_risiko:
        pilih_risiko = daftar_risiko
    else:
        pilih_risiko = st.multiselect("Pilih Kategori Risiko", daftar_risiko, default=daftar_risiko)
    
    # Tombol Reset Filter
    if st.button("Reset Semua Filter"):
        st.session_state.clear()
        st.experimental_rerun()
    
    # Terapkan filter
    data_filter = df[
        df['Nama_Negara'].isin(pilih_negara) &
        df['Kelompok_Usia'].isin(pilih_usia) &
        df['Kategori_Risiko'].isin(pilih_risiko)
    ]
    
    st.divider()
    st.caption(f"Menampilkan {len(data_filter):,} dari {len(df):,} pelanggan")

# === HITUNG ANGKA PENTING ===
jumlah_pelanggan = len(data_filter)
laki = data_filter[data_filter['Jenis_Kelamin'] == 'Laki-laki'].shape[0]
perempuan = data_filter[data_filter['Jenis_Kelamin'] == 'Perempuan'].shape[0]
rata_rata_pendapatan = data_filter['TotalPrice'].mean()
rata_rata_recency = data_filter['Recency'].mean()
pelanggan_berisiko = data_filter['Predicted_Churn'].sum()
persen_berisiko = (pelanggan_berisiko / jumlah_pelanggan) * 100 if jumlah_pelanggan > 0 else 0

# === JUDUL & METRIK UTAMA ===
st.markdown("# 📊 Dashboard Pelanggan & Prediksi Berhenti Belanja")
st.markdown("_Melihat kondisi pelanggan saat ini dan risiko mereka berhenti belanja_")

kolom = st.columns(5)
kolom[0].metric("Jumlah Pelanggan", f"{jumlah_pelanggan:,}")
kolom[1].metric("Laki-laki / Perempuan", f"{laki:,} / {perempuan:,}")
kolom[2].metric("Rata-rata Pendapatan", f"Rp {rata_rata_pendapatan:,.0f}")
kolom[3].metric("Rata-rata Lama Tidak Belanja", f"{rata_rata_recency:.0f} hari")
kolom[4].metric("Prediksi Berhenti Belanja", f"{persen_berisiko:.1f}%", 
                delta=f"+{persen_berisiko - 30:.1f}%" if persen_berisiko > 30 else None,
                delta_color="inverse" if persen_berisiko > 30 else "normal")

# === TAB NAVIGASI ===
tab1, tab2, tab3 = st.tabs(["👥 Data Pelanggan", "⚠️ Analisis Risiko Berhenti", "🚨 Daftar Pelanggan Berisiko"])

with tab1:
    kiri, kanan = st.columns(2)
    
    with kiri:
        st.subheader("Perbandingan Jenis Kelamin")
        pie_gender = px.pie(values=[laki, perempuan], names=['Laki-laki', 'Perempuan'],
                            color_discrete_sequence=['#2C3E50', '#FF6B9D'], hole=0.4)
        pie_gender.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(pie_gender, use_container_width=True)
        
        st.subheader("Kelompok Pendapatan")
        pie_pendapatan = px.pie(data_filter['Kelompok_Pendapatan'].value_counts(),
                                names=data_filter['Kelompok_Pendapatan'].value_counts().index,
                                hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        pie_pendapatan.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(pie_pendapatan, use_container_width=True)
    
    with kanan:
        st.subheader("Jumlah Pelanggan per Kelompok Usia")
        usia_jk = pd.crosstab(data_filter['Kelompok_Usia'], data_filter['Jenis_Kelamin']).reset_index()
        bar_usia = px.bar(usia_jk, x='Kelompok_Usia', y=['Perempuan', 'Laki-laki'],
                          color_discrete_sequence=['#FF6B9D', '#2C3E50'],
                          barmode='group')
        st.plotly_chart(bar_usia, use_container_width=True)
        
        st.subheader("Skor Kredit Pelanggan")
        pie_kredit = px.pie(data_filter['Skor_Kredit'].value_counts(),
                            names=data_filter['Skor_Kredit'].value_counts().index,
                            hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        pie_kredit.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(pie_kredit, use_container_width=True)

with tab2:
    kiri, kanan = st.columns(2)
    
    with kiri:
        st.subheader("Risiko Berhenti per Kelompok Usia")
        risiko_usia = data_filter.groupby('Kelompok_Usia')['Predicted_Churn'].mean() * 100
        bar_risiko_usia = px.bar(x=risiko_usia.index, y=risiko_usia.values,
                                 color=risiko_usia.values, color_continuous_scale='Reds',
                                 labels={'y': 'Risiko Berhenti (%)'})
        bar_risiko_usia.update_layout(showlegend=False)
        st.plotly_chart(bar_risiko_usia, use_container_width=True)
        
        st.subheader("Ringkasan Kategori Risiko")
        pie_risiko = px.pie(values=data_filter['Kategori_Risiko'].value_counts(),
                            names=['Risiko Rendah', 'Risiko Tinggi'],
                            color_discrete_sequence=['#27AE60', '#E74C3C'], hole=0.5)
        pie_risiko.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(pie_risiko, use_container_width=True)
    
    with kanan:
        st.subheader("Risiko Berhenti per Kelompok Pendapatan")
        risiko_pendapatan = data_filter.groupby('Kelompok_Pendapatan')['Predicted_Churn'].mean() * 100
        bar_risiko_pendapatan = px.bar(x=risiko_pendapatan.index, y=risiko_pendapatan.values,
                                       color=risiko_pendapatan.values, color_continuous_scale='Oranges',
                                       labels={'y': 'Risiko Berhenti (%)'})
        bar_risiko_pendapatan.update_layout(showlegend=False)
        st.plotly_chart(bar_risiko_pendapatan, use_container_width=True)

with tab3:
    st.subheader("🚨 Daftar Pelanggan yang Diprediksi Akan Berhenti")
    berisiko = data_filter[data_filter['Predicted_Churn'] == 1].copy()
    berisiko = berisiko[['CustomerID', 'Nama_Negara', 'Kelompok_Usia', 'Kelompok_Pendapatan', 'TotalPrice', 'Recency']]
    berisiko['TotalPrice'] = berisiko['TotalPrice'].map('Rp {:,.0f}'.format)
    berisiko = berisiko.rename(columns={
        'CustomerID': 'ID Pelanggan',
        'Nama_Negara': 'Negara',
        'Kelompok_Usia': 'Usia',
        'Kelompok_Pendapatan': 'Pendapatan',
        'TotalPrice': 'Total Belanja',
        'Recency': 'Hari Tidak Belanja'
    })
    
    st.dataframe(berisiko, use_container_width=True, height=500)
    
    if not berisiko.empty:
        csv = berisiko.to_csv(index=False).encode()
        st.download_button("📥 Unduh Daftar Pelanggan Berisiko", csv, "pelanggan_berisiko.csv", "text/csv")

# === RINGKASAN & SARAN ===
st.markdown("---")
st.header("📌 Ringkasan & Saran Tindakan")

kiri, kanan = st.columns(2)

with kiri:
    st.subheader("Temuan Utama")
    usia_paling_berisiko = data_filter.groupby('Kelompok_Usia')['Predicted_Churn'].mean().idxmax()
    st.markdown(f"""
    - **Jumlah pelanggan saat ini:** {jumlah_pelanggan:,} orang
    - **Prediksi akan berhenti:** {persen_berisiko:.1f}% ({pelanggan_berisiko:,} orang berisiko tinggi)
    - **Kelompok usia paling rawan:** {usia_paling_berisiko}
    - **Rata-rata pendapatan:** Rp {rata_rata_pendapatan:,.0f}
    - **Rata-rata lama tidak belanja:** {rata_rata_recency:.0f} hari
    """)

with kanan:
    st.subheader("Saran Tindakan")
    st.markdown("""
    **Langkah yang bisa segera dilakukan:**
    - Kirim **email atau promo khusus** untuk pelanggan yang sudah >90 hari tidak belanja
    - Beri **diskon spesial** untuk kelompok pendapatan rendah & menengah bawah
    - Perkuat **program loyalitas** untuk usia 41-70 tahun (jumlah besar + risiko tinggi)
    - Pantau terus pelanggan yang jarang transaksi

    **Target:** Turunkan angka pelanggan berhenti sebanyak **15-20%** dalam 3 bulan ke depan
    """)
    st.success("Mempertahankan pelanggan lama jauh lebih murah daripada mencari pelanggan baru!")

# Footer
st.markdown("---")
st.caption("Dashboard BI Streamlit • UAS Business Intelegent • Kelompok 5")
