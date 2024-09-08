import os
import fitz
from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS, cross_origin
import nltk

nltk.download('punkt')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit
CORS(app)

# Initialize BERT pipelines
ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", grouped_entities=False)
relation_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")  # For Relation Extraction

UPLOAD_FOLDER = "/tmp"  # Folder to store uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def pdf_to_text(pdf_path):
    # Function to extract text from PDF using PyMuPDF (fitz)
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def split_into_sentences(text):
    # Function to split text into sentences using NLTK
    return nltk.sent_tokenize(text)


@app.route('/upload_pdf', methods=['POST'])
@cross_origin()
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the PDF file to a temporary folder
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Extract text from PDF
        text = pdf_to_text(pdf_path)

        # Split text into sentences for relationship extraction
        sentences = split_into_sentences(text)

        # Entity extraction using NER
        entities = ner_pipeline(text)

        # Extract entity information and ensure entities are unique
        entity_map = {}
        formatted_entities = []
        for entity in entities:
            label = entity['entity']
            title = entity['word'].strip()  # Strip whitespace from entity titles

            # Keep track of unique entities
            if title not in entity_map:
                entity_map[title] = label
                formatted_entities.append({
                    "label": label,
                    "title": title
                })

        # Relation extraction
        relations = []
        candidate_labels = ["related_to", "works_at", "founded", "partnered_with"]  # Example relations
        for sentence in sentences:
            result = relation_pipeline(sentence, candidate_labels=candidate_labels)
            for idx, label in enumerate(result['labels']):
                if result['scores'][idx] > 0.5:  # Only take relations with high confidence
                    relations.append({
                        "source": "unknown",  # Assuming you can identify source/target from sentence in future
                        "target": "unknown",
                        "type": label
                    })

        # Clean up the saved file after processing
        os.remove(pdf_path)

        # Return the extracted entities and relations
        return jsonify({"entities": formatted_entities, "relations": relations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
