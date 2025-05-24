from flask import Request, jsonify
import requests
import PyPDF2
from io import BytesIO

def handler(request: Request):
    try:
        data = request.get_json()
        file_url = data.get("fileUrl")

        if not file_url:
            return jsonify({"error": "Missing fileUrl"}), 400

        # Fetch file
        response = requests.get(file_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch file"}), 500

        # Read PDF from content
        reader = PyPDF2.PdfReader(BytesIO(response.content))
        if not reader.pages:
            return jsonify({"error": "No pages found in PDF"}), 400

        # Get first line from first page
        text = reader.pages[0].extract_text()
        if not text:
            return jsonify({"error": "No text extracted"}), 400

        first_line = text.strip().split('\n')[0]
        return jsonify({"firstLine": first_line}), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500