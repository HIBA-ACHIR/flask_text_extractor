from flask import Flask, render_template, request, send_file, jsonify
from passporteye import read_mrz
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from PIL import Image
import io
from datetime import datetime

app = Flask(__name__)

# Function to format dates to DD.MM.YYYY
def format_date(mrz_date_str):
    if mrz_date_str:
        try:
            # Assuming the input date is in YYMMDD format
            year = int(mrz_date_str[0:2])
            month = int(mrz_date_str[2:4])
            day = int(mrz_date_str[4:6])
            # Format year to two digits (assumed 1900s or 2000s)
            if year < 50:  # Assuming years less than 50 are in 2000s
                year += 2000
            else:
                year += 1900
            return f"{day:02d}/{month:02d}/{year % 100:02d}"  # Format as DD/MM/YY
        except ValueError:
            return mrz_date_str  # If the format doesn't match, return original
    return ""

# Function to process the image and extract MRZ data
def process_passport_image(image):
    try:
        # Convert the file to an image format recognized by passporteye
        img = Image.open(image)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        # Extract MRZ data from the image
        mrz = read_mrz(img_byte_arr)
        if mrz is None:
            return None, "Could not extract MRZ data. Make sure the image is a valid passport image."
        return mrz.to_dict(), None

    except Exception as e:
        return None, str(e)

# Function to generate a well-structured PDF with the extracted information
def generate_pdf(data):
    buffer = io.BytesIO()  # PDF is written to an in-memory buffer
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []

    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph("Passport MRZ Data", styles['Title']))
    story.append(Spacer(1, 20))

    # Organize the data in sections
    personal_info = [
        ['Name', data.get('names')],
        ['Surname', data.get('surname')],
        ['Date of Birth', format_date(data.get('date_of_birth'))],  # Format date here
        ['Nationality', data.get('nationality')],
        ['Sex', data.get('sex')]
    ]

    doc_info = [
        ['Document Type', data.get('type')],
        ['Document Number', data.get('number')],
        ['Issuing Country', data.get('country')],
        ['Expiration Date', format_date(data.get('expiration_date'))],  # Format date here
        ['MRZ Code', data.get('mrz')]
    ]

    # Add personal information section
    story.append(Paragraph("Personal Information", styles['Heading2']))
    personal_table = Table(personal_info)
    personal_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)]))
    story.append(personal_table)
    story.append(Spacer(1, 20))

    # Add document information section
    story.append(Paragraph("Document Information", styles['Heading2']))
    doc_table = Table(doc_info)
    doc_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige)]))
    story.append(doc_table)
    story.append(Spacer(1, 20))

    # Build PDF document
    doc.build(story)
    
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No file uploaded", 400

        image = request.files['image']
        if image.filename == '':
            return "No selected file", 400

        # Process the uploaded image to extract MRZ data
        mrz_data, error = process_passport_image(image)
        
        if error:
            return error

        # If "Generate PDF" button is pressed
        if 'generate_pdf' in request.form:
            pdf_file = generate_pdf(mrz_data)
            return send_file(pdf_file, as_attachment=True, download_name='passport_info.pdf', mimetype='application/pdf')

        # If "Extract MRZ Code" button is pressed
        if 'extract_mrz_code' in request.form:
            return jsonify({'mrz_code': mrz_data.get('mrz', 'MRZ code not found')})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

