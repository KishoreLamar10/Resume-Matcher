from PyPDF2 import PdfReader

def extract_text_from_resume(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        return " ".join(page.extract_text() for page in reader.pages if page.extract_text())
    return uploaded_file.read().decode("utf-8")
