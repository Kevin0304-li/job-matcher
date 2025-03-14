
"""
Example script demonstrating how to use the ResumeJDMatcher API directly.
"""
import json
import os
from dotenv import load_dotenv
from resume_jd_matcher import ResumeJDMatcher

# Load environment variables from .env file
load_dotenv()

def main():
    # Initialize the matcher
    matcher = ResumeJDMatcher()
    
    # Read sample resume
    with open('sample_resume.txt', 'r', encoding='utf-8') as file:
        resume_text = file.read()
    
    # Read sample job description
    with open('sample_jd_google.txt', 'r', encoding='utf-8') as file:
        jd_text = file.read()
    
    print("1. Parsing resume...")
    parsed_resume = matcher.parse_resume(resume_text)
    print(f"Resume parsed successfully. Extracted {len(parsed_resume)} sections.")
    
    print("\n2. Parsing job description...")
    parsed_jd = matcher.parse_job_description(jd_text)
    print(f"Job description parsed successfully. Extracted {len(parsed_jd)} sections.")
    
    print("\n3. Matching resume to job description...")
    match_result = matcher.match_resume_to_jd(parsed_resume, parsed_jd)
    
    # Print the matching results
    print("\n4. Match Results:")
    
    # Education match
    education = match_result.get("education", {})
    print(f"\nEducation Match:")
    print(f"Level: {education.get('match_level', 'N/A')}/7")
    print(f"Score: {education.get('match_score', 'N/A')}")
    print(f"Reasoning: {education.get('reasoning', 'N/A')}")
    
    # Work experience match
    work_exp = match_result.get("work_and_project_experience", {})
    print(f"\nWork & Project Experience Match:")
    print(f"Level: {work_exp.get('match_level', 'N/A')}/7")
    print(f"Score: {work_exp.get('match_score', 'N/A')}")
    print(f"Reasoning: {work_exp.get('reasoning', 'N/A')}")
    
    # Skills match
    skills = match_result.get("skills", {})
    print(f"\nSkills Match:")
    print(f"Level: {skills.get('match_level', 'N/A')}/7")
    print(f"Score: {skills.get('match_score', 'N/A')}")
    print(f"Reasoning: {skills.get('reasoning', 'N/A')}")
    
    # Experience years match
    exp_years = match_result.get("experience_year", {})
    print(f"\nExperience Years Match:")
    print(f"Level: {exp_years.get('match_level', 'N/A')}/7")
    print(f"Score: {exp_years.get('match_score', 'N/A')}")
    print(f"Reasoning: {exp_years.get('reasoning', 'N/A')}")
    
    # Final match
    final_match = match_result.get("Final_match", {})
    print(f"\nFINAL MATCH:")
    print(f"Level: {final_match.get('match_level', 'N/A')}/7")
    print(f"Score: {final_match.get('Final_match_score', 'N/A')}")
    print(f"Reasoning: {final_match.get('reasoning', 'N/A')}")
    
    # Save the full result to a file
    with open('example_result.json', 'w', encoding='utf-8') as f:
        json.dump({
            "parsed_resume": parsed_resume,
            "parsed_job_description": parsed_jd,
            "matching_result": match_result
        }, f, indent=2)
    
    print("\nFull results saved to example_result.json")


if __name__ == "__main__":
    main() 