from flask import Flask, render_template, request, send_file
import requests
import os
from fpdf import FPDF
from dotenv import load_dotenv
import io

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Access the loaded environment variables
api_key = os.getenv('Api_Key')

# Function to extract text from an image using OCR.space API
def extract_text(image):
    try:
        api_url = 'https://api.ocr.space/parse/image'
        file_extension = os.path.splitext(image.filename)[1].lower()
        valid_filetypes = ['jpg', 'jpeg', 'png']

        if file_extension[1:] in valid_filetypes:
            params = {
                'apikey': api_key,
                'filetype': file_extension[1:]
            }

            image_bytes = image.read()
            response = requests.post(api_url, files={'file': image_bytes}, data=params)

            result = response.json()

            if 'ParsedResults' in result:
                return result['ParsedResults'][0]['ParsedText']
            else:
                return 'Error in OCR.space API response'
        else:
            return 'Unsupported file type'
    except Exception as e:
        return str(e)

# Function to create a PDF with the organized information
def create_pdf(extracted_text):
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add a title
    pdf.cell(200, 10, txt="Extracted Information", ln=True, align='C')

    # Simulate the organized data extraction for a passport
    lines = extracted_text.split("\n")

    # Add organized info to the PDF
    for line in lines:
        if line.strip():
            pdf.cell(200, 10, txt=line, ln=True, align='L')

    # Save PDF to a BytesIO buffer
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    
    return buffer

# Main route for the app
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' in request.files:
            image = request.files['image']
            
            if image.filename != '':
                # Extract text from the image
                extracted_text = extract_text(image)
                
                # Generate PDF option
                if 'generate_pdf' in request.form:
                    pdf_buffer = create_pdf(extracted_text)
                    return send_file(pdf_buffer, as_attachment=True, download_name="extracted_info.pdf", mimetype='application/pdf')

                return extracted_text  # Just show extracted text as response in HTML
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
