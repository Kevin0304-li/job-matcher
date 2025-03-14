#!/usr/bin/env python
"""
Test script for the Resume-JD Matcher.
This script evaluates the system against sample resumes and job descriptions.
"""
import json
import os
from resume_jd_matcher import ResumeJDMatcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestMatching:
    def __init__(self):
        """Initialize the test matcher."""
        self.matcher = ResumeJDMatcher()
        
        # Create the tests directory if it doesn't exist
        os.makedirs('tests', exist_ok=True)
        os.makedirs('tests/resumes', exist_ok=True)
        os.makedirs('tests/jds', exist_ok=True)
        os.makedirs('tests/results', exist_ok=True)
        
        # Create sample test files if they don't exist
        self._create_sample_files()
    
    def _create_sample_files(self):
        """Create sample test files if they don't exist."""
        # Create sample software engineer resume
        if not os.path.exists('tests/resumes/software_engineer.txt'):
            with open('tests/resumes/software_engineer.txt', 'w', encoding='utf-8') as f:
                f.write("""Jane Smith
jsmith@email.com | (123) 456-7890

EDUCATION
Master of Science in Computer Science, Stanford University, 2016-2018
Bachelor of Science in Software Engineering, MIT, 2012-2016

WORK EXPERIENCE
Senior Software Engineer, Amazon, 2020-Present
- Lead development of microservices architecture for e-commerce platform
- Implemented CI/CD pipeline reducing deployment time by 40%
- Optimized database queries resulting in 30% performance improvement

Software Engineer, Microsoft, 2018-2020
- Developed features for Microsoft Office suite
- Collaborated with UX team to improve user interface
- Fixed critical bugs affecting millions of users

Software Development Intern, Google, Summer 2017
- Built internal tools for developer productivity
- Created automated testing framework

PROJECTS
E-commerce Platform (2019)
- Full-stack web application using React and Node.js
- Implemented payment processing and inventory management

SKILLS
- Programming: Java, Python, JavaScript, C#, SQL
- Web: React, Angular, Node.js, HTML/CSS
- Tools: Git, Docker, Kubernetes, Jenkins
- Cloud: AWS, Azure
- Methodologies: Agile, Scrum, TDD
""")
        
        # Create sample data scientist resume
        if not os.path.exists('tests/resumes/data_scientist.txt'):
            with open('tests/resumes/data_scientist.txt', 'w', encoding='utf-8') as f:
                f.write("""Robert Johnson
rjohnson@email.com | (123) 567-8901

EDUCATION
Ph.D. in Statistics, UC Berkeley, 2015-2019
Master of Science in Data Science, NYU, 2013-2015
Bachelor of Science in Mathematics, UCLA, 2009-2013

WORK EXPERIENCE
Senior Data Scientist, Netflix, 2019-Present
- Developed recommendation algorithms improving user engagement by 15%
- Built predictive models for content performance
- Led a team of 3 data scientists on personalization projects

Data Scientist, Facebook, 2015-2019
- Created machine learning models for ad targeting
- Analyzed user behavior patterns to improve product features
- Implemented A/B testing framework for new features

Research Assistant, UC Berkeley, 2015-2019
- Published 3 papers on statistical methods in machine learning
- Collaborated with industry partners on applied research

PROJECTS
Customer Churn Prediction (2020)
- Built models to predict subscription cancellations
- Achieved 85% accuracy using ensemble methods

Image Recognition System (2018)
- Developed CNN for image classification
- Trained on custom dataset with 95% accuracy

SKILLS
- Programming: Python, R, SQL, Scala
- ML/Data: Scikit-learn, TensorFlow, PyTorch, Pandas, NumPy
- Big Data: Spark, Hadoop, Kafka
- Visualization: Tableau, Matplotlib, Seaborn
- Statistics: Hypothesis testing, Regression, Time Series Analysis
""")
        
        # Create sample software engineer job description
        if not os.path.exists('tests/jds/senior_software_engineer.txt'):
            with open('tests/jds/senior_software_engineer.txt', 'w', encoding='utf-8') as f:
                f.write("""Senior Software Engineer at Tech Innovations

About the Role:
Tech Innovations is seeking a Senior Software Engineer to join our engineering team. You will be responsible for designing, developing, and maintaining high-quality software solutions that meet business requirements.

Responsibilities:
- Design and develop scalable, high-performance applications
- Lead technical projects and mentor junior engineers
- Collaborate with cross-functional teams to define and implement new features
- Ensure code quality through code reviews and testing
- Troubleshoot and resolve complex technical issues
- Stay current with emerging technologies and industry trends

Requirements:
- 5+ years of professional software development experience
- Strong proficiency in Java, Python, or similar programming languages
- Experience with web technologies (JavaScript, React, Node.js)
- Knowledge of relational databases and SQL
- Experience with cloud platforms (AWS, Azure, or GCP)
- Bachelor's degree in Computer Science or related field
- Excellent problem-solving and communication skills

Preferred Qualifications:
- Experience with microservices architecture
- Knowledge of containerization (Docker, Kubernetes)
- CI/CD implementation experience
- Experience with Agile development methodologies
""")
        
        # Create sample data scientist job description
        if not os.path.exists('tests/jds/senior_data_scientist.txt'):
            with open('tests/jds/senior_data_scientist.txt', 'w', encoding='utf-8') as f:
                f.write("""Senior Data Scientist at Data Analytics Inc.

About the Role:
Data Analytics Inc. is looking for a Senior Data Scientist to join our team. You will work on complex data problems and develop advanced machine learning solutions that drive business impact.

Responsibilities:
- Develop and implement machine learning models to solve business problems
- Analyze large datasets to extract actionable insights
- Build data pipelines for model training and deployment
- Collaborate with product and engineering teams
- Present findings to stakeholders and executives
- Mentor junior data scientists

Requirements:
- 4+ years of experience in data science or related field
- Advanced degree (MS or PhD) in Statistics, Computer Science, or related field
- Strong programming skills in Python, R, or similar languages
- Experience with machine learning frameworks (Scikit-learn, TensorFlow, PyTorch)
- Proficiency in SQL and data manipulation
- Experience with big data technologies (Spark, Hadoop)
- Excellent communication and presentation skills

Preferred Qualifications:
- Experience in deploying ML models to production
- Knowledge of deep learning techniques
- Experience with cloud platforms (AWS, GCP, Azure)
- Published research in machine learning or data science
""")
    
    def run_tests(self):
        """Run matching tests with sample files."""
        print("Running Resume-JD Matching Tests")
        print("================================")
        
        # Get all resume files
        resume_files = [f for f in os.listdir('tests/resumes') if f.endswith('.txt')]
        
        # Get all job description files
        jd_files = [f for f in os.listdir('tests/jds') if f.endswith('.txt')]
        
        # Run tests for all combinations
        for resume_file in resume_files:
            for jd_file in jd_files:
                self._run_single_test(resume_file, jd_file)
    
    def _run_single_test(self, resume_file, jd_file):
        """Run a single matching test."""
        print(f"\nTesting: {resume_file} against {jd_file}")
        print("-" * 50)
        
        # Read resume content
        with open(f'tests/resumes/{resume_file}', 'r', encoding='utf-8') as f:
            resume_content = f.read()
        
        # Read job description content
        with open(f'tests/jds/{jd_file}', 'r', encoding='utf-8') as f:
            jd_content = f.read()
        
        # Match resume to job description
        result = self.matcher.process_resume_and_jd(resume_content, jd_content)
        
        # Save the result
        result_file = f"{os.path.splitext(resume_file)[0]}_vs_{os.path.splitext(jd_file)[0]}.json"
        with open(f'tests/results/{result_file}', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        # Print the matching results
        if "matching_result" in result and "error" not in result["matching_result"]:
            match_result = result["matching_result"]
            
            # Print education match
            if "education" in match_result:
                edu = match_result["education"]
                print(f"Education: Level {edu.get('match_level', 'N/A')}/7 - {edu.get('match_score', 'N/A')}")
            
            # Print work experience match
            if "work_and_project_experience" in match_result:
                work = match_result["work_and_project_experience"]
                print(f"Work & Projects: Level {work.get('match_level', 'N/A')}/7 - {work.get('match_score', 'N/A')}")
            
            # Print skills match
            if "skills" in match_result:
                skills = match_result["skills"]
                print(f"Skills: Level {skills.get('match_level', 'N/A')}/7 - {skills.get('match_score', 'N/A')}")
            
            # Print experience years match
            if "experience_year" in match_result:
                exp = match_result["experience_year"]
                print(f"Experience Years: Level {exp.get('match_level', 'N/A')}/7 - {exp.get('match_score', 'N/A')}")
            
            # Print final match
            if "Final_match" in match_result:
                final = match_result["Final_match"]
                print(f"OVERALL MATCH: Level {final.get('match_level', 'N/A')}/7 - {final.get('Final_match_score', 'N/A')}")
            
            print(f"Full results saved to: tests/results/{result_file}")
        else:
            print("Error in matching:", result.get("matching_result", {}).get("error", "Unknown error"))

if __name__ == "__main__":
    tester = TestMatching()
    tester.run_tests() 