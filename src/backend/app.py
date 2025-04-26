
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import docx2txt
import spacy
import re
from pdfminer.high_level import extract_text

app = Flask(__name__)
CORS(app)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SKILLS = [
    "python", "javascript", "react", "angular", "vue", "node", "express", "django", "flask",
    "html", "css", "typescript", "java", "c++", "c#", "php", "ruby", "swift", "kotlin",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "ci/cd", "devops",
    "sql", "mongodb", "postgresql", "mysql", "oracle", "nosql", "redis", "firebase",
    "machine learning", "deep learning", "ai", "data science", "tensorflow", "pytorch",
    "nlp", "computer vision", "data analysis", "pandas", "numpy", "scipy", "matplotlib",
    "agile", "scrum", "jira", "confluence", "product management", "project management",
    "leadership", "communication", "teamwork", "problem solving", "critical thinking"
]

ROLES = [
    "software engineer", "frontend developer", "backend developer", "full stack developer",
    "mobile developer", "data scientist", "machine learning engineer", "devops engineer",
    "cloud architect", "system administrator", "database administrator", "qa engineer",
    "product manager", "project manager", "ux designer", "ui designer", "graphic designer",
    "data analyst", "business analyst", "network engineer", "security engineer", "web developer",
    "ios developer", "android developer", "game developer", "embedded systems engineer"
]

def extract_text_from_pdf(pdf_file):
    return extract_text(pdf_file)

def extract_text_from_docx(docx_file):
    return docx2txt.process(docx_file)

def extract_info(text):
    doc = nlp(text.lower())
    
    # Extract skills
    found_skills = []
    for skill in SKILLS:
        if skill in text.lower():
            found_skills.append(skill)
    
    # Extract role
    found_role = None
    for role in ROLES:
        if role in text.lower():
            found_role = role
            break
    
    if not found_role and found_skills:
        # If no specific role found but skills are present, use a generic role based on skills
        if "react" in found_skills or "javascript" in found_skills:
            found_role = "frontend developer"
        elif "python" in found_skills or "java" in found_skills:
            found_role = "backend developer"
        else:
            found_role = "software engineer"  # Default role
    
    # Try to extract location
    location_pattern = r'(?:based in|located in|from) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
    location_match = re.search(location_pattern, text)
    location = location_match.group(1) if location_match else None
    
    # If no location is found with regex, try named entity recognition
    if not location:
        for ent in doc.ents:
            if ent.label_ == "GPE":  # GPE = Geopolitical Entity (cities, countries, etc.)
                location = ent.text
                break
    
    # Default location if none found
    if not location:
        location = "Remote"
        
    return {
        "skills": found_skills[:5],  # Limit to top 5 skills
        "role": found_role,
        "location": location
    }

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        text = ""
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(filename)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(filename)
        else:
            return jsonify({"error": "Unsupported file format"}), 400
        
        info = extract_info(text)
        os.remove(filename)  # Clean up the file
        
        return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
