from fastapi import FastAPI, Request
import requests
import fitz  # PyMuPDF for pdf reading

app = FastAPI()

@app.post("/api/read")
async def read_pdf(request: Request):
    data = await request.json()
    file_url = data.get("fileUrl")
    if not file_url:
        return {"error": "No file URL provided"}

    # Download PDF from Wix media url
    resp = requests.get(file_url)
    if resp.status_code != 200:
        return {"error": "Failed to download file"}

    pdf_data = resp.content

    # Read first line from PDF using PyMuPDF
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    first_page = doc.load_page(0)
    text = first_page.get_text("text").strip()
    first_line = text.split("\n")[0] if text else "Empty document"

    return {"message": f"Hey, your first line in your document is: {first_line}"}
