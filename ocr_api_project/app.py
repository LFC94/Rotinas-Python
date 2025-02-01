from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
import os
import re

app = Flask(__name__)

# Função para processar imagem e realizar OCR
def ocr_core(file_path):
    # Verifica se é um PDF
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path)
        text = ''
        for image in images:
            text += pytesseract.image_to_string(image, lang='por')
    else:
        # Processa a imagem se não for PDF
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='por')
    
    return text

# Função para classificar o tipo de documento com base no texto extraído
def classify_document(text):
    lower_text = text.lower()
    
    if 'cpf' in lower_text:
        return 'CPF'
    elif 'carteira de identidade' in lower_text or 'rg' in lower_text:
        return 'Identidade'
    elif 'diploma' in lower_text or 'universidade' in lower_text:
        return 'Diploma'
    elif 'nota fiscal' in lower_text or 'nfe' in lower_text:
        return 'Nota Fiscal'
    else:
        return 'Documento Desconhecido'

# Endpoint para receber o documento e realizar OCR
@app.route('/process-document', methods=['POST'])
def process_document():
    if 'document' not in request.files:
        return jsonify({"error": "Nenhum arquivo encontrado"}), 400
    
    file = request.files['document']
    file_path = os.path.join(os.getcwd(), file.filename) 
    file.save(file_path)

    # Realizar OCR
    text = ocr_core(file_path)
    
    # Classificar o tipo de documento
    document_type = classify_document(text)
    
    # Retornar o texto extraído e o tipo de documento
    return jsonify({
        "document_type": document_type,
        "extracted_text": text
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
