import fitz  # PyMuPDF to read PDF files
from flask import Flask, jsonify, request
import torch
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from transformers import BertTokenizer, BertForTokenClassification
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Load BERT model and tokenizer for NER
tokenizer = BertTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
model = BertForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")

# Sentence Transformer for sentence embeddings (used for relation extraction)
relation_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Load BERT-based NER pipeline
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

stop_words = set(stopwords.words('english'))
# Helper function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    text = ""
    for page in doc:
        text += page.get_text()
    return text


# Helper function to extract entities using BERT
# Helper function to extract entities using BERT
def extract_entities(text):
    ner_results = ner_pipeline(text)

    # Filter out entities with a confidence score lower than 50%
    filtered_entities = {}
    for entity in ner_results:
        if entity['score'] > 0.50:
            entity_text = entity['word'].strip()  # Clean entity text
            if entity_text not in filtered_entities:  # Avoid duplicates
                filtered_entities[entity_text] = {"text": entity_text, "label": entity['entity_group']}

    return list(filtered_entities.values())  # Return as a list of unique entities

def extract_nouns(sentence):
    words = word_tokenize(sentence)
    tagged = pos_tag(words)
    nouns = [word for word, pos in tagged if pos.startswith('NN') and word.lower() not in stop_words]
    return nouns

# Helper function to extract relationships based on sentence embeddings
# Improved function to extract relationships based on sentence embeddings and entity co-occurrence
def extract_relationships(text, entities):
    sentences = text.split('.')
    entity_texts = {e['text'] for e in entities}  # Extract the entity words from entities

    relationships = []

    # Iterate over sentences to find co-occurring entities and potential relationships
    for sentence in sentences:
        sentence_entities = [entity for entity in entity_texts if entity in sentence]

        if len(sentence_entities) > 1:  # More than one entity in the sentence
            relationship_type = "related_to"  # Default relationship type
            if "owns" in sentence or "owned by" in sentence:
                relationship_type = "owned by"
            elif "CEO" in sentence or "chief executive" in sentence:
                relationship_type = "CEO of"
            elif "founded" in sentence:
                relationship_type = "founded by"
            elif "headquarters" in sentence:
                relationship_type = "has headquarters in"

            relationships.append({
                "from": sentence_entities[0],
                "relation": "related_to",  # Simplified relation, you can add actual extraction logic
                "to": sentence_entities[1]
            })

    return relationships


# Route to handle file upload and process PDF
@app.route('/upload_pdf', methods=['POST'])
@cross_origin()
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the file temporarily
        pdf_path = file.filename
        file.save(pdf_path)

        # Extract text from the PDF
        text = extract_text_from_pdf(pdf_path)

        # Extract entities using BERT
        entities = extract_entities(text)

        # Extract relationships using sentence embeddings (or a relation extraction model)
        relationships = extract_relationships(text, entities)
        print('relationship', relationships)

        return jsonify({
            "entities": entities,
            "relationships": relationships
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
