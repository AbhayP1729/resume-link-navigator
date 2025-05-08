
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
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)

# Load more advanced spaCy model for better accuracy
try:
    nlp = spacy.load("en_core_web_lg")  # Larger model with word vectors
except:
    # Fallback to smaller model if large one not available
    nlp = spacy.load("en_core_web_sm")
    print("Warning: Using smaller spaCy model. For better results, install en_core_web_lg")

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Comprehensive lists for enhanced analysis
SKILLS = [
    # Technical skills
    "python", "javascript", "typescript", "react", "angular", "vue", "node", "express", "django", "flask",
    "html", "css", "sass", "less", "bootstrap", "tailwind", "material-ui", "styled-components",
    "java", "c++", "c#", "php", "ruby", "swift", "kotlin", "go", "rust", "scala", "perl",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "circleci", "gitlab-ci", "github-actions",
    "terraform", "ansible", "chef", "puppet", "prometheus", "grafana", "elk", "splunk",
    "sql", "mysql", "postgresql", "mongodb", "dynamodb", "redis", "elasticsearch", "cassandra", "oracle",
    "machine learning", "deep learning", "artificial intelligence", "data science", "tensorflow", "pytorch",
    "keras", "scikit-learn", "pandas", "numpy", "jupyter", "tableau", "power bi", "matplotlib", "opencv",
    "nlp", "computer vision", "reinforcement learning", "generative ai", "llm", "transformers", "bert", "gpt",
    "rest", "graphql", "grpc", "websockets", "oauth", "jwt", "microservices", "serverless", "soa",
    "git", "svn", "agile", "scrum", "kanban", "jira", "confluence", "tdd", "bdd", "ci/cd",
    
    # Data engineering
    "etl", "data warehouse", "data lake", "hadoop", "spark", "kafka", "airflow", "databricks", "snowflake",
    
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin", "ionic", "cordova", "swift", "kotlin",
    
    # DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "github actions", "circleci",
    "prometheus", "grafana", "ansible", "chef", "puppet", "vagrant", "packer",
    
    # Cybersecurity
    "penetration testing", "ethical hacking", "security auditing", "vulnerability assessment",
    "cryptography", "network security", "application security", "security compliance",
    
    # Soft skills
    "leadership", "communication", "teamwork", "problem solving", "critical thinking", "time management",
    "project management", "analytical skills", "creativity", "adaptability", "conflict resolution",
    "emotional intelligence", "presentation skills", "negotiation", "decision making"
]

ROLES = [
    # Engineering roles
    "software engineer", "frontend developer", "backend developer", "full stack developer",
    "mobile developer", "ios developer", "android developer", "devops engineer", "site reliability engineer",
    "qa engineer", "test automation engineer", "security engineer", "machine learning engineer",
    "data engineer", "database administrator", "cloud architect", "systems architect",
    "embedded systems engineer", "game developer",
    
    # Data roles
    "data scientist", "data analyst", "business intelligence analyst", "data architect",
    "big data engineer", "research scientist", "computational linguist", "ai researcher",
    
    # Design roles
    "ux designer", "ui designer", "product designer", "graphic designer", "web designer",
    "interaction designer", "visual designer",
    
    # Management roles
    "product manager", "project manager", "program manager", "engineering manager",
    "technical lead", "tech lead", "team lead", "cto", "vp of engineering", "director of engineering",
    
    # Other tech roles
    "technical writer", "solutions architect", "sales engineer", "customer success manager",
    "technical support engineer", "network engineer", "system administrator"
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
    "helped with", "participated in", "involved in", "good understanding of",
    "familiar with", "knowledge of", "exposure to"
]

# Strong action verbs for suggestions
STRONG_ACTION_VERBS = [
    "developed", "implemented", "designed", "created", "architected", "engineered",
    "optimized", "improved", "increased", "decreased", "reduced", "streamlined",
    "led", "managed", "directed", "coordinated", "spearheaded", "initiated",
    "analyzed", "evaluated", "researched", "identified", "solved", "delivered",
    "launched", "deployed", "maintained", "tested", "debugged", "documented",
    "refactored", "automated", "configured", "transformed", "scaled", "accelerated",
    "pioneered", "cultivated", "mentored", "guided", "orchestrated", "modernized"
]

# Generic terms to avoid
GENERIC_TERMS = [
    "team player", "hard worker", "detail-oriented", "self-starter",
    "go-getter", "think outside the box", "results-driven", "multitasker",
    "go-to person", "proven track record", "hit the ground running", "dynamic",
    "synergy", "best of breed", "value add", "proactive", "game-changer"
]

