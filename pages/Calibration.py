import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fungsi import polynomial_regression,str2int

# Mapping bagian tubuh
option_map = {
    0: "Brainstem (BS)",
    1: "Eye left (EL)",
    2: "Parotid left (PL)",
    3: "Spinal Cord",
    4: "Eye right (ER)",
}

# Data dosis aman per bagian tubuh (dalam cGy)
safe_dose_map = {
    0: [0, 540],    # Brainstem ≤ 54 Gy (5400 cGy)
    1: [0, 350],    # Eye left ≤ 35 Gy (3500 cGy), untuk menghindari efek samping ringan
    2: [0, 260],    # Parotid left ≤ 26 Gy (2600 cGy), rata-rata ideal untuk hindari xerostomia
    3: [0, 470],
    4: [0, 350],    # Eye right ≤ 35 Gy (3500 cGy)
}

# Data estimasi PDD untuk masing-masing organ (angka dalam persen)
pdd_map = {
    0: "80-88",  # Brainstem PDD
    1: "80-90",  # Eye left PDD
    2: "85-95",  # Parotid left PDD
    3: "70-80",
    4: "80-90",  # Eye right PDD
}



# Input segmented control
selection = st.segmented_control(
    "**Pilih bagian tubuh**",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)

if "tabel_merge" in st.session_state:
    # Tampilkan hasil jika data sudah ada di session_state
    if selection is not None:
        selected_part = option_map[selection]
        dose_range = safe_dose_map[selection]
        pdd_info = pdd_map[selection]
        
        st.write(f"Bagian tubuh: :violet-badge[{selected_part}]")
        st.markdown(f"Dosis radiasi yang direkomendasikan: :orange-badge[⚠️ {dose_range[0]} - {dose_range[1]}] cGy")
        st.markdown(f"Estimasi PDD: :blue-badge[{pdd_info}] %")

        # Ambil data dari session_state
        df = st.session_state["tabel_merge"]
        # st.dataframe(df)

        # Ambil nilai Mean dari dataframe
        mean = df["Mean"]
        
        # Tentukan dosis referensi berdasarkan rentang dosis yang dipilih
        
        # Perhitungan NetOD
        # netOD = np.abs(np.log10(mean[0] / mean))
        netOD = [np.abs(np.log10(mean[0] / mean[i])) for i in range(len(mean)) if mean[i]!= 0]
        dosis_ref = np.linspace(dose_range[0], dose_range[1], len(netOD))
        # st.write(netOD)
        pdd,_,_ = str2int(pdd_info)
        dosis_aktual = pdd*dosis_ref

        st.session_state.tabel_analisis = pd.DataFrame({
        "Dosis Referensi":dosis_ref,
        "Dosis Aktual":dosis_aktual,
        "rata rata piksel":[mean[i] for i in range(len(mean)) if (mean[i]!=0) or (i==0)],
        "netto OD":netOD
        })
        
        st.dataframe(st.session_state.tabel_analisis)
        

        netOD,dosis_aktual = np.array(netOD),np.array(dosis_aktual)
        model = polynomial_regression(netOD, dosis_aktual, degree=3)
        
        # Inisialisasi session_state untuk menyimpan data
        if "data_tabel" not in st.session_state:
            st.session_state.data_tabel = pd.DataFrame(columns=["Nama", "Usia", "Jenis Kelamin"])

        # Form input data
        st.subheader("Input Data")
        with st.form("form_input"):
            nama = st.selectbox("Bagian Tubuh", ["Brainstem", "Eye Left", "Parotid Left","Spinal Cord","Eye Right"])
            piksel = st.number_input("piksel", min_value=0, max_value=30000, step=1)
            dosis = st.number_input("Dosis", min_value=0.00, max_value=120.00, step=0.01)
            submit = st.form_submit_button("Kirim")

        # Jika form disubmit
        if submit:
            net_OD_fungsi = lambda x:np.abs(np.log10(mean[0]/x))
            galat = np.abs((model(net_OD_fungsi(piksel))-dosis)/dosis)*100
            # Tambahkan data ke session state
            new_data = {"Bagian Tubuh": nama, "net OD": net_OD_fungsi(piksel), "Dosis": dosis, "Galat (%)":galat}
            st.session_state.data_tabel = pd.concat(
                [st.session_state.data_tabel, pd.DataFrame([new_data])],
                ignore_index=True
            )
            st.success("Data berhasil ditambahkan!")
        # Tombol reset session state
        if st.button("Reset Data"):
            st.session_state.data_tabel = pd.DataFrame(columns=["Bagian Tubuh", "net OD", "Dosis", "Galat (%)"])
            st.success("Data berhasil direset!")

        # Tampilkan tabel data
        st.subheader("Tabel Data yang Sudah Dikirim")
        st.dataframe(st.session_state.data_tabel)


    else:
        st.warning("Silakan pilih bagian tubuh.")
else:
    st.warning("Data belum ada. Jalankan halaman utama terlebih dahulu.")

