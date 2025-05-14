import streamlit as st
import easyocr
import pandas as pd
import tempfile
from PIL import Image
import os
import re

# Inisialisasi EasyOCR reader
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

# Fungsi ekstraksi field dari teks OCR
def extract_fields_from_text(text):
    fields = {
        "Name": "",
        "Date of Birth": "",
        "Place of Birth": "",
        "Passport No": "",
        "Expired Date": ""
    }

    # Ekstraksi Nama (setelah "姓名")
    name_match = re.search(r"姓名\s*/?\s*(.*?)\s*/?\s*HAN\s*YIN", text)
    if name_match:
        fields["Name"] = name_match.group(1).strip()

    # Ekstraksi Nomor Paspor (setelah "Passport No")
    passport_match = re.search(r"Passport No\s*/?\s*(\S+)", text)
    if passport_match:
        fields["Passport No"] = passport_match.group(1).strip()

    # Ekstraksi Tanggal Lahir (setelah "Date of birth")
    dob_match = re.search(r"Date cf birth\s*(\d{1,2} \w{3} \d{4})", text)
    if dob_match:
        fields["Date of Birth"] = dob_match.group(1).strip()

    # Ekstraksi Tempat Lahir (setelah "Place of birth")
    pob_match = re.search(r"出生地点\s*/?\s*(.*?)\s*/?", text)
    if pob_match:
        fields["Place of Birth"] = pob_match.group(1).strip()

    # Ekstraksi Tanggal Kadaluarsa (setelah "Date of expiry")
    expiry_match = re.search(r"Date Of expiry\s*/?\s*(\d{1,2} \w{3} \d{4})", text)
    if expiry_match:
        fields["Expired Date"] = expiry_match.group(1).strip()

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
