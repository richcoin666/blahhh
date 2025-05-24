from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import fitz  # PyMuPDF
from docx import Document
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your Wix domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_pdf_first_line(file_path):
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text = page.get_text().strip()
            if text:
                return text.splitlines()[0]
        return "PDF is empty."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_docx_first_line(file_path):
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            if para.text.strip():
                return para.text.strip()
        return "DOCX is empty."
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

@app.post("/api/read")
async def read_file(request: Request):
    try:
        data = await request.json()
        file_url = data.get("fileUrl")

        if not file_url:
            return JSONResponse({"error": "Missing fileUrl"}, status_code=400)

        print("📥 Downloading file from:", file_url)
        response = requests.get(file_url)
        if response.status_code != 200:
            return JSONResponse({"error": "Failed to download file"}, status_code=400)

        content_type = response.headers.get("content-type", "")
        extension = ".pdf" if "pdf" in content_type else ".docx"
        temp_path = f"/tmp/temp_file{extension}"

        with open(temp_path, "wb") as f:
            f.write(response.content)

        if extension == ".pdf":
            first_line = read_pdf_first_line(temp_path)
        else:
            first_line = read_docx_first_line(temp_path)

        os.remove(temp_path)
        return JSONResponse({"message": first_line})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
