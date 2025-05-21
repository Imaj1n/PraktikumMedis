import streamlit as st
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd

# def auto_grid(uploaded_file, channel='red'):
#     st.title("📸 Ukur Piksel Otomatis")
#     if uploaded_file:
#         # Slider untuk threshold
#         threshold_value = st.slider("Threshold", 0, 255, 5)

#         # Slider untuk margin visualisasi & ROI
#         shrink_margin = st.slider("Margin ROI dari bounding box (px)", 0, 50, 5)

#         # Load gambar sebagai RGB
#         image = Image.open(uploaded_file).convert('RGB')
#         img_rgb = np.array(image)
#         img_color = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)  # Untuk tampilan dan drawing box

#         # Ambil hanya kanal yang dipilih
#         if channel == 'red':
#             img_channel = img_color[:, :, 2]  # Merah di index ke-2 (BGR)
#         elif channel == 'green':
#             img_channel = img_color[:, :, 1]  # Hijau di index ke-1
#         elif channel == 'blue':
#             img_channel = img_color[:, :, 0]  # Biru di index ke-0
#         else:
#             return st.error("Channel tidak dikenali. Gunakan: 'red', 'green', atau 'blue'.")

#         # Threshold pada kanal yang dipilih
#         _, thresh = cv2.threshold(img_channel, threshold_value, 255, cv2.THRESH_BINARY)

#         # Temukan kontur
#         contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         rois = []
#         stats = []

#         for cnt in contours:
#             approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
#             if len(approx) == 4:
#                 x, y, w, h = cv2.boundingRect(cnt)

#                 # Gambar kotak hijau (asli)
#                 cv2.rectangle(img_color, (x, y), (x+w, y+h), (0, 255, 0), 2)

#                 # Kotak kecil (ROI biru)
#                 shrink_x = max(x + shrink_margin, 0)
#                 shrink_y = max(y + shrink_margin, 0)
#                 shrink_w = max(w - 2 * shrink_margin, 1)
#                 shrink_h = max(h - 2 * shrink_margin, 1)

#                 if shrink_x + shrink_w <= img_channel.shape[1] and shrink_y + shrink_h <= img_channel.shape[0]:
#                     cv2.rectangle(img_color, (shrink_x, shrink_y), (shrink_x + shrink_w, shrink_y + shrink_h), (255, 0, 0), 2)

#                     roi = img_channel[shrink_y:shrink_y+shrink_h, shrink_x:shrink_x+shrink_w]

                    
#                     rois.append(((shrink_x, shrink_y, shrink_w, shrink_h), roi))

#                     mean = np.mean(roi)
#                     min_val = np.min(roi)
#                     max_val = np.max(roi)
#                     area = roi.size

#                     stats.append({
#                         "ROI #": len(stats) + 1,
#                         "Area": area,
#                         "Mean": round(mean, 2),
#                         "Min": int(min_val),
#                         "Max": int(max_val)
#                     })

#         cola, colb = st.columns(2)
#         with cola:
#             st.subheader(f"Hasil Deteksi Persegi Panjang - {channel.capitalize()}")
#             fig, ax = plt.subplots()
#             ax.imshow(cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB))
#             ax.axis('off')
#             st.pyplot(fig)

#         with colb:
#             if not rois:
#                 return st.warning("Tidak ditemukan objek berbentuk persegi panjang yang sesuai.")
#             else:
#                 stats_df = pd.DataFrame(stats)
#                 st.subheader(f"Tabel Statistik ROI")
#                 st.dataframe(stats_df)
#                 return stats_df

import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tempfile
import os
import pandas as pd
import matplotlib.pyplot as plt

