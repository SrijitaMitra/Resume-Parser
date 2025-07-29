import streamlit as st
import pdfplumber
from docx import Document
import re
import spacy
import pandas as pd

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract raw text from uploaded file
def extract_text(file):
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() or '' for page in pdf.pages)
    elif file.name.endswith('.docx'):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return "Unsupported file format."

# Function to parse key details from resume text
def parse_resume(text):
    parsed = {}
    doc = nlp(text)

    parsed['Email'] = re.findall(r'\S+@\S+', text)
    parsed['Phone'] = re.findall(r'\+?\d[\d -]{8,}\d', text)
    parsed['Name'] = doc.ents[0].text if doc.ents else "Not Found"
    parsed['Skills'] = list(set([token.text for token in doc if token.pos_ == 'NOUN' and token.is_alpha and len(token.text) > 2]))

    return parsed

# Streamlit UI
st.set_page_config(page_title="Resume Parser", layout="centered")
st.title("\U0001F4C4 AI Resume Parser")
st.markdown("Upload a resume (PDF or DOCX) and extract candidate details.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file:
    text = extract_text(uploaded_file)
    st.subheader("Extracted Text")
    st.text_area("Raw Resume Text", text, height=250)

    st.subheader("Parsed Information")
    parsed_info = parse_resume(text)
    st.json(parsed_info)

    if st.button("Save to CSV"):
        df = pd.DataFrame([parsed_info])
        df.to_csv("parsed_resumes.csv", mode='a', header=False, index=False)
        st.success("Saved to parsed_resumes.csv")
