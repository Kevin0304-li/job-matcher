#!/usr/bin/env python
"""
Simple web interface for the Resume-JD Matcher.
Run with: python web_app.py
Then access at: http://localhost:5000
"""
import json
import os
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from resume_jd_matcher import ResumeJDMatcher

# Load environment variables
load_dotenv()

app = Flask(__name__)
matcher = ResumeJDMatcher()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/match', methods=['POST'])
def match():
    """Match resume to job description."""
    resume_text = request.form.get('resume', '')
    jd_text = request.form.get('jd', '')
    
    if not resume_text or not jd_text:
        return jsonify({'error': 'Both resume and job description are required'}), 400
    
    try:
        result = matcher.process_resume_and_jd(resume_text, jd_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parse_resume', methods=['POST'])
def parse_resume():
    """Parse resume only."""
    resume_text = request.form.get('resume', '')
    
    if not resume_text:
        return jsonify({'error': 'Resume text is required'}), 400
    
    try:
        result = matcher.parse_resume(resume_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parse_jd', methods=['POST'])
def parse_jd():
    """Parse job description only."""
    jd_text = request.form.get('jd', '')
    
    if not jd_text:
        return jsonify({'error': 'Job description text is required'}), 400
    
    try:
        result = matcher.parse_job_description(jd_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create the templates directory and HTML template
def create_templates():
    """Create the templates directory and index.html file."""
    os.makedirs('templates', exist_ok=True)
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Resume-JD Matcher</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .results-container {
            max-height: 500px;
            overflow-y: auto;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        .match-category {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
            background-color: #f0f0f0;
        }
        .match-level {
            font-size: 1.2em;
            font-weight: bold;
        }
        .match-score {
            font-size: 1.2em;
            color: #0d6efd;
        }
        .final-match {
            background-color: #e7f5ff;
            border: 1px solid #0d6efd;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">Resume-Job Description Matcher</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Resume</h5>
                    </div>
                    <div class="card-body">
                        <textarea id="resume" class="form-control" rows="15" placeholder="Paste resume text here..."></textarea>
                        <button id="parseResumeBtn" class="btn btn-secondary mt-2">Parse Resume Only</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Job Description</h5>
                    </div>
                    <div class="card-body">
                        <textarea id="jd" class="form-control" rows="15" placeholder="Paste job description text here..."></textarea>
                        <button id="parseJdBtn" class="btn btn-secondary mt-2">Parse JD Only</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center my-3">
            <button id="matchBtn" class="btn btn-primary btn-lg">Match Resume to Job Description</button>
            <button id="clearBtn" class="btn btn-outline-secondary btn-lg ms-2">Clear All</button>
        </div>
        
        <div id="loading" class="text-center d-none">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Processing... This may take a minute.</p>
        </div>
        
        <div id="results" class="card d-none">
            <div class="card-header">
                <h5>Matching Results</h5>
            </div>
            <div class="card-body results-container">
                <div id="matchingResults">
                    <!-- Results will be displayed here -->
                </div>
                
                <div class="mt-4">
                    <h6>Raw JSON:</h6>
                    <pre id="rawJson"></pre>
                </div>
            </div>
        </div>
        
        <div id="parseResults" class="card d-none">
            <div class="card-header">
                <h5>Parsing Results</h5>
            </div>
            <div class="card-body results-container">
                <pre id="parseJson"></pre>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('matchBtn').addEventListener('click', async () => {
            const resume = document.getElementById('resume').value;
            const jd = document.getElementById('jd').value;
            
            if (!resume || !jd) {
                alert('Please provide both resume and job description');
                return;
            }
            
            showLoading();
            clearResults();
            
            try {
                const response = await fetch('/match', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'resume': resume,
                        'jd': jd
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(`Error: ${data.error}`);
                    return;
                }
                
                displayMatchResults(data);
            } catch (error) {
                alert(`Error: ${error.message}`);
            } finally {
                hideLoading();
            }
        });
        
        document.getElementById('parseResumeBtn').addEventListener('click', async () => {
            const resume = document.getElementById('resume').value;
            
            if (!resume) {
                alert('Please provide a resume to parse');
                return;
            }
            
            showLoading();
            clearResults();
            
            try {
                const response = await fetch('/parse_resume', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'resume': resume
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(`Error: ${data.error}`);
                    return;
                }
                
                displayParseResults(data, 'Resume');
            } catch (error) {
                alert(`Error: ${error.message}`);
            } finally {
                hideLoading();
            }
        });
        
        document.getElementById('parseJdBtn').addEventListener('click', async () => {
            const jd = document.getElementById('jd').value;
            
            if (!jd) {
                alert('Please provide a job description to parse');
                return;
            }
            
            showLoading();
            clearResults();
            
            try {
                const response = await fetch('/parse_jd', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'jd': jd
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(`Error: ${data.error}`);
                    return;
                }
                
                displayParseResults(data, 'Job Description');
            } catch (error) {
                alert(`Error: ${error.message}`);
            } finally {
                hideLoading();
            }
        });
        
        document.getElementById('clearBtn').addEventListener('click', () => {
            document.getElementById('resume').value = '';
            document.getElementById('jd').value = '';
            clearResults();
        });
        
        function showLoading() {
            document.getElementById('loading').classList.remove('d-none');
        }
        
        function hideLoading() {
            document.getElementById('loading').classList.add('d-none');
        }
        
        function clearResults() {
            document.getElementById('results').classList.add('d-none');
            document.getElementById('parseResults').classList.add('d-none');
            document.getElementById('matchingResults').innerHTML = '';
            document.getElementById('rawJson').innerHTML = '';
            document.getElementById('parseJson').innerHTML = '';
        }
        
        function displayMatchResults(data) {
            const matchingResults = document.getElementById('matchingResults');
            const rawJson = document.getElementById('rawJson');
            
            if (data.matching_result) {
                const result = data.matching_result;
                let html = '';
                
                // Education
                if (result.education) {
                    html += createCategoryHTML('Education', result.education);
                }
                
                // Work & Project Experience
                if (result.work_and_project_experience) {
                    html += createCategoryHTML('Work & Project Experience', result.work_and_project_experience);
                }
                
                // Skills
                if (result.skills) {
                    html += createCategoryHTML('Skills', result.skills);
                }
                
                // Experience Years
                if (result.experience_year) {
                    html += createCategoryHTML('Experience Years', result.experience_year);
                }
                
                // Final Match
                if (result.Final_match) {
                    html += createCategoryHTML('Final Match', result.Final_match, true);
                }
                
                matchingResults.innerHTML = html;
                rawJson.textContent = JSON.stringify(data, null, 2);
                document.getElementById('results').classList.remove('d-none');
            }
        }
        
        function createCategoryHTML(categoryName, categoryData, isFinal = false) {
            const matchLevel = categoryData.match_level || 'N/A';
            const matchScore = isFinal ? categoryData.Final_match_score : categoryData.match_score;
            const reasoning = categoryData.reasoning || 'No reasoning provided';
            
            return `
                <div class="match-category ${isFinal ? 'final-match' : ''}">
                    <h5>${categoryName}</h5>
                    <div class="d-flex justify-content-between">
                        <div>
                            <span class="match-level">Level: ${matchLevel}/7</span>
                        </div>
                        <div>
                            <span class="match-score">Score: ${matchScore}</span>
                        </div>
                    </div>
                    <div class="mt-2">
                        <strong>Reasoning:</strong>
                        <p>${reasoning}</p>
                    </div>
                </div>
            `;
        }
        
        function displayParseResults(data, type) {
            const parseJson = document.getElementById('parseJson');
            parseJson.textContent = JSON.stringify(data, null, 2);
            document.getElementById('parseResults').classList.remove('d-none');
        }
    </script>
</body>
</html>
"""
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    create_templates()
    print("Web app is starting...")
    print("Access the application at http://localhost:5000")
    app.run(debug=True) 