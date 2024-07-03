from flask import Flask, request, jsonify
import threading
import os
from datetime import datetime, timedelta
import fitz
from traceback import format_exc
import re
import uuid
from dotenv import load_dotenv
load_dotenv()


from convert_pdf_to_image import extract_text
from prompt_model import get_info
app = Flask(__name__)

lock = threading.Lock()
is_executing = False






@app.before_request
def before_request():
    global is_executing
    if is_executing:
        return jsonify({"error": "Server is busy. Please try again later."}), 503

    with lock:
        is_executing = True

@app.after_request
def after_request(response):
    global is_executing
    with lock:
        is_executing = False
    return response














def get_creation_date(file_path):
    with open(file_path, 'rb') as file:
       pdf_document = fitz.open(stream=file.read(), filetype="pdf")
       metadata = pdf_document.metadata
       creation_date = metadata.get('creationDate')
   
       if creation_date:
           # Strip the prefix 'D:'
           creation_date = creation_date.strip('D:')
           # Handle timezone
           match = re.match(r'(\d{14})([+-]\d{2})\'(\d{2})\'', creation_date)
           if match:
               datetime_part, tz_hour, tz_minute = match.groups()
               creation_date = datetime.strptime(datetime_part, '%Y%m%d%H%M%S')
               tz_offset = int(tz_hour) * 60 + int(tz_minute)
               offset_delta = timedelta(minutes=tz_offset)
               if tz_hour.startswith('-'):
                   creation_date -= offset_delta
               else:
                   creation_date += offset_delta
               return creation_date.date().strftime('%Y-%m-%d')
           else:
               # Fallback if no timezone information
               creation_date = datetime.strptime(creation_date, '%Y%m%d%H%M%S')
               return creation_date.date().strftime('%Y-%m-%d')
    return "Unknown"



@app.route('/upload', methods=['POST'])
def upload_file():

    files = request.files.getlist('file')
   
    if len(files) == 0:
        return jsonify({'error': 'No file part'}), 400
    if len(files) > 1:
        return jsonify({'error': 'Multiple files uploaded. Only one file is allowed.'}), 400
    
    file = files[0]
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'File is not a PDF'}), 400

    try:
         # Save the file to disk
        file_name = str(uuid.uuid4()) + '.pdf'
        file_path = os.path.join(os.environ["UPLOAD_FOLDER"], file_name)
        file.save(file_path)

        d=get_info(*extract_text(file_path))
        creation_date=get_creation_date(file_path)
 

        d1={
        "file_name":file_name,
        "creation_date":creation_date
        }
        d.update(d1)
        return d
    except Exception as e:
        print(format_exc())
        return jsonify({'error': str(e), 'text': format_exc()}), 500

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=os.environ['PORT'])
#    app.run(debug=True, host="0.0.0.0")