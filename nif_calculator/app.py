from flask import Flask, render_template, jsonify, request
import requests
import logging
import os

from nif_calculator.helper import NIFAnnotator

app = Flask(__name__)

# Configure logging level based on APP_DEBUG environment variable
if os.getenv('APP_DEBUG') == '1':
    app.logger.setLevel('DEBUG')
else:
    app.logger.setLevel('WARNING')

@app.route('/')
def index():
    app.logger.info("Accessed index page.")
    return render_template('index.html')

@app.route('/faq')
def faq():
    app.logger.info("Accessed FAQ page.")
    return render_template('faq.html')

@app.route('/api/health', methods=['GET'])
def health():
    app.logger.debug("Health check requested.")
    response = {
        'status': 'success'
    }
    app.logger.debug("Health check response: %s", response)
    return jsonify(response)

@app.route('/api/generate_nif_table', methods=['GET'])
def generate_nif_table():
    app.logger.debug("generate_nif_table API called.")
    sequence = request.args.get('sequence')
    
    if not sequence:
        app.logger.warning("Missing 'sequence' parameter in request.")
        return jsonify({'error': '"sequence" parameter is required'}), 400
    
    try:
        app.logger.info(f"Generating NIF table for sequence: {sequence}")
        nif_annotator = NIFAnnotator(sequence=sequence)
        nif_table = nif_annotator.get_nif_table()
        app.logger.debug(f"NIF table generated: {nif_table}")
        return jsonify(nif_table)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error while generating NIF table: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.logger.info("Starting Flask app.")
    debug_mode = os.getenv('APP_DEBUG') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)
