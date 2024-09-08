import fitz  # PyMuPDF to read PDF files
from flask import Flask, jsonify, request
import spacy
import string
import os
from flask_cors import CORS, cross_origin
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")
stop_words = spacy.lang.en.stop_words.STOP_WORDS
parser = English()
punctuations = string.punctuation


# Helper function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    text = ""
    for page in doc:
        text += page.get_text()
    return text


# Helper function to extract entities and relationships
def extract_entities_and_relationships(text):
    doc = nlp(text)

    # Use sets to store unique entities and relationships
    entities = set()
    relationships = set()

    # Extract entities
    for ent in doc.ents:
        # Add unique entity as a tuple (text, label)
        entities.add((ent.text, ent.label_))

    # Extract relationships - refined logic
    for sent in doc.sents:
        root = None
        subject = None
        obj = None

        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                root = token
            if token.dep_ == "nsubj":  # Subject
                subject = token
            if token.dep_ == "dobj":  # Object
                obj = token

        # If a valid subject-verb-object structure is found
        if root and subject and obj:
            relationships.add((subject.text, root.text, obj.text))

        # Debugging print to understand sentence structure
        print(f"Sentence: {sent.text}")
        print(f"Subject: {subject}, Root: {root}, Object: {obj}")

    # Filter entities based on relationships
    related_entities = set()
    for rel in relationships:
        related_entities.add(rel[0])  # From (subject)
        related_entities.add(rel[2])  # To (object)

    # Keep only entities that have relationships
    filtered_entities = [{"text": ent[0], "label": ent[1]} for ent in entities if ent[0] in related_entities]

    # Convert relationships to a list of dictionaries
    relationships_list = [{"from": rel[0], "relation": rel[1], "to": rel[2]} for rel in relationships]

    # Debugging print for entities and relationships
    print(f"Entities: {filtered_entities}")
    print(f"Relationships: {relationships_list}")

    return filtered_entities, relationships_list


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
        print(text)

        # Extract entities and relationships from the text
        entities, relationships = extract_entities_and_relationships(text)
        print('Entities:', entities)
        print('Relationships:', relationships)

        return jsonify({
            "entities": entities,
            "relationships": relationships
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

