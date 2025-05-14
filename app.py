import streamlit as st
import easyocr
import pandas as pd
import tempfile
from PIL import Image
import os

# Inisialisasi EasyOCR reader
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

# Fungsi ekstraksi field dari teks OCR
import re

def extract_fields_from_text(text):
    lines = text.splitlines()
    fields = {
        "Name": "",
        "Date of Birth": "",
        "Place of Birth": "",
        "Passport No": "",
        "Expired Date": ""
    }

    for i, line in enumerate(lines):
        line_lower = line.lower()

        if "name" in line_lower or "姓名" in line:
            # Ambil 1–2 baris berikutnya
            next_line = lines[i+1] if i+1 < len(lines) else ""
            second_line = lines[i+2] if i+2 < len(lines) else ""
            fields["Name"] = f"{next_line.strip()} / {second_line.strip()}".strip(" /")

        elif "passport" in line_lower and "no" in line_lower:
            fields["Passport No"] = lines[i+1].strip() if i+1 < len(lines) else ""

        elif "birth" in line_lower and "date" in line_lower:
            fields["Date of Birth"] = lines[i+1].strip() if i+1 < len(lines) else ""

        elif "place of birth" in line_lower or "出生地点" in line:
            fields["Place of Birth"] = lines[i+1].strip() if i+1 < len(lines) else ""

        elif "expiry" in line_lower or "有效期至" in line:
            fields["Expired Date"] = lines[i+1].strip() if i+1 < len(lines) else ""

    return fields

# Streamlit App
st.set_page_config(page_title="Passport OCR App", layout="centered")
st.title("🛂 Passport OCR Extractor")
st.markdown("Ekstrak informasi penting dari gambar paspor.")

uploaded_file = st.file_uploader("Unggah gambar paspor (JPEG/PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    image = Image.open(tmp_path)
    st.image(image, caption='Gambar Diunggah', use_column_width=True)

    with st.spinner("🔍 Menjalankan OCR..."):
        results = reader.readtext(tmp_path)
        ocr_text = "\n".join([res[1] for res in results])
        st.text_area("📄 Hasil OCR Mentah", ocr_text, height=300)

        fields = extract_fields_from_text(ocr_text)

        st.markdown("### 📌 Hasil Ekstraksi")
        df = pd.DataFrame([fields])
        st.dataframe(df)

        # Simpan ke Excel
        output_excel = "hasil_ekstraksi.xlsx"
        df.to_excel(output_excel, index=False)
        with open(output_excel, "rb") as f:
            st.download_button("📥 Unduh Hasil Excel", data=f, file_name="passport_data.xlsx")

        # Bersihkan file sementara
        os.remove(tmp_path)
