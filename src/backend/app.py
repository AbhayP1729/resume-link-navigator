
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import docx2txt
import spacy
import re
import json
from pdfminer.high_level import extract_text
from collections import Counter
import string

app = Flask(__name__)
CORS(app)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lists of skills, roles, and indicators for enhanced analysis
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

# Enhanced lists for personality insights
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

# Weak phrases to identify in resumes
WEAK_PHRASES = [
    "responsible for", "duties included", "worked on", "assisted with", 
    "helped with", "participated in", "involved in", "good understanding of"
]

# Strong action verbs for suggestions
STRONG_ACTION_VERBS = [
    "developed", "implemented", "designed", "created", "architected", "engineered",
    "optimized", "improved", "increased", "decreased", "reduced", "streamlined",
    "led", "managed", "directed", "coordinated", "spearheaded", "initiated",
    "analyzed", "evaluated", "researched", "identified", "solved", "delivered",
    "launched", "deployed", "maintained", "tested", "debugged", "documented"
]

# Generic terms to avoid
GENERIC_TERMS = [
    "team player", "hard worker", "detail-oriented", "self-starter",
    "go-getter", "think outside the box", "results-driven", "multitasker"
]

# Outdated technologies by field
OUTDATED_TECH = {
    "web": ["flash", "silverlight", "jquery", "xml", "soap", "ie6", "ie7", "ie8"],
    "programming": ["cobol", "fortran", "pascal", "vb6", "actionscript"],
    "mobile": ["objective-c", "cordova", "phonegap"],
    "database": ["access", "foxpro", "sybase"]
}

def extract_text_from_pdf(pdf_file):
    return extract_text(pdf_file)

def extract_text_from_docx(docx_file):
    return docx2txt.process(docx_file)

