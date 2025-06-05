from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import fitz  # PyMuPDF
from docx import Document
import os
import tempfile
import json
import csv
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text().strip() + "\n"
        return text.strip() or "PDF is empty."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_docx(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        return text or "DOCX is empty."
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def read_txt(file_bytes):
    try:
        return file_bytes.decode('utf-8').strip() or "TXT file is empty."
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def read_json(file_bytes):
    try:
        data = json.loads(file_bytes.decode('utf-8'))
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error reading JSON: {str(e)}"

def read_csv(file_bytes):
    try:
        text_io = io.StringIO(file_bytes.decode('utf-8'))
        reader = csv.reader(text_io)
        rows = ["\t".join(row) for row in reader]
        return "\n".join(rows) or "CSV is empty."
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

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

        content_type = response.headers.get("content-type", "").lower()
        content = response.content

        # Determine file type
        extension = None
        if any(ext in file_url for ext in [".pdf"]) or "pdf" in content_type:
            extension = "pdf"
        elif any(ext in file_url for ext in [".docx"]) or "word" in content_type:
            extension = "docx"
        elif any(ext in file_url for ext in [".txt"]) or "text/plain" in content_type:
            extension = "txt"
        elif any(ext in file_url for ext in [".json"]) or "application/json" in content_type:
            extension = "json"
        elif any(ext in file_url for ext in [".csv"]) or "csv" in content_type:
            extension = "csv"

        if not extension:
            return JSONResponse({"error": f"Unsupported file type: {content_type}"}, status_code=400)

        # Read file based on type
        if extension == "pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            result = read_pdf(tmp_path)
            os.remove(tmp_path)
        elif extension == "docx":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            result = read_docx(tmp_path)
            os.remove(tmp_path)
        elif extension == "txt":
            result = read_txt(content)
        elif extension == "json":
            result = read_json(content)
        elif extension == "csv":
            result = read_csv(content)
        else:
            result = "Unsupported file type."

        return JSONResponse({"message": result})

    except Exception as e:
        print("❌ Error in /api/read:", str(e))
        return JSONResponse({"error": str(e)}, status_code=500)
