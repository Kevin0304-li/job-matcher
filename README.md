# Resume-Job Description Matching System

This system uses AI to parse resumes and job descriptions, then evaluates how well a resume matches a job description. It provides detailed match scores and reasoning for different categories.

## Features

- Resume parsing: Extracts education, work experience, projects, skills, and total years of experience
- Job description parsing: Identifies required qualifications, skills, and experience requirements
- Resume-JD matching: Evaluates match level (1-7) and match score (percentage) for:
  - Education
  - Work and project experience
  - Skills
  - Experience years
  - Overall match
- Powered by OpenAI's GPT-4o mini model for efficient and cost-effective processing

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key:
   - Create a `.env` file in the project root and add:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - Or set it as an environment variable:
     ```
     export OPENAI_API_KEY=your_api_key_here
     ```

## Usage

### Command Line Interface

The easiest way to use this system is through the command-line interface:

```bash
# Run with sample data
python cli.py test

# Process your own resume and job description
python cli.py --resume path/to/resume.txt --jd path/to/job_description.txt

# Save the results to a file
python cli.py --resume path/to/resume.txt --jd path/to/job_description.txt --output results.json

# Provide API key directly
python cli.py --resume path/to/resume.txt --jd path/to/job_description.txt --api-key your_api_key
```

### Web Interface

The system includes a web interface built with Flask:

```bash
# Start the web server
python web_app.py
```

Then access the application at http://localhost:5000 in your browser.

### Python API

You can also use the system programmatically:

```python
from resume_jd_matcher import ResumeJDMatcher

# Initialize the matcher
matcher = ResumeJDMatcher()  # Or provide API key: ResumeJDMatcher(api_key="your_api_key")

# Process a resume and job description
resume_text = "Your resume text here..."
job_description_text = "Your job description text here..."

result = matcher.process_resume_and_jd(resume_text, job_description_text)

# Access the matching results
matching_result = result["matching_result"]
print(matching_result)
```

For a complete example of using the API, see the `example.py` file.

### Individual Functions

You can also use the individual functions:

```python
# Parse resume
parsed_resume = matcher.parse_resume(resume_text)

# Parse job description
parsed_jd = matcher.parse_job_description(job_description_text)

# Match parsed resume to parsed job description
match_result = matcher.match_resume_to_jd(parsed_resume, parsed_jd)
```

## Output Format

The matching function returns a JSON object with the following structure:

```json
{
  "education": {
    "match_level": 5,
    "match_score": "75%",
    "reasoning": "The candidate has an MS in Computer Science which matches the preferred qualification..."
  },
  "work_and_project_experience": {
    "match_level": 6,
    "match_score": "85%",
    "reasoning": "The candidate has extensive experience in ML engineering at major tech companies..."
  },
  "skills": {
    "match_level": 7,
    "match_score": "90%",
    "reasoning": "The candidate possesses all the required technical skills including Python, TensorFlow..."
  },
  "experience_year": {
    "match_level": 5,
    "match_score": "70%",
    "reasoning": "The job requires 7+ years of software engineering experience, and the candidate has around 5 years..."
  },
  "Final_match": {
    "match_level": 6,
    "Final_match_score": "80%",
    "reasoning": "Overall, the candidate is a strong match for this position with excellent technical skills..."
  }
}
```

## Error Handling

The system includes robust JSON validation and error handling to ensure proper processing of the OpenAI API responses. If there are any issues with parsing JSON or API errors, the system will provide detailed error information.

## Scripts Overview

The repository contains several scripts for different use cases:

- `resume_jd_matcher.py`: The main class implementing the parsing and matching functionality
- `cli.py`: Command-line interface for the system
- `example.py`: Example of using the Python API directly
- `web_app.py`: Simple web interface for the system
- `test_matching.py`: Test script for evaluating the system with multiple resumes and job descriptions

## Sample Files

The repository includes sample files to test the system:

- `sample_resume.txt`: A sample resume for testing
- `sample_jd_google.txt`: A sample job description for a Senior Software Engineer, AI/ML position at Google

The `test_matching.py` script also creates additional sample files in the `tests` directory:

- `tests/resumes/`: Contains sample resumes in different formats and fields
- `tests/jds/`: Contains sample job descriptions for various positions
- `tests/results/`: Stores the matching results from test runs

You can use these for testing:

```bash
# Use the provided sample files
python cli.py --resume sample_resume.txt --jd sample_jd_google.txt

# Run tests with multiple combinations
python test_matching.py
```

## Testing

Run the test function to see a sample match with provided test data:

```bash
python resume_jd_matcher.py
# or
python cli.py test
```

For more comprehensive testing with multiple resumes and job descriptions:

```bash
python test_matching.py
```

This will process multiple combinations of resumes and job descriptions and save the results in the `tests/results` directory. 