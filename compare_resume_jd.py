import os
from resume_jd_matcher import ResumeJDMatcher

def compare_files(resume_file, jd_file):
    """
    Compare a resume file with a job description file using ResumeJDMatcher.
    
    Args:
        resume_file (str): Path to the resume file
        jd_file (str): Path to the job description file
    """
    print(f"\n{'='*80}")
    print(f"Comparing resume: {resume_file}")
    print(f"With job description: {jd_file}")
    print(f"{'='*80}\n")
    
    # Check if files exist
    if not os.path.exists(resume_file):
        print(f"Error: Resume file '{resume_file}' not found.")
        return
    
    if not os.path.exists(jd_file):
        print(f"Error: Job description file '{jd_file}' not found.")
        return
    
    # Read file contents
    with open(resume_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()
    
    with open(jd_file, 'r', encoding='utf-8') as f:
        jd_text = f.read()
    
    # Initialize matcher
    matcher = ResumeJDMatcher()
    
    # Process the resume and job description
    result = matcher.process_resume_and_jd(resume_text, jd_text)
    
    # Print the matching result
    if "matching_result" in result and "error" not in result["matching_result"]:
        print("\nMATCHING RESULT:")
        print(f"{'='*80}")
        
        # Get the matching result
        matching_json = result["matching_result"]
        
        # Print each category's match level, score, and reasoning
        categories = ["education", "work_and_project_experience", "skills", "experience_year", "Final_match"]
        
        for category in categories:
            if category in matching_json:
                cat_data = matching_json[category]
                
                if category == "Final_match":
                    score_key = "Final_match_score"
                else:
                    score_key = "match_score"
                
                print(f"\n{category.upper()}")
                print(f"Match Level: {cat_data.get('match_level', 'N/A')}/7")
                print(f"Match Score: {cat_data.get(score_key, 'N/A')}")
                print(f"Reasoning: {cat_data.get('reasoning', 'N/A')}")
        
        print(f"\n{'='*80}")
        
        # Save the JSON to a file for easy access
        output_file = os.path.join("comparison_of_the_samples", "updated_comparison_result.json")
        import json
        with open(output_file, "w") as f:
            json.dump(matching_json, f, indent=2)
        print(f"The JSON result has been saved to '{output_file}'")
    else:
        print("Error in matching:", result.get("matching_result", {}).get("error", "Unknown error"))

# Compare the sample resume with the sample job description
if __name__ == "__main__":
    resume_file = os.path.join("comparison_of_the_samples", "sample_resume.txt")
    jd_file = os.path.join("comparison_of_the_samples", "sample_jd_google.txt")
    compare_files(resume_file, jd_file) 