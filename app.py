import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import io
import re

st.set_page_config(page_title="Passport OCR", layout="wide")

st.title("📄 Passport OCR (China) - Extract Name, DOB, POB, Passport No, Expiry")

uploaded_files = st.file_uploader("Upload passport image(s)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

def extract_fields_tesseract(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
    data = data.dropna(subset=['text'])

    fields = {
        "Name": "",
        "Date of Birth": "",
        "Place of Birth": "",
        "Passport No": "",
        "Expired Date": "",
    }

    text = " ".join(data['text'].tolist())

    # Name
    name_match = re.search(r'姓名.?/?.?Name\s+(.+?)\s+([A-Z]+\s+[A-Z]+)', text)
    if name_match:
        fields["Name"] = f"{name_match.group(1).strip()} / {name_match.group(2).strip()}"
    else:
        # fallback: detect two-line Hanzi / Latin
        hanzi = ""
        latin = ""
        for i, row in data.iterrows():
            if "姓名" in row['text'] or "Name" in row['text']:
                if i+2 < len(data):
                    hanzi = data.iloc[i+1]['text']
                    latin = data.iloc[i+2]['text']
                break
        if hanzi and latin:
            fields["Name"] = f"{hanzi.strip()} / {latin.strip()}"

    # Passport No
    passport_match = re.search(r'\b[P]?\d{7,9}\b', text)
    if passport_match:
        fields["Passport No"] = passport_match.group()

    # Date of Birth
    dob_match = re.search(r'(\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{4})', text, re.IGNORECASE)
    if dob_match:
        fields["Date of Birth"] = dob_match.group(0)

    # Place of Birth
    pob_match = re.search(r'出生地点.?/?Place of birth\s+(.+?)(\s+[A-Z]+)?\s+Date', text)
    if pob_match:
        fields["Place of Birth"] = pob_match.group(1).strip()

    # Expired Date
    exp_match = re.findall(r'\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{4}', text, re.IGNORECASE)
    if len(exp_match) >= 2:
        # heuristik: tanggal kedua adalah expired
        exp_texts = re.findall(r'\d{1,2}\s+[A-Z]+\s+\d{4}', text)
        fields["Expired Date"] = exp_texts[1]

    return fields


if uploaded_files:
    results = []
    for uploaded_file in uploaded_files:
        st.markdown("---")
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

        image = Image.open(uploaded_file)
        fields = extract_fields_tesseract(image)
        results.append(fields)

        st.subheader("Extracted Info")
        st.json(fields)

    # Export to Excel
    df = pd.DataFrame(results)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Passport OCR")

    st.download_button("📥 Download Excel", data=buffer.getvalue(), file_name="passport_ocr.xlsx")

