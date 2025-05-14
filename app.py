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

    lines = text.split("\n")

    # Normalize all lines (remove extra spaces, lowercase for search)
    norm_lines = [line.strip() for line in lines]

    # Loop for Name
    for i, line in enumerate(norm_lines):
        if "姓名" in line or "name" in line.lower():
            # Expecting Hanzi and Latin name in next 1-2 lines
            possible_name = ""
            if i + 2 < len(norm_lines):
                hanzi = norm_lines[i + 1]
                latin = norm_lines[i + 2]
                possible_name = f"{hanzi} / {latin}"
            elif i + 1 < len(norm_lines):
                possible_name = norm_lines[i + 1]
            fields["Name"] = possible_name.strip()
            break

    # Passport No
    for line in norm_lines:
        match = re.search(r'\b[PA]?\d{7,9}\b', line)
        if match:
            fields["Passport No"] = match.group()
            break

    # Date of Birth
    for i, line in enumerate(norm_lines):
        if "birth" in line.lower():
            dob_match = re.search(r'\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}', norm_lines[i + 1] if i + 1 < len(norm_lines) else "", re.IGNORECASE)
            if dob_match:
                fields["Date of Birth"] = dob_match.group()
                break

    # Place of Birth
    for i, line in enumerate(norm_lines):
        if "place of birth" in line.lower() or "出生地点" in line:
            if i + 1 < len(norm_lines):
                fields["Place of Birth"] = norm_lines[i + 1]
                break

    # Expired Date
    for i, line in enumerate(norm_lines):
        if "expiry" in line.lower() or "有效" in line:
            match = re.search(r'\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}', line, re.IGNORECASE)
            if match:
                fields["Expired Date"] = match.group()
                break

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
