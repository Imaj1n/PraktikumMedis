import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from streamlit_cropper import st_cropper
import pandas as pd

def manual_grid(uploaded_file, channel='red'):
    st.title("📸 Ukur Piksel Manual")

    # Inisialisasi session state
    if 'statistics_table' not in st.session_state:
        st.session_state.statistics_table = pd.DataFrame(columns=["ROI #", "Area", "Mean", "Min", "Max"])

    if uploaded_file:
        # Baca gambar yang diunggah
        image = Image.open(uploaded_file)

        # Konversi gambar ke 16-bit
        # Jika gambar 8-bit (mode 'RGB' atau 'L'), konversikan ke 16-bit dengan mengalikan nilai piksel dengan 256
        if image.mode == 'RGB':
            # Jika gambar berwarna, kita mengonversi setiap kanal menjadi 16-bit
            img_array = np.array(image)
            img_array_16bit = img_array.astype(np.uint16) * 256  # Mengubah ke format 16-bit
        elif image.mode == 'L':
            # Jika gambar grayscale, cukup perbesar nilainya ke 16-bit
            img_array = np.array(image)
            img_array_16bit = img_array.astype(np.uint16) * 256  # Mengubah ke format 16-bit
        else:
            st.error("Hanya gambar RGB atau grayscale yang dapat diubah ke 16-bit.")
            return

        col1, col2 = st.columns(2)

        with col1:
            try:
                # Cropper untuk memilih ROI manual
                cropped_image = st_cropper(
                    image,
                    realtime_update=True,
                    box_color="red",
                    aspect_ratio=None,
                )
            except Exception as e:
                st.error(f"⚠️ Gagal melakukan crop: {e}")
                cropped_image = None

            if cropped_image:
                # Konversi gambar terpotong menjadi array NumPy untuk analisis
                cropped_array = np.array(cropped_image)

                # Jika gambar asli adalah gambar 16-bit, kita gunakan gambar 16-bit yang sudah diproses
                cropped_array_16bit = cropped_array.astype(np.uint16) * 256  # Pastikan 16-bit

                # Pilih kanal berdasarkan input (merah, hijau, biru untuk gambar 16-bit)
                if channel == 'red':
                    channel_img = cropped_array_16bit[:, :, 0]  # Kanal merah pada gambar 16-bit
                elif channel == 'green':
                    channel_img = cropped_array_16bit[:, :, 1]  # Kanal hijau pada gambar 16-bit
                elif channel == 'blue':
                    channel_img = cropped_array_16bit[:, :, 2]  # Kanal biru pada gambar 16-bit
                else:
                    return st.error("Channel tidak dikenali. Gunakan: 'red', 'green', atau 'blue'.")

                # Hitung statistik pada ROI
                area = channel_img.size  # Ukuran ROI
                mean_val = channel_img.mean()  # Rata-rata nilai piksel
                min_val = channel_img.min()  # Nilai minimum piksel
                max_val = channel_img.max()  # Nilai maksimum piksel

                # Tambahkan ke tabel statistik
                roi_name = len(st.session_state.statistics_table) + 1
                new_stats = pd.DataFrame([[roi_name, area, mean_val, min_val, max_val]],
                                         columns=["ROI #", "Area", "Mean", "Min", "Max"])
                st.session_state.statistics_table = pd.concat([st.session_state.statistics_table, new_stats],
                                                              ignore_index=True)

        with col2:
            st.subheader("📋 Tabel Statistik ROI")
            st.write(st.session_state.statistics_table)

            # Tombol Reset
            if st.button("🔄 Reset Tabel Statistik"):
                st.session_state.statistics_table = pd.DataFrame(columns=["ROI #", "Area", "Mean", "Min", "Max"])
                st.success("Tabel statistik telah di-reset.")

    return st.session_state.statistics_table