def extract_contact_info(text):
    """Extract name, email, phone, and LinkedIn profile"""
    contact_info = {
        "name": None,
        "email": None,
        "phone": None,
        "linkedin": None
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        contact_info["email"] = email_matches[0]
    
    # Extract phone number (various formats)
    phone_pattern = r'(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        contact_info["phone"] = phone_matches[0]
    
    # Extract LinkedIn URL
    linkedin_pattern = r'(linkedin\.com/in/[A-Za-z0-9_-]+)'
    linkedin_matches = re.findall(linkedin_pattern, text.lower())
    if linkedin_matches:
        contact_info["linkedin"] = linkedin_matches[0]
    
    # Attempt to extract name (more complex, using first few lines)
    lines = text.split('\n')
    for i in range(min(5, len(lines))):
        line = lines[i].strip()
        # Look for a line that's likely to be a name (short, no special chars)
        if 2 <= len(line.split()) <= 4 and all(c.isalpha() or c.isspace() for c in line):
            contact_info["name"] = line
            break
    
    return contact_info

def analyze_experience(text):
    """Extract years of experience and analyze work history"""
    experience_data = {
        "years": None,
        "positions": []
    }
    
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
        experience_data["years"] = max(years)
    
    # Try to extract job positions (this is simplified and would need refinement)
    position_patterns = [
        r'((?:Senior|Junior|Lead|Principal|Staff)?\s*(?:' + '|'.join(ROLES) + r'))',
        r'(?:at|with)\s+([A-Z][A-Za-z0-9\s&]+)(?:,|\.|from|\(|\s+\d)'
    ]
    
    for pattern in position_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Filter out very short matches and duplicates
            positions = [m for m in matches if len(m) > 3]
            experience_data["positions"].extend(positions[:3])
    
    return experience_data

def analyze_education(text, doc):
    """Extract and analyze education information"""
    education = []
    edu_keywords = ["degree", "bachelor", "master", "phd", "doctorate", "bsc", "msc", "b.tech", "m.tech", "diploma", "university", "college"]
    institutions = ["university", "college", "institute", "school"]
    degrees = ["bachelor", "master", "phd", "doctorate", "b.tech", "m.tech", "bsc", "msc"]
    
    # Try to identify education sections
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if any(keyword in sent_text for keyword in edu_keywords):
            # Check if sentence contains both institution and degree info
            has_institution = any(inst in sent_text for inst in institutions)
            has_degree = any(deg in sent_text for deg in degrees)
            
            if has_institution or has_degree:
                # Clean and format
                clean_text = sent.text.strip().replace('\n', ' ')
                if clean_text not in [e.get("text") for e in education]:
                    education_item = {
                        "text": clean_text,
                        "quality_score": calculate_education_quality(clean_text)
                    }
                    education.append(education_item)
    
    return education

def calculate_education_quality(edu_text):
    """Calculate a simple quality score for education"""
    quality_score = 5  # Base score
    
    # Prestigious keywords
    prestigious = ["ivy", "league", "top", "prestigious", "renowned", "leading"]
    tech_focus = ["technical", "technology", "engineering", "computer science", "data science"]
    advanced = ["phd", "doctorate", "research", "thesis", "dissertation", "master"]
    
    # Adjust score based on keywords
    if any(word in edu_text.lower() for word in prestigious):
        quality_score += 2
    if any(word in edu_text.lower() for word in tech_focus):
        quality_score += 1
    if any(word in edu_text.lower() for word in advanced):
        quality_score += 2
        
    # Cap at 10
    return min(10, quality_score)

def extract_projects(text):
    """Extract project information from resume"""
    projects = []
    
    # Look for project sections or markers
    project_markers = ["project", "projects:", "key projects", "academic projects"]
    
    # Find potential project sections
    lines = text.split('\n')
    in_project_section = False
    current_project = {"title": None, "description": ""}
    
    for i, line in enumerate(lines):
        lower_line = line.lower().strip()
        
        # Check if line indicates the start of projects section
        if any(marker in lower_line for marker in project_markers) and len(lower_line) < 30:
            in_project_section = True
            continue
            
        # If we're in a projects section
        if in_project_section:
            # Check for potential project title (short line, often with technologies in parentheses)
            if 3 <= len(lower_line) <= 100 and not lower_line.startswith(('•', '-', '●')) and current_project["title"] is None:
                current_project["title"] = line.strip()
            
            # Check for description bullet points
            elif lower_line.startswith(('•', '-', '●')) or (i > 0 and lines[i-1].endswith(':')):
                if current_project["title"]:
                    current_project["description"] += line.strip() + " "
            
            # If blank line and we have title/description, save project and reset
            elif not lower_line and current_project["title"]:
                if len(current_project["description"]) > 10:  # Only save if has meaningful description
                    complexity_score = calculate_project_complexity(current_project)
                    current_project["complexity_score"] = complexity_score
                    projects.append(current_project)
                current_project = {"title": None, "description": ""}
            
            # Section break detection
            elif lower_line and len(lower_line) < 30 and lower_line.endswith(':') and not any(marker in lower_line for marker in project_markers):
                in_project_section = False
    
    # Don't forget the last project if pending
    if current_project["title"] and len(current_project["description"]) > 10:
        complexity_score = calculate_project_complexity(current_project)
        current_project["complexity_score"] = complexity_score
        projects.append(current_project)
    
    return projects[:3]  # Limit to top 3 projects

def calculate_project_complexity(project):
    """Calculate complexity score for a project"""
    complexity_score = 5  # Base score
    
    # Technical keywords that indicate complexity
    complexity_indicators = [
        "architecture", "scalable", "optimized", "algorithm", "database", "cloud",
        "distributed", "microservices", "api", "security", "authentication",
        "machine learning", "ai", "data", "analytics", "visualization"
    ]
    
    # Tech stack breadth
    tech_stack_size = sum(1 for skill in SKILLS if skill in project["description"].lower())
    
    # Adjust score based on indicators and tech stack
    full_text = (project["title"] + " " + project["description"]).lower()
    for indicator in complexity_indicators:
        if indicator in full_text:
            complexity_score += 0.5
    
    complexity_score += min(3, tech_stack_size * 0.5)  # Add up to 3 points for tech stack
    
    # Cap at 10
    return min(10, complexity_score)

def analyze_skills(text):
    """Extract and analyze skills from resume"""
    skill_data = {
        "technical": [],
        "soft": [],
        "outdated": []
    }
    
    technical_skills = []
    
    # Technical skills extraction
    for skill in SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
            technical_skills.append(skill)
    
    # Check for outdated technologies
    outdated = []
    for category, techs in OUTDATED_TECH.items():
        for tech in techs:
            if re.search(r'\b' + re.escape(tech) + r'\b', text.lower()):
                outdated.append(tech)
    
    # Soft skills extraction (simplified)
    soft_skills = ["communication", "leadership", "teamwork", "problem solving", 
                  "critical thinking", "time management", "adaptability"]
    found_soft_skills = []
    
    for skill in soft_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
            found_soft_skills.append(skill)
    
    # Calculate technical/soft skill balance
    skill_data["technical"] = technical_skills[:10]  # Top 10 technical skills
    skill_data["soft"] = found_soft_skills
    skill_data["outdated"] = outdated
    skill_data["balance_score"] = min(10, len(technical_skills) + len(found_soft_skills) - len(outdated))
    
    return skill_data

def analyze_interests(text, doc):
    """Analyze interests and passion areas based on resume content"""
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
    return [{"skill": skill, "score": min(10, score)} for skill, score in sorted_interests[:5]]

def analyze_growth_potential(text):
    """Analyze growth potential based on language used in resume"""
    growth_score = 0
    growth_areas = []
    
    # Check for growth indicators
    for indicator in GROWTH_INDICATORS:
        count = len(re.findall(r'\b' + re.escape(indicator) + r'\b', text.lower()))
        growth_score += count
        
        if count > 0 and indicator not in growth_areas:
            growth_areas.append(indicator)
    
    # Check for learning patterns
    learning_patterns = [
        r'(?:completed|pursuing|earned|achieved)\s+(?:a|an)\s+(?:course|certification|degree)',
        r'(?:self|auto)-taught',
        r'(?:continuously|actively)\s+(?:learning|developing|improving)'
    ]
    
    for pattern in learning_patterns:
        if re.search(pattern, text.lower()):
            growth_score += 2
    
    return {
        "score": min(10, growth_score),  # Cap at 10
        "indicators": growth_areas[:3]   # Top 3 growth indicators
    }

def analyze_writing_quality(text):
    """Analyze the writing quality of the resume"""
    quality_score = 7  # Start with a baseline score
    
    # Check for weak phrases
    weak_phrase_count = sum(1 for phrase in WEAK_PHRASES if phrase in text.lower())
    
    # Check for strong action verbs
    action_verb_count = sum(1 for verb in STRONG_ACTION_VERBS if re.search(r'\b' + re.escape(verb) + r'\b', text.lower()))
    
    # Check for quantifiable achievements
    quantifiable_patterns = [
        r'\d+%',
        r'increased .* by',
        r'decreased .* by',
        r'reduced .* by',
        r'improved .* by',
        r'generated .*\$[\d,]+'
    ]
    quantifiable_count = sum(1 for pattern in quantifiable_patterns if re.search(pattern, text.lower()))
    
    # Check for generic terms
    generic_count = sum(1 for term in GENERIC_TERMS if term in text.lower())
    
    # Calculate final score
    quality_score -= (weak_phrase_count * 0.5)  # Penalize weak phrases
    quality_score += min(3, action_verb_count * 0.3)  # Reward action verbs (max +3)
    quality_score += min(2, quantifiable_count * 0.5)  # Reward quantifiable achievements (max +2)
    quality_score -= (generic_count * 0.5)  # Penalize generic terms
    
    # Cap score between 1-10
    return {
        "score": max(1, min(10, quality_score)),
        "weak_phrases_found": weak_phrase_count,
        "action_verbs_found": action_verb_count,
        "quantifiable_achievements": quantifiable_count,
        "generic_terms_found": generic_count
    }

def generate_resume_suggestions(parsed_data):
    """Generate actionable suggestions for resume improvement"""
    suggestions = []
    
    # Check writing quality
    writing_quality = parsed_data.get("writing_quality", {})
    if writing_quality.get("weak_phrases_found", 0) > 0:
        suggestions.append({
            "type": "writing",
            "severity": "high" if writing_quality.get("weak_phrases_found", 0) > 3 else "medium",
            "text": f"Replace passive phrases like '{WEAK_PHRASES[0]}' with strong action verbs such as '{STRONG_ACTION_VERBS[0]}', '{STRONG_ACTION_VERBS[1]}', or '{STRONG_ACTION_VERBS[2]}'."
        })
    
    # Check quantifiable achievements
    if writing_quality.get("quantifiable_achievements", 0) < 2:
        suggestions.append({
            "type": "achievement",
            "severity": "high",
            "text": "Add measurable achievements with metrics (e.g., 'Reduced processing time by 40%' instead of 'Improved processing time')."
        })
    
    # Check for generic terms
    if writing_quality.get("generic_terms_found", 0) > 0:
        suggestions.append({
            "type": "specificity",
            "severity": "medium",
            "text": f"Replace generic phrases like '{GENERIC_TERMS[0]}' with specific examples that demonstrate these qualities."
        })
    
    # Check skills balance
    skills = parsed_data.get("skills", {})
    if len(skills.get("technical", [])) < 5:
        suggestions.append({
            "type": "skills",
            "severity": "high",
            "text": "Add more specific technical skills relevant to your target role."
        })
    
    if len(skills.get("soft", [])) < 2:
        suggestions.append({
            "type": "skills",
            "severity": "medium",
            "text": "Include soft skills such as communication, teamwork, or leadership with concrete examples."
        })
    
    # Check for outdated technologies
    if skills.get("outdated", []):
        outdated_list = ", ".join(skills.get("outdated", [])[:3])
        suggestions.append({
            "type": "tech",
            "severity": "high",
            "text": f"Consider removing or downplaying outdated technologies like {outdated_list} unless specifically required for the role."
        })
    
    # Project suggestion
    projects = parsed_data.get("projects", [])
    if not projects:
        suggestions.append({
            "type": "projects",
            "severity": "high",
            "text": "Add detailed projects with technologies used and your specific contributions."
        })
    elif any(p.get("complexity_score", 0) < 6 for p in projects):
        suggestions.append({
            "type": "projects",
            "severity": "medium",
            "text": "Enhance project descriptions with technical details and highlight the complexity of problems solved."
        })
    
    # Education suggestion
    education = parsed_data.get("education", [])
    if not education:
        suggestions.append({
            "type": "education",
            "severity": "medium",
            "text": "Add your educational background, including degrees, institutions, and relevant coursework."
        })
    
    # Ensure we return at least 3 suggestions
    if len(suggestions) < 3:
        general_suggestions = [
            {
                "type": "format",
                "severity": "medium",
                "text": "Ensure your resume is well-formatted with consistent spacing, bullet points, and fonts."
            },
            {
                "type": "length",
                "severity": "medium",
                "text": "Keep your resume concise - aim for one page for early-career professionals."
            },
            {
                "type": "keywords",
                "severity": "high",
                "text": "Tailor your resume with keywords from the job descriptions you're applying to."
            }
        ]
        
        suggestions.extend(general_suggestions[:3 - len(suggestions)])
    
    return suggestions[:5]  # Return top 5 suggestions

def calculate_ats_score(parsed_data):
    """Calculate overall ATS score based on all components"""
    scoring = {
        "overall": 0,
        "components": {
            "contact_info": 0,
            "skills_match": 0,
            "experience": 0,
            "education": 0,
            "projects": 0,
            "writing_quality": 0
        }
    }
    
    # Contact info score
    contact_info = parsed_data.get("contact_info", {})
    contact_score = sum(2 for item in contact_info.values() if item) / 8 * 10  # Each item worth 2.5 points
    scoring["components"]["contact_info"] = round(contact_score)
    
    # Skills match score
    skills = parsed_data.get("skills", {})
    skills_score = min(10, len(skills.get("technical", [])) + len(skills.get("soft", [])) - len(skills.get("outdated", [])))
    scoring["components"]["skills_match"] = max(1, skills_score)
    
    # Experience score
    experience_years = parsed_data.get("experience", {}).get("years", 0) or 0
    exp_positions = parsed_data.get("experience", {}).get("positions", [])
    experience_score = min(10, (experience_years * 2) + len(exp_positions))
    scoring["components"]["experience"] = max(1, experience_score)
    
    # Education score
    education = parsed_data.get("education", [])
    avg_edu_score = sum(edu.get("quality_score", 5) for edu in education) / max(1, len(education))
    scoring["components"]["education"] = round(avg_edu_score)
    
    # Projects score
    projects = parsed_data.get("projects", [])
    avg_proj_score = sum(proj.get("complexity_score", 5) for proj in projects) / max(1, len(projects))
    scoring["components"]["projects"] = round(avg_proj_score)
    
    # Writing quality score
    writing_score = parsed_data.get("writing_quality", {}).get("score", 5)
    scoring["components"]["writing_quality"] = writing_score
    
    # Calculate weighted average for overall score
    weights = {
        "contact_info": 0.1,
        "skills_match": 0.25,
        "experience": 0.2,
        "education": 0.15,
        "projects": 0.2,
        "writing_quality": 0.1
    }
    
    overall_score = sum(score * weights[component] for component, score in scoring["components"].items())
    scoring["overall"] = round(overall_score)
    
    return scoring

def extract_info(text):
    """Main function to extract and analyze resume data"""
    doc = nlp(text.lower())
    
    # Contact information
    contact_info = extract_contact_info(text)
    
    # Experience analysis
    experience = analyze_experience(text)
    
    # Education analysis
    education = analyze_education(text, doc)
    
    # Project analysis
    projects = extract_projects(text)
    
    # Skills analysis
    skills = analyze_skills(text)
    
    # Interests analysis
    interests = analyze_interests(text, doc)
    
    # Growth potential analysis
    growth = analyze_growth_potential(text)
    
    # Writing quality analysis
    writing_quality = analyze_writing_quality(text)
    
    # Default location and role extraction (from existing code)
    # Extract role
    found_role = None
    for role in ROLES:
        if role in text.lower():
            found_role = role
            break
    
    if not found_role and skills.get("technical", []):
        # If no specific role found but skills are present, use a generic role based on skills
        if "react" in skills.get("technical", []) or "javascript" in skills.get("technical", []):
            found_role = "frontend developer"
        elif "python" in skills.get("technical", []) or "java" in skills.get("technical", []):
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
    
    # Combine all data
    parsed_data = {
        "contact_info": contact_info,
        "skills": skills,
        "role": found_role,
        "location": location,
        "experience": experience,
        "education": education,
        "projects": projects,
        "interests": interests,
        "growth_potential": growth,
        "writing_quality": writing_quality
    }
    
    # Generate suggestions
    suggestions = generate_resume_suggestions(parsed_data)
    parsed_data["resume_suggestions"] = suggestions
    
    # Calculate ATS score
    ats_score = calculate_ats_score(parsed_data)
    parsed_data["ats_score"] = ats_score
    
    # For compatibility with existing frontend
    # Include the expected fields from the original implementation
    parsed_data["skills"] = skills.get("technical", [])[:5]
    parsed_data["experience_years"] = experience.get("years")
    
    return parsed_data

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

@app.route('/api/analyze-job-match', methods=['POST'])
def analyze_job_match():
    """Analyze match between resume and job description"""
    data = request.json
    if not data or "resume_text" not in data or "job_description" not in data:
        return jsonify({"error": "Missing resume text or job description"}), 400
    
    resume_text = data["resume_text"]
    job_description = data["job_description"]
    
    # Extract skills from job description
    job_skills = []
    for skill in SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', job_description.lower()):
            job_skills.append(skill)
    
    # Extract skills from resume
    resume_skills = []
    for skill in SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', resume_text.lower()):
            resume_skills.append(skill)
    
    # Find matching and missing skills
    matching_skills = [skill for skill in job_skills if skill in resume_skills]
    missing_skills = [skill for skill in job_skills if skill not in resume_skills]
    
    # Calculate match percentage
    match_percentage = len(matching_skills) / max(1, len(job_skills)) * 100
    
    return jsonify({
        "match_percentage": round(match_percentage),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "job_skills": job_skills
    })

if __name__ == '__main__':
    app.run(debug=True)
