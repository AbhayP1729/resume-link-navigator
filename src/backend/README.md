
# Hire-AI Backend

This is the Flask backend for the Hire-AI resume parsing service.

## Setup

1. Install Python 3.8+ if not already installed

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
```
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Download the spaCy model:
```
python -m spacy download en_core_web_sm
```

6. Run the application:
```
flask run
```

The server will start on http://localhost:5000

## API Endpoints

### POST /api/parse-resume
Accepts a resume file (PDF or DOCX) and returns extracted information.

#### Request
- Content-Type: multipart/form-data
- Body: form data with key 'file' containing the resume file

#### Response
JSON object with:
- skills: Array of extracted skills
- role: Extracted job role
- location: Extracted location
