
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import docx2txt
import spacy
import re
from pdfminer.high_level import extract_text
from collections import Counter

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

# New lists for enhanced analysis
PASSION_INDICATORS = [
    "passionate about", "enthusiastic", "dedicated", "committed", "driven", 
    "motivated", "excited", "love", "enjoy", "thrive", "keen", "eager",
    "self-taught", "self-motivated", "initiative", "proactive", "volunteer",
    "personal project", "side project", "portfolio", "blog", "contribution",
    "open source", "hackathon", "competition", "award", "achievement"
]

GROWTH_INDICATORS = [
    "growth", "learn", "develop", "improve", "progress", "advance", "achieve",
    "goal", "aspire", "ambition", "further", "challenge", "opportunity", 
    "potential", "career path", "vision", "future", "certification", 
    "training", "workshop", "course", "degree", "continuing education",
    "upskill", "reskill", "mentor", "mentorship", "leadership"
]

def extract_text_from_pdf(pdf_file):
    return extract_text(pdf_file)

def extract_text_from_docx(docx_file):
    return docx2txt.process(docx_file)

def analyze_experience(text):
    # Pattern to look for years of experience
    experience_patterns = [
        r'(\d+)(?:\+)?\s+years?\s+(?:of\s+)?experience',
        r'experience\s+(?:of\s+)?(\d+)(?:\+)?\s+years?',
        r'worked\s+(?:for\s+)?(\d+)(?:\+)?\s+years?'
    ]
    
    years = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, text.lower())
        years.extend([int(y) for y in matches if y.isdigit()])
    
    if years:
        return max(years)
    return None

def analyze_education(doc):
    education = []
    edu_keywords = ["degree", "bachelor", "master", "phd", "doctorate", "bsc", "msc", "b.tech", "m.tech", "diploma"]
    
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in edu_keywords):
            education.append(sent.text.strip())
    
    return education[:3]  # Return top 3 education items

def analyze_interests(text, doc):
    interest_score = {}
    
    # Count mentions of skills to determine interest areas
    for skill in SKILLS:
        count = len(re.findall(r'\b' + re.escape(skill) + r'\b', text.lower()))
        if count > 0:
            interest_score[skill] = count
    
    # Check for passion indicators near skills
    for sentence in doc.sents:
        sentence_text = sentence.text.lower()
        for indicator in PASSION_INDICATORS:
            if indicator in sentence_text:
                for skill in SKILLS:
                    if skill in sentence_text:
                        interest_score[skill] = interest_score.get(skill, 0) + 2
    
    # Sort by score and return top interests
    sorted_interests = sorted(interest_score.items(), key=lambda x: x[1], reverse=True)
    return [{"skill": skill, "score": score} for skill, score in sorted_interests[:5]]

def analyze_growth_potential(text):
    growth_score = 0
    growth_areas = []
    
    # Check for growth indicators
    for indicator in GROWTH_INDICATORS:
        count = len(re.findall(r'\b' + re.escape(indicator) + r'\b', text.lower()))
        growth_score += count
        
        if count > 0 and indicator not in growth_areas:
            growth_areas.append(indicator)
    
    return {
        "score": min(10, growth_score),  # Cap at 10
        "indicators": growth_areas[:3]   # Top 3 growth indicators
    }

def generate_resume_suggestions(text, skills, education, experience_years):
    suggestions = []
    
    # Check length
    word_count = len(text.split())
    if word_count < 300:
        suggestions.append("Your resume appears to be quite short. Consider adding more details about your projects, responsibilities, and achievements.")
    elif word_count > 1000:
        suggestions.append("Your resume is quite lengthy. Consider condensing it to highlight your most relevant experiences.")
    
    # Check skills section
    if len(skills) < 3:
        suggestions.append("Consider adding more technical skills to your resume to showcase your expertise.")
    
    # Check action verbs
    action_verbs = ["implemented", "developed", "created", "designed", "managed", "led", "coordinated", "achieved", "improved", "reduced"]
    action_verb_count = sum(1 for verb in action_verbs if re.search(r'\b' + re.escape(verb) + r'\b', text.lower()))
    
    if action_verb_count < 3:
        suggestions.append("Use more action verbs (like 'implemented', 'developed', 'achieved') to make your accomplishments stand out.")
    
    # Check quantifiable achievements
    if not re.search(r'\d+%|\d+ percent', text.lower()):
        suggestions.append("Add quantifiable achievements (e.g., 'increased efficiency by 20%') to demonstrate your impact.")
    
    # Check education section
    if not education:
        suggestions.append("Make sure your education section is clearly formatted and includes your degree and institution.")
    
    # Provide general suggestion if none specific
    if not suggestions:
        suggestions.append("Your resume appears to be well-structured. Consider tailoring it for specific job applications.")
    
    return suggestions

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
    
    # Enhanced analysis
    experience_years = analyze_experience(text)
    education = analyze_education(doc)
    interests = analyze_interests(text, doc)
    growth = analyze_growth_potential(text)
    suggestions = generate_resume_suggestions(text, found_skills, education, experience_years)
        
    return {
        "skills": found_skills[:5],  # Limit to top 5 skills
        "role": found_role,
        "location": location,
        "experience_years": experience_years,
        "education": education,
        "interests": interests,
        "growth_potential": growth,
        "resume_suggestions": suggestions
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
