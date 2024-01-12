from quart import Quart, request, abort, current_app, jsonify, Response, render_template
from quart_cors import cors

import uuid
from threading import Thread, current_thread
from translator.pdf_parser import PDFParser
from utils import LOG
from urllib.parse import urlparse

app = Quart("Trasnlation")
app = cors(app, allow_origin="*")
threads = {}
results = {}
translation = {}

@app.route('/')
async def hello():
    url = request.url
    parsed_url = urlparse(url)
    host = parsed_url.hostname  # Get the host (including port if specified)
    port = parsed_url.port  # Get the port
    return await render_template('index.html', host=host, port=port)

@app.route('/jobs', methods=['GET'])
async def get_jobs():
    return results

@app.route('/jobs/<job_id>', methods=['GET'])
async def get_job(job_id):
    if job_id=="test":
        return jsonify({"test":"test"})
    if job_id in results:
        return results[job_id]
    else:
        abort(404)

@app.route('/translations/<job_id>', methods=['GET'])
async def get_translation(job_id):
    if job_id in translation:
        filename = translation[job_id]['filename']
        buffer = translation[job_id]['buffer']
        buffer.seek(0)
        return Response(buffer, 
                        mimetype='application/pdf', 
                        headers={'Content-Disposition': f'inline; filename={filename}'})
    else:
        abort(404)

@app.route('/jobs', methods=['POST'])
async def create_job():
    print("Receive requests")
    files = await request.files
    formdata = await request.form
    if 'file' not in files:
        return jsonify({'error': 'No file part in the request'}), 400

    pdffile = files['file']
    # Check if the file is a PDF
    if pdffile.filename == '' or not pdffile.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid or no PDF file provided'}), 400

    file_format = formdata['file_format']
    to_lan = formdata['to_lan']
    style = formdata['style']
    translator = current_app.config.get("translator")
    
    if 'translator' not in current_app.config:
        return jsonify({'error': 'Translator not found'}), 500
    job_id = str(uuid.uuid4())

    t = Thread(target=translate_book, name=f"job_{job_id}", 
           kwargs={'job_id': job_id, 'translator': translator, 'pdffile': pdffile,
                   'file_format': file_format, 'to_lan':to_lan, 'style': style})
    threads[t.ident] = t
    j = {"job_id": job_id, "status": "Started"}
    results[job_id] = j
    t.start()
    return j
    
def translate_book(job_id, translator, pdffile, file_format, to_lan='Chinese', style = 'plain'):
    LOG.info("Start translate")
    results[job_id]['status'] = 'InProgress'
    try:
        buffer = translator.translate_pdf(pdffile, file_format, to_lan, style)
        results[job_id]['status'] = 'Finished'
        translation[job_id] = {
            'filename': pdffile.filename.replace('.pdf', f'_{to_lan}.{file_format}'),
            'buffer': buffer
        }
    except Exception as e:
        results[job_id]['status'] = 'Failed'
        results[job_id]['error_msg'] = str(e)
    LOG.info("Finish translate")

