import streamlit as st
import pandas as pd
import json, re, os
from PIL import Image
import google.generativeai as genai

# --------------------------------------------
# 🔑 Configure Gemini API Key
# --------------------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the model
model = genai.GenerativeModel("gemini-2.5-flash")

# --------------------------------------------
# 🎨 Streamlit UI
# --------------------------------------------
st.set_page_config(page_title="Patient Register Extractor", page_icon="📄", layout="wide")

st.title("📄 Patient Register Extractor (Gemini Vision)")
st.markdown("Upload handwritten or scanned **patient registers** and extract structured data automatically into Excel.")

uploaded_files = st.file_uploader("📸 Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

if uploaded_files:
    all_data = []
    progress = st.progress(0)

    for i, file in enumerate(uploaded_files, start=1):
        st.write(f"🖼️ Processing file: `{file.name}` ...")
        image = Image.open(file)

        prompt = """
        Extract patient data from the image as a JSON array.
        Each object must have these fields:
        - Date
        - Name
        - Age
        - Mobile No
        - Amount

        If a value is missing, write 'NA'.
        Correct common OCR mistakes:
        'Sanjana' → 'Ranjana'
        'Satyashankar' → 'Vijay Shankar'
        Output only valid JSON.
        """

        # Gemini Vision API call
        response = model.generate_content([prompt, image])
        text = response.text.strip()

        # JSON clean-up
        try:
            data = json.loads(text)
        except:
            json_match = re.search(r"\[.*\]", text, re.S)
            data = json.loads(json_match.group(0)) if json_match else []

        df = pd.DataFrame(data)
        df["SourceFile"] = file.name
        all_data.append(df)

        progress.progress(i / len(uploaded_files))

    # Combine all results
    combined = pd.concat(all_data, ignore_index=True)
    st.subheader("📊 Extracted Records")
    st.dataframe(combined)

    # Save and allow download
    excel_path = "Patient_Records.xlsx"
    combined.to_excel(excel_path, index=False)

    with open(excel_path, "rb") as f:
        st.download_button("⬇️ Download Excel", f, file_name="Patient_Records.xlsx", mime="application/vnd.ms-excel")

st.markdown("---")
st.caption("Built with ❤️ using Google Gemini Vision & Streamlit")