# Outdated technologies by field
OUTDATED_TECH = {
    "web": ["flash", "silverlight", "jquery", "xml", "soap", "ie6", "ie7", "ie8", "vbscript"],
    "programming": ["cobol", "fortran", "pascal", "vb6", "actionscript", "perl", "delphi"],
    "mobile": ["objective-c", "cordova", "phonegap", "titanium", "sencha", "blackberry"],
    "database": ["access", "foxpro", "sybase", "db2", "paradox", "informix"],
    "os": ["windows xp", "windows vista", "windows 7", "windows server 2003"]
}

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF with improved handling of formatting"""
    try:
        text = extract_text(pdf_file)
        # Clean up text - remove excessive whitespace while preserving paragraph breaks
        text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(docx_file):
    """Extract text from DOCX with improved handling of formatting"""
    try:
        text = docx2txt.process(docx_file)
        # Clean up text while preserving structure
        text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_contact_info(text, doc):
    """Extract name, email, phone, and LinkedIn profile with improved accuracy"""
    contact_info = {
        "name": None,
        "email": None,
        "phone": None,
        "linkedin": None
    }
    
    # Extract email with validation
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        # Use the first match that's likely to be a real email (has proper domain)
        for email in email_matches:
            if re.search(r'@(gmail|yahoo|outlook|hotmail|protonmail|icloud|\w+\.(com|org|net|edu|io))', email):
                contact_info["email"] = email
                break
        if not contact_info["email"] and email_matches:
            contact_info["email"] = email_matches[0]  # Fallback to first match
    
    # Extract phone number with improved pattern matching
    phone_patterns = [
        r'(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # Standard formats
        r'(\d{3}[\s.-]?\d{3}[\s.-]?\d{4})',  # US without country code
        r'(\(\d{3}\)[\s.-]?\d{3}[\s.-]?\d{4})'  # Parentheses format
    ]
    
    for pattern in phone_patterns:
        phone_matches = re.findall(pattern, text)
        if phone_matches:
            # Clean up the phone number
            phone = re.sub(r'[^0-9+]', '', phone_matches[0])
            if len(phone) >= 10:  # Must be at least 10 digits to be valid
                contact_info["phone"] = phone
                break
    
    # Extract LinkedIn URL with improved pattern matching
    linkedin_patterns = [
        r'(linkedin\.com/in/[A-Za-z0-9_-]+)',
        r'(linkedin\.com/profile/[A-Za-z0-9_-]+)'
    ]
    
    for pattern in linkedin_patterns:
        linkedin_matches = re.findall(pattern, text.lower())
        if linkedin_matches:
            contact_info["linkedin"] = linkedin_matches[0]
            break
    
    # Improved name extraction using NER and heuristics
    # First try named entity recognition
    person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
    # Filter by likely names (2-3 words, proper capitalization)
    likely_names = [name for name in person_entities if 
                   1 <= len(name.split()) <= 3 and 
                   all(word[0].isupper() for word in name.split())]
    
    if likely_names:
        contact_info["name"] = likely_names[0]  # Use the first likely name
    else:
        # Fallback: look at the beginning of the document for possible name
        lines = text.split('\n')
        for i in range(min(5, len(lines))):
            line = lines[i].strip()
            # Look for a line that's likely to be a name (short, properly capitalized)
            words = line.split()
            if 1 <= len(words) <= 3 and all(word[0].isupper() if word else False for word in words):
                if not any(term.lower() in line.lower() for term in ["resume", "cv", "curriculum", "vitae"]):
                    contact_info["name"] = line
                    break
    
    return contact_info

def analyze_experience(text, doc):
    """Extract years of experience and analyze work history with improved accuracy"""
    experience_data = {
        "years": None,
        "positions": []
    }
    
    # Enhanced pattern recognition for years of experience
    experience_patterns = [
        r'(\d+)(?:\+)?\s+years?\s+(?:of\s+)?experience',
        r'experience\s+(?:of\s+)?(\d+)(?:\+)?\s+years?',
        r'worked\s+(?:for\s+)?(\d+)(?:\+)?\s+years?',
        r'(\d+)(?:\+)?\s+years?\s+(?:in|at|with)',
        r'career\s+(?:of|spanning)\s+(\d+)(?:\+)?\s+years?'
    ]
    
    years = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, text.lower())
        years.extend([int(y) for y in matches if y.isdigit()])
    
    # Calculate experience based on work history if explicit years not found
    if not years:
        # Look for date ranges
        date_ranges = re.findall(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\s*(?:-|–|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|present|current|now)', text, re.IGNORECASE)
        
        total_months = 0
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        for start, end in date_ranges:
            try:
                start_date = datetime.strptime(start, "%b %Y")
            except ValueError:
                try:
                    start_date = datetime.strptime(start, "%B %Y")
                except ValueError:
                    continue
                    
            if re.search(r'present|current|now', end, re.IGNORECASE):
                end_date = datetime(current_year, current_month, 1)
            else:
                try:
                    end_date = datetime.strptime(end, "%b %Y")
                except ValueError:
                    try:
                        end_date = datetime.strptime(end, "%B %Y")
                    except ValueError:
                        continue
            
            # Calculate months between dates
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months
        
        # Convert months to years
        if total_months > 0:
            years = [total_months // 12]
    
    if years:
        experience_data["years"] = max(years)
    
    # Improved job title extraction using NER and pattern matching
    # Look for job titles based on known roles
    positions = []
    
    # Method 1: NER for JOB_TITLE if available
    org_entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG"]]
    
    # Method 2: Pattern-based matching for job titles
    job_patterns = [
        r'(?:^|\n)((?:Senior|Junior|Lead|Principal|Staff|Chief|Head of|Director of|VP of)?\s*[A-Z][A-Za-z\s]+(?:Developer|Engineer|Designer|Architect|Manager|Analyst|Scientist|Specialist|Consultant))',
        r'(?:as|at|with)\s+(?:a|an)\s+((?:Senior|Junior|Lead|Principal)?\s*[A-Z][A-Za-z\s]+(?:Developer|Engineer|Designer|Architect|Manager))'
    ]
    
    for pattern in job_patterns:
        matches = re.findall(pattern, text)
        positions.extend([m.strip() for m in matches if 3 < len(m) < 50])
    
    # Method 3: Look for position titles at the beginning of bullet points
    bullet_points = re.findall(r'(?:^|\n)(?:•|-|\*|\d+\.)\s*([A-Z][A-Za-z\s]+(?:Developer|Engineer|Designer|Manager|Analyst|Specialist))(?:at|,|\s+\(|\s+with)', text)
    positions.extend([bp.strip() for bp in bullet_points if 3 < len(bp) < 50])
    
    # Method 4: Look for known roles from our list
    for role in ROLES:
        if re.search(r'\b' + re.escape(role) + r'\b', text.lower()):
            capitalized_role = ' '.join(word.capitalize() for word in role.split())
            positions.append(capitalized_role)
    
    # Filter and deduplicate positions
    positions = list(set(positions))
    positions = [p for p in positions if not any(term.lower() in p.lower() for term in ["resume", "cv", "curriculum", "vitae", "references"])]
    
    # Sort positions by likely seniority (containing keywords like Senior, Lead, etc.)
    positions.sort(key=lambda x: 1 if any(level in x.lower() for level in ["senior", "lead", "principal", "head", "chief", "director"]) else 2)
    
    experience_data["positions"] = positions[:3]  # Top 3 most relevant positions
    
    return experience_data

def analyze_education(text, doc):
    """Extract and analyze education information with improved accuracy"""
    education = []
    
    # Enhanced keyword lists
    edu_keywords = [
        "degree", "bachelor", "master", "phd", "doctorate", "mba", "ms", "ma", "bsc", "msc", 
        "b.tech", "m.tech", "b.e.", "m.e.", "b.s.", "m.s.", "b.a.", "m.a.", "diploma", 
        "certificate", "certification", "university", "college", "institute", "school", 
        "graduated", "graduation"
    ]
    
    institutions = [
        "university", "college", "institute", "school", "academy", "polytechnic"
    ]
    
    degrees = [
        "bachelor", "master", "phd", "doctorate", "mba", "ms", "ma", "bsc", "msc",
        "b.tech", "m.tech", "b.e.", "m.e.", "b.s.", "m.s.", "b.a.", "m.a."
    ]
    
    # Improved education section detection
    edu_section = None
    
    # Try to find education section
    section_headers = re.findall(r'(?:^|\n)(education|academic background|academic qualifications|educational qualifications?)(?::|\n)', text, re.IGNORECASE)
    
    if section_headers:
        # Find the start and end of education section
        start_match = re.search(r'(?:^|\n)(education|academic background|academic qualifications|educational qualifications?)(?::|\n)', text, re.IGNORECASE)
        if start_match:
            start_idx = start_match.start()
            
            # Look for the next section header
            next_section = re.search(r'(?:^|\n)(experience|work experience|employment|skills|projects|certifications|activities|interests|languages|references)(?::|\n)', text[start_idx:], re.IGNORECASE)
            
            if next_section:
                end_idx = start_idx + next_section.start()
                edu_section = text[start_idx:end_idx]
            else:
                edu_section = text[start_idx:]
    
    # If education section found, analyze it first
    if edu_section:
        paragraphs = edu_section.split('\n\n')
        
        for para in paragraphs:
            if any(keyword in para.lower() for keyword in edu_keywords):
                # Clean and format
                clean_text = para.strip().replace('\n', ' ')
                
                # Skip if too short or probably not education
                if len(clean_text) < 10:
                    continue
                
                # Calculate quality score and add to list
                if clean_text not in [e.get("text") for e in education]:
                    education_item = {
                        "text": clean_text,
                        "quality_score": calculate_education_quality(clean_text, doc)
                    }
                    education.append(education_item)
    else:
        # Fallback: look for education info throughout the document
        sentences = [sent.text for sent in doc.sents]
        
        for sent in sentences:
            sent_text = sent.lower()
            if any(keyword in sent_text for keyword in edu_keywords):
                # Check if sentence contains both institution and degree info
                has_institution = any(inst in sent_text for inst in institutions)
                has_degree = any(deg in sent_text for deg in degrees)
                
                if has_institution or has_degree:
                    # Clean and format
                    clean_text = sent.strip().replace('\n', ' ')
                    if len(clean_text) >= 10 and clean_text not in [e.get("text") for e in education]:
                        education_item = {
                            "text": clean_text,
                            "quality_score": calculate_education_quality(clean_text, doc)
                        }
                        education.append(education_item)
    
    return education

def calculate_education_quality(edu_text, doc):
    """Calculate a more accurate quality score for education"""
    quality_score = 5  # Base score
    
    # Enhanced quality factors
    prestigious = ["ivy", "league", "top", "prestigious", "renowned", "leading", "ranked", "tier", "accredited"]
    tech_focus = ["technical", "technology", "engineering", "computer science", "data science", "artificial intelligence", "machine learning", "cyber", "information technology", "software", "computational"]
    advanced = ["phd", "doctorate", "research", "thesis", "dissertation", "master", "msc", "ms", "ma", "mba", "postgraduate", "post-graduate", "advanced"]
    gpa_pattern = r'(?:gpa|grade point average)[:\s]+([0-9.]+/[0-9.]+|[0-9]\.[0-9])'
    
    # Check for honors or distinctions
    honors = ["summa cum laude", "magna cum laude", "cum laude", "honors", "distinction", "dean's list", "scholarship", "award", "fellowship"]
    
    # Check for prestigious schools
    prestigious_schools = ["harvard", "stanford", "mit", "yale", "princeton", "berkeley", "oxford", "cambridge", "caltech", "chicago", "imperial", "eth zurich", "mcgill"]
    
    # Adjust score based on keywords
    if any(word in edu_text.lower() for word in prestigious):
        quality_score += 1
    
    if any(school in edu_text.lower() for school in prestigious_schools):
        quality_score += 2
    
    if any(word in edu_text.lower() for word in tech_focus):
        quality_score += 1
    
    if any(word in edu_text.lower() for word in advanced):
        quality_score += 1.5
        
    if any(word in edu_text.lower() for word in honors):
        quality_score += 1
    
    # Check for GPA (if high)
    gpa_match = re.search(gpa_pattern, edu_text.lower())
    if gpa_match:
        gpa_str = gpa_match.group(1)
        try:
            # Handle different GPA formats
            if '/' in gpa_str:
                num, denom = gpa_str.split('/')
                gpa = float(num) / float(denom) * 4.0  # Normalize to 4.0 scale
            else:
                gpa = float(gpa_str)
                
            # Adjust score based on GPA (assuming 4.0 scale)
            if gpa >= 3.7:
                quality_score += 1.5
            elif gpa >= 3.5:
                quality_score += 1
            elif gpa >= 3.0:
                quality_score += 0.5
        except:
            pass  # If GPA conversion fails, ignore
    
    # Analyze relevance to technical fields
    if any(skill.lower() in edu_text.lower() for skill in SKILLS):
        quality_score += 1
        
    # Cap at 10
    return min(10, quality_score)

def extract_projects(text, doc):
    """Extract project information with improved accuracy"""
    projects = []
    
    # Improved markers for project sections
    project_markers = [
        "project", "projects:", "key projects", "selected projects", "personal projects",
        "academic projects", "professional projects", "side projects", "portfolio"
    ]
    
    # Identify project section
    project_section = None
    
    # Try to find project section
    section_match = re.search(r'(?:^|\n)(projects|selected projects|personal projects|academic projects|professional projects|side projects|portfolio)(?::|\n)', text, re.IGNORECASE)
    
    if section_match:
        start_idx = section_match.start()
        
        # Look for the next section header
        next_section = re.search(r'(?:^|\n)(experience|education|skills|certifications|activities|interests|languages|references)(?::|\n)', text[start_idx:], re.IGNORECASE)
        
        if next_section:
            end_idx = start_idx + next_section.start()
            project_section = text[start_idx:end_idx]
        else:
            project_section = text[start_idx:]
    
    # If project section found
    if project_section:
        lines = project_section.split('\n')
        in_project = False
        current_project = {"title": None, "description": ""}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                # End of project
                if in_project and current_project["title"] and current_project["description"]:
                    complexity_score = calculate_project_complexity(current_project)
                    current_project["complexity_score"] = complexity_score
                    projects.append(current_project)
                    current_project = {"title": None, "description": ""}
                    in_project = False
                continue
                
            # Skip section headers
            if any(marker.lower() == line.lower() for marker in project_markers):
                continue
                
            # Check if this is a new project title (first line after section header or blank line)
            if not in_project and not line.startswith(('•', '-', '*', '→')):
                current_project["title"] = line
                in_project = True
            elif in_project:
                # Add to description
                current_project["description"] += line + " "
        
        # Don't forget the last project
        if in_project and current_project["title"] and current_project["description"]:
            complexity_score = calculate_project_complexity(current_project)
            current_project["complexity_score"] = complexity_score
            projects.append(current_project)
    else:
        # Fallback: try to find projects throughout the document
        # Look for paragraphs that might be projects
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            lines = para.split('\n')
            if 2 <= len(lines) <= 10:  # Projects typically have a title and a few lines of description
                first_line = lines[0].strip()
                
                # Project titles often contain tech keywords, are capitalized, and might contain "project"
                if (any(skill.lower() in para.lower() for skill in SKILLS) and 
                    any(word[0].isupper() for word in first_line.split()) and
                    len(first_line) < 100):
                    
                    description = " ".join(line.strip() for line in lines[1:])
                    if len(description) > 10:
                        proj = {
                            "title": first_line,
                            "description": description,
                            "complexity_score": calculate_project_complexity({
                                "title": first_line,
                                "description": description
                            })
                        }
                        projects.append(proj)
    
    # Filter out non-project entries
    filtered_projects = []
    for proj in projects:
        # Ensure it's actually a project
        title_lower = proj["title"].lower()
        desc_lower = proj["description"].lower()
        
        # Skip if it doesn't look like a project
        if "resume" in title_lower or "cv" in title_lower or "reference" in title_lower:
            continue
            
        # Skip if too short
        if len(proj["description"]) < 20:
            continue
            
        # Skip if title is too generic
        if title_lower in ["experience", "education", "skills", "contact"]:
            continue
            
        filtered_projects.append(proj)
    
    # Sort projects by complexity score
    filtered_projects.sort(key=lambda x: x["complexity_score"], reverse=True)
    
    return filtered_projects[:3]  # Top 3 projects

def calculate_project_complexity(project):
    """Calculate complexity score for a project with improved analysis"""
    complexity_score = 5  # Base score
    
    # Technical keywords that indicate complexity
    complexity_indicators = [
        "architecture", "scalable", "optimized", "algorithm", "database", "cloud",
        "distributed", "microservices", "api", "security", "authentication",
        "machine learning", "ai", "data", "analytics", "visualization",
        "performance", "optimization", "real-time", "concurrent", "parallel",
        "cross-platform", "responsive", "automated", "integration", "deployment",
        "infrastructure", "monitoring", "testing"
    ]
    
    # Tech stack breadth
    tech_stack_size = sum(1 for skill in SKILLS if skill.lower() in project["description"].lower())
    
    # Adjust score based on indicators and tech stack
    full_text = (project["title"] + " " + project["description"]).lower()
    
    # Check for complexity indicators
    for indicator in complexity_indicators:
        if indicator in full_text:
            complexity_score += 0.5
    
    # Add points for technical breadth
    complexity_score += min(2, tech_stack_size * 0.4)
    
    # Check for quantifiable metrics
    metrics = re.findall(r'(\d+[%+]|\d+\s*%|\$\d+|\d+\s*users|\d+\s*clients|\d+\s*transactions)', full_text)
    complexity_score += min(1, len(metrics) * 0.5)
    
    # Check for project challenges
    challenges = ["challenge", "complex", "difficult", "solved", "improved", "enhanced", "innovative", "novel"]
    for challenge in challenges:
        if challenge in full_text:
            complexity_score += 0.25
    
    # Check for project scale
    scale_indicators = ["enterprise", "production", "large-scale", "mission-critical", "high-volume", "nationwide", "global"]
    for indicator in scale_indicators:
        if indicator in full_text:
            complexity_score += 0.5
    
    # Adjust for leadership role
    leadership = ["led", "managed", "coordinated", "directed", "spearheaded", "oversaw"]
    for lead in leadership:
        if lead in full_text:
            complexity_score += 0.5
            break
    
    # Cap at 10
    return min(10, complexity_score)

def analyze_skills(text, doc):
    """Extract and analyze skills with improved accuracy"""
    skill_data = {
        "technical": [],
        "soft": [],
        "outdated": []
    }
    
    # Potential skill section
    skills_section = None
    
    # Try to find skills section
    section_match = re.search(r'(?:^|\n)(skills|technical skills|core competencies|expertise|technologies|tech stack)(?::|\n)', text, re.IGNORECASE)
    
    if section_match:
        start_idx = section_match.start()
        
        # Look for the next section header
        next_section = re.search(r'(?:^|\n)(experience|education|projects|certifications|activities|interests|languages|references)(?::|\n)', text[start_idx:], re.IGNORECASE)
        
        if next_section:
            end_idx = start_idx + next_section.start()
            skills_section = text[start_idx:end_idx]
        else:
            skills_section = text[start_idx:]
    
    # Technical skills extraction - improved with confidence scores
    technical_skills = []
    technical_confidence = {}
    
    # First check skills section if available
    if skills_section:
        for skill in SKILLS:
            if re.search(r'\b' + re.escape(skill) + r'\b', skills_section.lower()):
                technical_skills.append(skill)
                # Higher confidence for skills listed in skills section
                technical_confidence[skill] = 0.8
    
    # Then check entire document
    for skill in SKILLS:
        if skill not in technical_confidence and re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
            technical_skills.append(skill)
            
            # Calculate confidence based on frequency and context
            matches = re.findall(r'\b' + re.escape(skill) + r'\b', text.lower())
            frequency = len(matches)
            
            # Check context - skills near "experience with" or similar phrases have higher confidence
            context_score = 0
            skill_contexts = [
                f"experience with {skill}",
                f"proficient in {skill}",
                f"knowledge of {skill}",
                f"{skill} experience",
                f"{skill} development",
                f"using {skill}",
                f"worked with {skill}"
            ]
            
            for context in skill_contexts:
                if context in text.lower():
                    context_score += 0.2
            
            # Confidence score based on frequency and context
            technical_confidence[skill] = min(0.7, 0.3 + (frequency * 0.1) + context_score)
    
    # Check for outdated technologies with improved detection
    outdated = []
    for category, techs in OUTDATED_TECH.items():
        for tech in techs:
            # Only flag if it appears without qualifiers like "migrated from X" or "replaced X"
            plain_match = re.search(r'\b' + re.escape(tech) + r'\b', text.lower())
            migration_context = re.search(r'(migrated|replaced|upgraded|moved) (from|away from)? \b' + re.escape(tech) + r'\b', text.lower())
            
            if plain_match and not migration_context:
                outdated.append(tech)
                # If this tech is in technical_skills, reduce its confidence
                if tech in technical_confidence:
                    technical_confidence[tech] *= 0.5
    
    # Soft skills extraction with improved accuracy
    # More comprehensive soft skills list
    soft_skills = [
        "communication", "teamwork", "leadership", "problem solving", "critical thinking", 
        "time management", "project management", "adaptability", "creativity", "interpersonal",
        "collaboration", "presentation", "negotiation", "conflict resolution", "mentoring",
        "decision making", "strategic thinking", "customer service", "emotional intelligence",
        "self-motivated", "detail-oriented", "analytical thinking", "initiative", "persuasion",
        "training", "team building", "client relations", "prioritization", "public speaking"
    ]
    
    found_soft_skills = []
    soft_skill_confidence = {}
    
    for skill in soft_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
            found_soft_skills.append(skill)
            
            # Calculate confidence for soft skill
            matches = re.findall(r'\b' + re.escape(skill) + r'\b', text.lower())
            frequency = len(matches)
            
            # Look for evidence/examples of the skill
            evidence_patterns = [
                f"{skill}.*example",
                f"demonstrated {skill}",
                f"{skill}.*team",
                f"{skill}.*project",
                f"{skill}.*client",
                f"{skill}.*result"
            ]
            
            evidence_score = 0
            for pattern in evidence_patterns:
                if re.search(pattern, text.lower()):
                    evidence_score += 0.2
            
            # Confidence score based on frequency and evidence
            soft_skill_confidence[skill] = min(0.8, 0.4 + (frequency * 0.1) + evidence_score)
    
    # Sort technical skills by confidence and take top ones
    sorted_technical = sorted([(skill, technical_confidence.get(skill, 0)) 
                              for skill in technical_skills], 
                              key=lambda x: x[1], reverse=True)
    
    # Sort soft skills by confidence and take top ones
    sorted_soft = sorted([(skill, soft_skill_confidence.get(skill, 0)) 
                          for skill in found_soft_skills], 
                          key=lambda x: x[1], reverse=True)
    
    # Prepare final lists
    technical_final = [skill for skill, conf in sorted_technical if conf >= 0.3][:10]
    soft_final = [skill for skill, conf in sorted_soft if conf >= 0.4][:5]
    
    # Calculate technical/soft skill balance - improved formula
    num_technical = len(technical_final)
    num_soft = len(soft_final)
    num_outdated = len(outdated)
    
    balance_score = 5  # Base score
    
    # Adjust based on skill counts
    if num_technical >= 5:
        balance_score += 2
    elif num_technical >= 3:
        balance_score += 1
    
    if num_soft >= 3:
        balance_score += 2
    elif num_soft >= 1:
        balance_score += 1
    
    # Penalize for outdated skills
    balance_score -= min(4, num_outdated)
    
    # Final balance score, capped between 1-10
    final_balance = max(1, min(10, balance_score))
    
    skill_data["technical"] = technical_final
    skill_data["soft"] = soft_final
    skill_data["outdated"] = outdated
    skill_data["balance_score"] = final_balance
    
    return skill_data

def analyze_interests(text, doc):
    """Analyze interests and passion areas with improved accuracy"""
    interest_score = {}
    
    # Enhanced analysis using word vectors and contextual clues
    # Count explicit mentions of skills
    for skill in SKILLS:
        count = len(re.findall(r'\b' + re.escape(skill) + r'\b', text.lower()))
        if count > 0:
            interest_score[skill] = count
    
    # Look for phrases indicating passion
    passion_contexts = [
        r'passionate about ([\w\s]+)',
        r'interested in ([\w\s]+)',
        r'fascinated by ([\w\s]+)',
        r'enjoy ([\w\s]+)',
        r'love ([\w\s]+)',
        r'excited by ([\w\s]+)'
    ]
    
    for pattern in passion_contexts:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            # Check if any skill is within the passionate context
            for skill in SKILLS:
                if skill in match:
                    interest_score[skill] = interest_score.get(skill, 0) + 3
    
    # Check for passion indicators near skills
    for sentence in doc.sents:
        sentence_text = sentence.text.lower()
        has_passion = any(indicator in sentence_text for indicator in PASSION_INDICATORS)
        
        if has_passion:
            for skill in SKILLS:
                if skill in sentence_text:
                    interest_score[skill] = interest_score.get(skill, 0) + 2
    
    # Look for personal projects or side activities
    project_indicators = [
        "personal project", "side project", "hobby project", "contributed to",
        "open source", "github", "portfolio", "blog", "wrote", "created", "developed",
        "built", "designed", "implemented", "volunteer"
    ]
    
    # Find sentences with project indicators
    project_sentences = []
    for sentence in doc.sents:
        if any(indicator in sentence.text.lower() for indicator in project_indicators):
            project_sentences.append(sentence.text.lower())
    
    # Check for skills in project contexts
    for sentence in project_sentences:
        for skill in SKILLS:
            if skill in sentence:
                interest_score[skill] = interest_score.get(skill, 0) + 3
    
    # Consider skills mentioned in leadership or ownership contexts
    ownership_indicators = ["led", "managed", "spearheaded", "initiated", "founded", "created", "started"]
    
    for sentence in doc.sents:
        sentence_text = sentence.text.lower()
        has_ownership = any(indicator in sentence_text for indicator in ownership_indicators)
        
        if has_ownership:
            for skill in SKILLS:
                if skill in sentence_text:
                    interest_score[skill] = interest_score.get(skill, 0) + 1
    
    # Normalize scores to 1-10 scale
    max_score = max(interest_score.values()) if interest_score else 1
    normalized_interests = {
        skill: min(10, max(1, int(5 * score / max_score) + 3))
        for skill, score in interest_score.items()
    }
    
    # Sort by score and return top interests
    sorted_interests = sorted(normalized_interests.items(), key=lambda x: x[1], reverse=True)
    return [{"skill": skill, "score": score} for skill, score in sorted_interests[:5]]

def analyze_growth_potential(text, doc):
    """Analyze growth potential with improved accuracy"""
    growth_score = 0
    growth_areas = []
    
    # Check for growth indicators with weighted scoring
    for indicator in GROWTH_INDICATORS:
        count = len(re.findall(r'\b' + re.escape(indicator) + r'\b', text.lower()))
        if count > 0:
            growth_score += min(3, count * 0.5)  # Cap contribution from any single indicator
            
            # Only add unique indicators
            if indicator not in growth_areas:
                growth_areas.append(indicator)
    
    # Check for learning patterns with contextual analysis
    learning_patterns = [
        r'(?:completed|pursuing|earned|achieved)\s+(?:a|an)\s+(?:course|certification|degree)',
        r'(?:self|auto)-taught',
        r'(?:continuously|actively)\s+(?:learning|developing|improving)',
        r'enrolled in',
        r'studying',
        r'learning',
        r'taking courses',
        r'professional development'
    ]
    
    for pattern in learning_patterns:
        if re.search(pattern, text.lower()):
            growth_score += 1
    
    # Check for career progression indicators
    progression_indicators = [
        r'promoted',
        r'advancement',
        r'career growth',
        r'progression',
        r'moved up',
        r'transitioned to',
        r'increased responsibilities'
    ]
    
    for indicator in progression_indicators:
        if re.search(indicator, text.lower()):
            growth_score += 1
            if "career progression" not in growth_areas:
                growth_areas.append("career progression")
    
    # Check for adaptability indicators
    adaptability_indicators = [
        r'adapt',
        r'flexible',
        r'versatile',
        r'pivot',
        r'transition',
        r'quick learner',
        r'rapidly',
        r'agile'
    ]
    
    adaptability_count = sum(1 for indicator in adaptability_indicators if re.search(indicator, text.lower()))
    if adaptability_count > 0:
        growth_score += min(2, adaptability_count)
        if "adaptability" not in growth_areas:
            growth_areas.append("adaptability")
    
    # Look for sentences discussing future goals
    future_indicators = ["goal", "aim", "aspire", "future", "plan", "intend", "looking to", "seeking"]
    
    for sentence in doc.sents:
        sentence_text = sentence.text.lower()
        if any(indicator in sentence_text for indicator in future_indicators):
            growth_score += 1
            if "future-oriented" not in growth_areas:
                growth_areas.append("future-oriented")
            break
    
    # Normalize score and select top growth areas
    final_growth_score = min(10, max(1, int(growth_score)))
    
    # Prioritize growth areas to return the most relevant ones
    prioritized_areas = []
    priority_terms = ["learning", "development", "growth", "career", "leadership", "education", "adaptability"]
    
    for term in priority_terms:
        matching_areas = [area for area in growth_areas if term in area]
        prioritized_areas.extend(matching_areas)
    
    # Add any remaining areas
    remaining_areas = [area for area in growth_areas if area not in prioritized_areas]
    prioritized_areas.extend(remaining_areas)
    
    return {
        "score": final_growth_score,
        "indicators": prioritized_areas[:3]  # Top 3 growth indicators
    }

def analyze_writing_quality(text, doc):
    """Analyze the writing quality with improved accuracy"""
    quality_score = 7  # Start with a baseline score
    
    # Check for weak phrases
    weak_phrase_count = sum(1 for phrase in WEAK_PHRASES if re.search(r'\b' + re.escape(phrase) + r'\b', text.lower()))
    
    # Check for strong action verbs
    action_verb_count = sum(1 for verb in STRONG_ACTION_VERBS if re.search(r'\b' + re.escape(verb) + r'\b', text.lower()))
    
    # Check for quantifiable achievements with improved detection
    quantifiable_patterns = [
        r'\d+%',
        r'increased .* by',
        r'decreased .* by',
        r'reduced .* by',
        r'improved .* by',
        r'generated .*\$[\d,]+',
        r'saved .*\$[\d,]+',
        r'[\$€£][\d,]+',
        r'\d+ users',
        r'\d+ clients',
        r'\d+ projects',
        r'\d+ team members',
        r'top \d+%'
    ]
    
    quantifiable_count = sum(1 for pattern in quantifiable_patterns if re.search(pattern, text.lower()))
    
    # Check for generic terms
    generic_count = sum(1 for term in GENERIC_TERMS if re.search(r'\b' + re.escape(term) + r'\b', text.lower()))
    
    # Advanced analysis
    
    # Check for active voice vs passive voice
    sentences = list(doc.sents)
    passive_count = 0
    active_count = 0
    
    for sent in sentences:
        sent_text = sent.text.lower()
        # Simple passive voice detection (can be improved)
        if re.search(r'\b(was|were|been|be|is|are)\b.*\b(by)\b', sent_text):
            passive_count += 1
        elif any(verb in sent_text for verb in STRONG_ACTION_VERBS):
            active_count += 1
    
    # Calculate active/passive ratio
    if passive_count + active_count > 0:
        active_ratio = active_count / (passive_count + active_count)
        # Adjust score based on active voice usage
        quality_score += (active_ratio - 0.5) * 2  # +1 point for 100% active, -1 for 0% active
    
    # Check for consistency in tense
    past_tense_verbs = re.findall(r'\b(ed|created|developed|managed|led|implemented|designed)\b', text.lower())
    present_tense_verbs = re.findall(r'\b(ing|create|develop|manage|lead|implement|design)s?\b', text.lower())
    
    # Most resumes should use past tense consistently
    if len(past_tense_verbs) + len(present_tense_verbs) > 0:
        tense_consistency = len(past_tense_verbs) / (len(past_tense_verbs) + len(present_tense_verbs))
        
        # Penalize mixed tenses (too much present tense)
        if 0.3 < tense_consistency < 0.7:
            quality_score -= 1
    
    # Check for redundancy or repetition
    words = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
    word_counts = Counter(words)
    
    # Find words repeated too frequently
    repetitive_words = [word for word, count in word_counts.items() if count > 5 and word not in ["experience", "project", "skill"]]
    
    if repetitive_words:
        quality_score -= min(1, len(repetitive_words) * 0.2)
    
    # Calculate final score with weighted factors
    quality_score -= (weak_phrase_count * 0.4)  # Penalize weak phrases
    quality_score += min(3, action_verb_count * 0.2)  # Reward action verbs (max +3)
    quality_score += min(2, quantifiable_count * 0.4)  # Reward quantifiable achievements (max +2)
    quality_score -= (generic_count * 0.4)  # Penalize generic terms
    
    # Cap score between 1-10
    return {
        "score": max(1, min(10, round(quality_score))),
        "weak_phrases_found": weak_phrase_count,
        "action_verbs_found": action_verb_count,
        "quantifiable_achievements": quantifiable_count,
        "generic_terms_found": generic_count
    }

def generate_resume_suggestions(parsed_data):
    """Generate actionable suggestions with improved personalization"""
    suggestions = []
    
    # Check writing quality
    writing_quality = parsed_data.get("writing_quality", {})
    
    if writing_quality.get("weak_phrases_found", 0) > 0:
        weak_example = next((phrase for phrase in WEAK_PHRASES if re.search(r'\b' + re.escape(phrase) + r'\b', parsed_data.get("raw_text", ""))), WEAK_PHRASES[0])
        action_examples = ", ".join(STRONG_ACTION_VERBS[:3])
        
        suggestions.append({
            "type": "writing",
            "severity": "high" if writing_quality.get("weak_phrases_found", 0) > 3 else "medium",
            "text": f"Replace passive phrases like '{weak_example}' with strong action verbs such as '{action_examples}'."
        })
    
    # Check quantifiable achievements
    if writing_quality.get("quantifiable_achievements", 0) < 2:
        suggestions.append({
            "type": "achievement",
            "severity": "high",
            "text": "Add measurable achievements with specific metrics (e.g., 'Reduced processing time by 40%' instead of 'Improved processing time')."
        })
    
    # Check for generic terms
    if writing_quality.get("generic_terms_found", 0) > 0:
        generic_term = next((term for term in GENERIC_TERMS if re.search(r'\b' + re.escape(term) + r'\b', parsed_data.get("raw_text", ""))), GENERIC_TERMS[0])
        
        suggestions.append({
            "type": "specificity",
            "severity": "medium",
            "text": f"Replace generic phrases like '{generic_term}' with specific examples that demonstrate these qualities."
        })
    
    # Check skills balance
    skills = parsed_data.get("skills_data", {})
    if len(skills.get("technical", [])) < 5:
        role = parsed_data.get("role", "software professional")
        suggestions.append({
            "type": "skills",
            "severity": "high",
            "text": f"Add more specific technical skills relevant to {role} roles."
        })
    
    if len(skills.get("soft", [])) < 2:
        suggestions.append({
            "type": "skills",
            "severity": "medium",
            "text": "Include relevant soft skills with concrete examples of how you've applied them."
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
            "text": "Add detailed projects that showcase your technical skills and problem-solving abilities."
        })
    elif any(p.get("complexity_score", 0) < 6 for p in projects):
        suggestions.append({
            "type": "projects",
            "severity": "medium",
            "text": "Enhance project descriptions with technical details, challenges overcome, and quantifiable outcomes."
        })
    
    # Education suggestion
    education = parsed_data.get("education", [])
    if not education:
        suggestions.append({
            "type": "education",
            "severity": "medium",
            "text": "Add your educational background with relevant coursework or achievements."
        })
    
    # Prioritize high severity suggestions
    high_severity = [s for s in suggestions if s["severity"] == "high"]
    medium_severity = [s for s in suggestions if s["severity"] == "medium"]
    
    # Return prioritized suggestions - high severity first, then medium
    return (high_severity + medium_severity)[:4]  # Limit to 4 top suggestions

def calculate_ats_score(parsed_data):
    """Calculate more accurate ATS score"""
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
    
    # Contact info score - weighted components
    contact_info = parsed_data.get("contact_info", {})
    contact_weights = {"name": 2, "email": 3, "phone": 3, "linkedin": 2}
    contact_score = sum(contact_weights[item] for item, value in contact_info.items() if value) / sum(contact_weights.values()) * 10
    scoring["components"]["contact_info"] = round(contact_score)
    
    # Skills match score - improved algorithm
    skills = parsed_data.get("skills_data", {})
    technical_count = len(skills.get("technical", []))
    soft_count = len(skills.get("soft", []))
    outdated_count = len(skills.get("outdated", []))
    
    # Base score calculation
    if technical_count >= 8:
        skills_score = 9
    elif technical_count >= 6:
        skills_score = 8
    elif technical_count >= 4:
        skills_score = 7
    elif technical_count >= 2:
        skills_score = 6
    else:
        skills_score = 4
    
    # Adjust for soft skills
    skills_score += min(1, soft_count * 0.5)
    
    # Penalize for outdated skills
    skills_score -= min(4, outdated_count)
    
    scoring["components"]["skills_match"] = max(1, min(10, skills_score))
    
    # Experience score
    experience_years = parsed_data.get("experience", {}).get("years", 0) or 0
    exp_positions = parsed_data.get("experience", {}).get("positions", [])
    
    # Base score from years
    if experience_years >= 10:
        experience_score = 10
    elif experience_years >= 7:
        experience_score = 9
    elif experience_years >= 5:
        experience_score = 8
    elif experience_years >= 3:
        experience_score = 7
    elif experience_years >= 1:
        experience_score = 6
    else:
        experience_score = 4
    
    # Adjust for position quality
    senior_positions = sum(1 for pos in exp_positions if any(level in pos.lower() for level in ["senior", "lead", "principal", "head", "chief", "director"]))
    experience_score = min(10, experience_score + senior_positions)
    
    scoring["components"]["experience"] = max(1, experience_score)
    
    # Education score
    education = parsed_data.get("education", [])
    if education:
        avg_edu_score = sum(edu.get("quality_score", 5) for edu in education) / len(education)
        edu_score = round(avg_edu_score)
    else:
        edu_score = 3  # Baseline if no education listed
    
    scoring["components"]["education"] = edu_score
    
    # Projects score
    projects = parsed_data.get("projects", [])
    if projects:
        avg_proj_score = sum(proj.get("complexity_score", 5) for proj in projects) / len(projects)
        project_score = round(avg_proj_score)
        
        # Bonus for multiple relevant projects
        if len(projects) >= 3:
            project_score = min(10, project_score + 1)
    else:
        project_score = 3  # Baseline if no projects listed
    
    scoring["components"]["projects"] = project_score
    
    # Writing quality score
    writing_score = parsed_data.get("writing_quality", {}).get("score", 5)
    scoring["components"]["writing_quality"] = writing_score
    
    # Calculate weighted average for overall score
    weights = {
        "contact_info": 0.1,
        "skills_match": 0.25,
        "experience": 0.25,
        "education": 0.15,
        "projects": 0.15,
        "writing_quality": 0.1
    }
    
    overall_score = sum(score * weights[component] for component, score in scoring["components"].items())
    scoring["overall"] = round(overall_score)
    
    return scoring

def extract_info(text):
    """Main function to extract and analyze resume data with improved accuracy"""
    # Clean the text for better processing
    clean_text = text.replace('\r', '\n')
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)  # Normalize line breaks
    
    # Preserve raw text for reference
    raw_text = clean_text
    
    # Create spaCy doc
    doc = nlp(clean_text.lower())
    
    # Contact information
    contact_info = extract_contact_info(clean_text, doc)
    
    # Experience analysis
    experience = analyze_experience(clean_text, doc)
    
    # Education analysis
    education = analyze_education(clean_text, doc)
    
    # Project analysis
    projects = extract_projects(clean_text, doc)
    
    # Skills analysis
    skills_data = analyze_skills(clean_text, doc)
    skills = skills_data.get("technical", [])
    
    # Interests analysis
    interests = analyze_interests(clean_text, doc)
    
    # Growth potential analysis
    growth = analyze_growth_potential(clean_text, doc)
    
    # Writing quality analysis
    writing_quality = analyze_writing_quality(clean_text, doc)
    
    # Location and role extraction with improved accuracy
    
    # Extract role
    found_role = None
    role_candidates = []
    
    # First look for explicit role statements
    role_patterns = [
        r'(seeking|looking for|interested in) (?:a|an) ([\w\s]+) (?:position|role|opportunity)',
        r'([\w\s]+) (?:professional|specialist|engineer|developer|designer)'
    ]
    
    for pattern in role_patterns:
        matches = re.findall(pattern, clean_text.lower())
        if matches:
            for match in matches:
                candidate = match[1] if len(match) > 1 else match[0]
                role_candidates.append(candidate)
    
    # Then check for known roles
    for role in ROLES:
        if re.search(r'\b' + re.escape(role) + r'\b', clean_text.lower()):
            role_candidates.append(role)
    
    # Score candidates by frequency and position in document
    role_scores = {}
    lines = clean_text.lower().split('\n')
    
    for i, line in enumerate(lines[:10]):  # Check early in document (header/summary)
        for candidate in role_candidates:
            if candidate in line:
                role_scores[candidate] = role_scores.get(candidate, 0) + (10 - i)  # Higher score if appears earlier
    
    # Also score by frequency throughout document
    for candidate in role_candidates:
        count = len(re.findall(r'\b' + re.escape(candidate) + r'\b', clean_text.lower()))
        role_scores[candidate] = role_scores.get(candidate, 0) + count
    
    # Select highest scoring role
    if role_scores:
        found_role = max(role_scores.items(), key=lambda x: x[1])[0]
    
    # Fallback based on skills if no role found
    if not found_role and skills_data.get("technical", []):
        # If no specific role found but skills are present, use a generic role based on skills
        tech_skills = skills_data.get("technical", [])
        if any(skill in ["react", "vue", "angular", "javascript", "typescript", "html", "css"] for skill in tech_skills):
            found_role = "frontend developer"
        elif any(skill in ["python", "java", "c#", "ruby", "php", "node", "express", "django", "flask"] for skill in tech_skills):
            found_role = "backend developer"
        elif any(skill in ["tensorflow", "pytorch", "machine learning", "deep learning", "ai", "data science"] for skill in tech_skills):
            found_role = "machine learning engineer"
        else:
            found_role = "software engineer"  # Default role
    
    # Extract location with improved accuracy
    location = None
    
    # First try explicit location patterns
    location_patterns = [
        r'(?:based in|located in|from|location: |location) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
        r'([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*(?:[A-Z]{2}|[A-Za-z]+)\s*\d*'  # City, State ZIP
    ]
    
    for pattern in location_patterns:
        location_match = re.search(pattern, clean_text)
        if location_match:
            location = location_match.group(1)
            break
    
    # If no matches, try named entity recognition for GPE (Geopolitical Entity)
    if not location:
        locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        if locations:
            # Prefer locations that appear early in the document (header)
            first_20_lines = ' '.join(clean_text.split('\n')[:20]).lower()
            for loc in locations:
                if loc.lower() in first_20_lines:
                    location = loc
                    break
            
            # If still no location, use the first one found
            if not location and locations:
                location = locations[0]
    
    # Default location if none found
    if not location:
        location = "Remote"
    
    # Store everything in the parsed data
    parsed_data = {
        "contact_info": contact_info,
        "skills": skills,
        "skills_data": skills_data,
        "role": found_role,
        "location": location,
        "experience": experience,
        "experience_years": experience.get("years"),
        "education": education,
        "projects": projects,
        "interests": interests,
        "growth_potential": growth,
        "writing_quality": writing_quality,
        "raw_text": raw_text
    }
    
    # Generate suggestions
    suggestions = generate_resume_suggestions(parsed_data)
    parsed_data["resume_suggestions"] = suggestions
    
    # Calculate ATS score
    ats_score = calculate_ats_score(parsed_data)
    parsed_data["ats_score"] = ats_score
    
    return parsed_data

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        try:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            text = ""
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(filename)
            elif filename.lower().endswith('.docx'):
                text = extract_text_from_docx(filename)
            else:
                os.remove(filename)  # Clean up the file
                return jsonify({"error": "Unsupported file format. Please upload a PDF or DOCX file."}), 400
            
            if not text or len(text) < 100:
                os.remove(filename)
                return jsonify({"error": "Could not extract sufficient text from the file. Please check if the file is valid."}), 400
            
            info = extract_info(text)
            os.remove(filename)  # Clean up the file
            
            return jsonify(info)
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            try:
                os.remove(filename)  # Try to clean up the file
            except:
                pass
                
            return jsonify({"error": f"Error processing resume: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

