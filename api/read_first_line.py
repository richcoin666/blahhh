import PyPDF2
from flask import Request, jsonify

def handler(request: Request):
    try:
        file = request.files['file']
        reader = PyPDF2.PdfReader(file)
        first_line = reader.pages[0].extract_text().split('\n')[0]
        return jsonify({"message": f"Hey, your first line in your document is {first_line}"})
    except Exception as e:
        return jsonify({"error": f"Error from Vercel: {str(e)}"}), 500