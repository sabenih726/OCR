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
    name = re.search(r'姓名.*?\n(.*)', text)
    dob = re.search(r'(Date of Birth|Date cf birth|Date of birth).*?\n([^\n]+)', text, re.IGNORECASE)
    pob = re.search(r'(出生地点|Place of birth).*?\n(.*)', text, re.IGNORECASE)
    passport = re.search(r'Passport\s*No.*?\n(.*)', text, re.IGNORECASE)
    expiry = re.search(r'(Date Of expiry|有效期至).*?\n(.*)', text, re.IGNORECASE)

    return {
        "Name": name.group(1).strip() if name else "",
        "Date of Birth": dob.group(2).strip() if dob else "",
        "Place of Birth": pob.group(2).strip() if pob else "",
        "Passport No": passport.group(1).strip() if passport else "",
        "Expired Date": expiry.group(2).strip() if expiry else ""
    }

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