def auto_grid(uploaded_file, channel='red'):
    st.title("📸 Ukur Piksel Otomatis")
    if uploaded_file:
        # Slider untuk threshold
        threshold_value = st.slider("Threshold", 0, 65535, 5)  # Ubah threshold untuk 16-bit
        # Slider untuk margin visualisasi & ROI
        shrink_margin = st.slider("Margin ROI dari bounding box (px)", 0, 50, 5)

        # Simpan gambar sementara untuk dibaca dengan OpenCV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Baca gambar dengan OpenCV tanpa mengubah bit-depth
        img_raw = cv2.imread(tmp_path, cv2.IMREAD_UNCHANGED)  # Membaca gambar dengan bit-depth asli
        print("Tipe gambar:", img_raw.dtype)  # Pastikan dtype-nya uint16 jika 16-bit

        # Periksa apakah gambar berwarna (RGB) atau grayscale
        if len(img_raw.shape) == 3:  # RGB / multi-channel
            if channel == 'red':
                img_channel = img_raw[:, :, 2]  # Kanal merah di OpenCV (BGR)
            elif channel == 'green':
                img_channel = img_raw[:, :, 1]  # Kanal hijau di OpenCV (BGR)
            elif channel == 'blue':
                img_channel = img_raw[:, :, 0]  # Kanal biru di OpenCV (BGR)
            else:
                st.error("Channel tidak dikenali. Gunakan: 'red', 'green', atau 'blue'.")
                return
        else:  # Jika gambar grayscale
            img_channel = img_raw

        # Threshold pada kanal yang dipilih (65535 untuk gambar 16-bit)
        _, thresh = cv2.threshold(img_channel, threshold_value, 65535, cv2.THRESH_BINARY)

        # Konversi hasil threshold (16-bit) menjadi 8-bit agar bisa diproses oleh findContours
        thresh_8bit = np.uint8(thresh / 256)  # Ubah 16-bit menjadi 8-bit (menyusutkan rentang)

        # Temukan kontur (gunakan cv2.RETR_EXTERNAL untuk menemukan objek utama)
        contours, _ = cv2.findContours(thresh_8bit, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        rois = []
        stats = []

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(cnt)

                # Gambar kotak hijau (asli)
                cv2.rectangle(img_raw, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Kotak kecil (ROI biru)
                shrink_x = max(x + shrink_margin, 0)
                shrink_y = max(y + shrink_margin, 0)
                shrink_w = max(w - 2 * shrink_margin, 1)
                shrink_h = max(h - 2 * shrink_margin, 1)

                if shrink_x + shrink_w <= img_channel.shape[1] and shrink_y + shrink_h <= img_channel.shape[0]:
                    cv2.rectangle(img_raw, (shrink_x, shrink_y), (shrink_x + shrink_w, shrink_y + shrink_h), (255, 0, 0), 2)

                    roi = img_channel[shrink_y:shrink_y+shrink_h, shrink_x:shrink_x+shrink_w]
                    rois.append(((shrink_x, shrink_y, shrink_w, shrink_h), roi))

                    mean = np.mean(roi)
                    min_val = np.min(roi)
                    max_val = np.max(roi)
                    area = roi.size

                    stats.append({
                        "ROI #": len(stats) + 1,
                        "Area": area,
                        "Mean": round(mean, 2),
                        "Min": int(min_val),
                        "Max": int(max_val)
                    })

        # Hapus file sementara setelah proses selesai
        os.remove(tmp_path)

        # Menampilkan hasil
        cola, colb = st.columns(2)
        with cola:
            st.subheader(f"Hasil Deteksi Persegi Panjang - {channel.capitalize()}")
            fig, ax = plt.subplots()
            ax.imshow(cv2.cvtColor(img_raw, cv2.COLOR_BGR2RGB))
            ax.axis('off')
            st.pyplot(fig)

        with colb:
            if not rois:
                return st.warning("Tidak ditemukan objek berbentuk persegi panjang yang sesuai.")
            else:
                stats_df = pd.DataFrame(stats)
                st.subheader(f"Tabel Statistik ROI")
                st.dataframe(stats_df)
                return stats_df
