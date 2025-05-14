import streamlit as st
import easyocr
import pandas as pd
import re
from PIL import Image
import io

st.set_page_config(page_title="OCR Passport Extractor", layout="centered")

st.title("📄 OCR Passport Extractor (China Passport)")

uploaded_files = st.file_uploader("Upload passport images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

reader = easyocr.Reader(['en', 'ch_sim'], gpu=False)

def extract_fields(text: str):
    fields = {
        "Name": "",
        "Date of Birth": "",
        "Place of Birth": "",
        "Passport No": "",
        "Expired Date": "",
    }

    # Passport No
    passport_match = re.search(r'\b[PA]?\d{7,9}\b', text)
    if passport_match:
        fields["Passport No"] = passport_match.group()

    # Name
    name_match = re.search(r'姓名\s*/\s*Name\s*([\u4e00-\u9fff]+\s*[A-Z]+\s*[A-Z]+)', text)
    if name_match:
        fields["Name"] = name_match.group(1).strip()
    else:
        # fallback
        name_lines = [line for line in text.split('\n') if "Name" in line or "姓名" in line]
        if name_lines:
            fields["Name"] = name_lines[0].split()[-1]

    # Date of Birth
    dob_match = re.search(r'\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}', text, re.IGNORECASE)
    if dob_match:
        fields["Date of Birth"] = dob_match.group()

    # Place of Birth
    pob_match = re.search(r'(出生地点|Place of bin|Place of birth)\s*/?.*\n(.+)', text, re.IGNORECASE)
    if pob_match:
        fields["Place of Birth"] = pob_match.group(2).strip()

    # Expired Date
    exp_match = re.search(r'\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}', text, re.IGNORECASE)
    if exp_match:
        fields["Expired Date"] = exp_match.group()

    return fields

if uploaded_files:
    data = []

    for uploaded_file in uploaded_files:
        st.subheader(f"📷 Image: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        st.image(image, width=300)

        with st.spinner("🔍 Running OCR..."):
            result = reader.readtext(image, detail=0)
            text = "\n".join(result)
            st.text_area("📜 OCR Result", value=text, height=200)

            fields = extract_fields(text)
            data.append(fields)

    df = pd.DataFrame(data)
    st.subheader("🧾 Extracted Data")
    st.dataframe(df)

    # Export to Excel
    excel_bytes = io.BytesIO()
    with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 Download Excel", data=excel_bytes.getvalue(), file_name="passport_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
