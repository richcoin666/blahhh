from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import io

app = FastAPI()

@app.post("/api/read")
async def read_first_line(file: UploadFile = File(...)):
    try:
        if file.content_type != "application/pdf":
            return JSONResponse({"error": "Only PDF files are supported."}, status_code=400)

        contents = await file.read()
        doc = fitz.open(stream=io.BytesIO(contents), filetype="pdf")

        text = ""
        for page in doc:
            text = page.get_text()
            if text.strip():
                break

        first_line = text.strip().splitlines()[0] if text.strip() else "No text found in PDF"
        return JSONResponse({"message": f"First line of the doc u submitted is: {first_line}"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)