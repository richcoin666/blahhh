from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import PyPDF2
import requests
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/read")
async def read_file_url(request: Request):
    try:
        data = await request.json()
        file_url = data.get("fileUrl")

        if not file_url:
            return JSONResponse({"error": "No fileUrl provided"}, status_code=400)

        # Download the file
        pdf_response = requests.get(file_url)
        pdf_response.raise_for_status()

        # Parse PDF from bytes
        pdf_bytes = io.BytesIO(pdf_response.content)
        reader = PyPDF2.PdfReader(pdf_bytes)

        first_line = reader.pages[0].extract_text().split('\n')[0]

        return JSONResponse({"message": f"Hey, your first line is: {first_line}"})

    except Exception as e:
        return JSONResponse({"error": f"Failed to process PDF: {str(e)}"}, status_code=500)
