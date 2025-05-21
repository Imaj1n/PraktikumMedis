import streamlit as st
import pandas as pd
from PIL import Image, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt
from auto import auto_grid
from manual import manual_grid


st.set_page_config(layout="wide")
st.title("☢️ Kalibrasi Film Dosimetri")

st.markdown('''



''')

st.text_area(
    "**Mengukur pixel**",
    '''pengukuran pixel hasil scan film dosimetri bisa menggunaan otomatis (menggunakan openCV) atau manual. Tabel hasil dari pengukuran otomatis dan manual akan digabung menjadi tabel otomatis
    
    '''
)
# Unggah gambar
uploaded_file = st.file_uploader("Unggah Gambar TIFF / PNG / JPG", type=["tiff", "png", "jpg", "jpeg"])


# Pilihan metode
genre = st.radio(
    "Pilih opsi pengukuran",
    [":red[otomatis]", ":blue[***manual***]"],
    captions=[
        "piksel dipilih secara otomatis",
        "piksel dipilih secara manual.",
    ],
)

# Jalankan dan simpan hasil ke session_state
if uploaded_file is not None:
    if genre == ":red[otomatis]":
        st.session_state.tabel_auto = auto_grid(uploaded_file)
    else:
        st.session_state.tabel_manual = manual_grid(uploaded_file)

# Ambil tabel dari session_state (jika sudah ada)
df_auto = st.session_state.get("tabel_auto")
df_manual = st.session_state.get("tabel_manual")

# Gabungkan otomatis jika salah satu atau dua tabel sudah ada
if df_auto is not None or df_manual is not None:
    # Pakai DataFrame kosong kalau belum ada
    df_auto = df_auto if df_auto is not None else pd.DataFrame()
    df_manual = df_manual if df_manual is not None else pd.DataFrame()

    # Tambahkan kolom sumber (opsional)
    if not df_auto.empty:
        df_auto["Sumber"] = "Otomatis"
    if not df_manual.empty:
        df_manual["Sumber"] = "Manual"

    # Gabungkan
    df_gabungan = pd.concat([df_auto, df_manual], ignore_index=True)

    # Tampilkan
    st.subheader("📊 Tabel Gabungan Otomatis:")
    st.dataframe(df_gabungan)
    st.session_state.tabel_merge = df_gabungan
else:
    st.info("Silakan pilih metode dan unggah gambar terlebih dahulu.")
