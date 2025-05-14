import os
import easyocr
import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import io
import re

# Streamlit page setup
st.set_page_config(page_title="OCR Paspor China", layout="wide")
st.title("📄 OCR Paspor RRC (CN) - Multiple Upload + Export Excel")

# Buat folder model
MODEL_DIR = './models'
os.makedirs(MODEL_DIR, exist_ok=True)

# Load EasyOCR
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'ch_sim'], model_storage_directory=MODEL_DIR, gpu=False)

reader = load_reader()

# Upload multiple image files
uploaded_files = st.file_uploader("Unggah 1–20 gambar paspor (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Fungsi ekstraksi info dari OCR text
def extract_info(text):
    info = {}

    match_name = re.search(r"Name\s*\n*(.*)", text)
    if match_name:
        info["Name"] = match_name.group(1).strip()

    match_pob = re.search(r"Place of birth\s*\n*(.*)", text)
    if match_pob:
        info["Place of Birth"] = match_pob.group(1).strip()

    match_dob = re.search(r"Date of birth\s*\n*([\d]{1,2} \w+ \d{4})", text)
    if match_dob:
        info["Date of Birth"] = match_dob.group(1).strip()

    match_exp = re.search(r"Date of expiry\s*\n*([\d]{1,2} \w+ \d{4})", text)
    if match_exp:
        info["Date of Expiry"] = match_exp.group(1).strip()

    match_passport = re.search(r"Passport No\.?\s*\n*([A-Z0-9]+)", text)
    if match_passport:
        info["Passport Number"] = match_passport.group(1).strip()

    return info

# Proses setiap file
if uploaded_files:
    extracted_data = []

    for file in uploaded_files:
        st.markdown(f"---\n### 🖼️ {file.name}")
        image = Image.open(file)
        st.image(image, use_column_width=True)

        with st.spinner(f"🔍 Memproses {file.name}..."):
            image_np = np.array(image)
            results = reader.readtext(image_np, detail=0)
            full_text = "\n".join(results)
            st.text(full_text)

            info = extract_info(full_text)
            info["Filename"] = file.name
            extracted_data.append(info)

    # Tampilkan hasil di tabel
    df = pd.DataFrame(extracted_data)
    st.subheader("📊 Hasil Ekstraksi")
    st.dataframe(df)

    # Unduh sebagai Excel
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='OCR Results')
        return output.getvalue()

    excel_data = to_excel(df)
    st.download_button(
        label="📥 Unduh Hasil sebagai Excel",
        data=excel_data,
        file_name="hasil_ocr_paspor.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
