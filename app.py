import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
import re

# Inisialisasi EasyOCR reader
reader = easyocr.Reader(['en', 'ch_sim'], gpu=False)

st.set_page_config(page_title="OCR Paspor", layout="centered")
st.title("🛂 Ekstraksi Data Paspor Otomatis")
st.write("Unggah gambar paspor (format JPEG/PNG) dan sistem akan mengekstrak data utama.")

# Upload gambar
uploaded_file = st.file_uploader("Unggah gambar paspor", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Gambar Paspor", use_column_width=True)

    # Konversi ke format numpy array untuk OCR
    img_array = np.array(image)

    # OCR processing
    st.info("🔍 Mengekstraksi teks...")
    result = reader.readtext(img_array, detail=0)

    full_text = "\n".join(result)
    st.text_area("📄 Hasil OCR Mentah", full_text, height=200)

    # Ekstraksi data dengan regex
    def extract_field(label, pattern):
        match = re.search(pattern, full_text, re.IGNORECASE)
        return match.group(1).strip() if match else "-"

    name = extract_field("Name", r"Name\s*[:\-]?\s*([A-Z,\s]+)")
    dob = extract_field("Date of birth", r"Date of birth\s*[:\-]?\s*(\d{1,2}\s\w+\s\d{4})")
    pob = extract_field("Place of birth", r"Place of birth\s*[:\-]?\s*([A-Z\s]+)")
    expiry = extract_field("Date of expiry", r"Date of expiry\s*[:\-]?\s*(\d{1,2}\s\w+\s\d{4})")
    passport_no = extract_field("Passport No", r"Passport No\.?\s*[:\-]?\s*([A-Z0-9]+)")

    st.markdown("### 🧾 Data Terstruktur")
    st.write(f"**Nama:** {name}")
    st.write(f"**Tempat Lahir (POB):** {pob}")
    st.write(f"**Tanggal Lahir (DOB):** {dob}")
    st.write(f"**Tanggal Kedaluwarsa:** {expiry}")
    st.write(f"**Nomor Paspor:** {passport_no}")
