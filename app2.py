from flask import Flask, render_template, request, redirect, url_for, send_file
import PyPDF2
import os
from gtts import gTTS
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Language codes supported by gTTS
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ta': 'Tamil',
    'hi': 'Hindi',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'te': 'Telugu',
    'ur': 'Urdu',
    'ko': 'Korean'
}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return "No file uploaded", 400

    file = request.files['pdf']
    if file.filename == '':
        return "No selected file", 400

    if not file.filename.lower().endswith('.pdf'):
        return "Only PDF files are allowed", 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    selected_language = request.form.get('language')
    if selected_language not in LANGUAGES:
        return "Invalid language selected", 400

    try:
        # Extract text from PDF
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "

        if not text.strip():
            return "No readable text found in PDF", 400

        # Convert text to speech
        tts = gTTS(text=text, lang=selected_language)

        audio_name = filename.rsplit('.', 1)[0] + ".mp3"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_name)
        tts.save(audio_path)

        return redirect(url_for('download_file', filename=audio_name))

    except Exception as e:
        return f"Error processing PDF: {str(e)}", 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
