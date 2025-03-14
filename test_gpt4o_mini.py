#!/usr/bin/env python
"""
Test script to verify GPT-4o mini is working correctly with the resume-job description matcher.
"""
import json
import os
from dotenv import load_dotenv
from resume_jd_matcher import ResumeJDMatcher

# Load environment variables
load_dotenv()

def test_gpt4o_mini():
    """Test the resume matcher with GPT-4o mini model."""
    print("Testing Resume-JD Matcher with GPT-4o mini")
    print("-------------------------------------------")
    
    # Initialize the matcher
    matcher = ResumeJDMatcher()
    
    # Load test data
    with open('sample_resume.txt', 'r', encoding='utf-8') as f:
        resume_text = f.read()
    
    with open('sample_jd_google.txt', 'r', encoding='utf-8') as f:
        jd_text = f.read()
    
    # Test resume parsing
    print("\n1. Testing resume parsing...")
    start_time = __import__('time').time()
    parsed_resume = matcher.parse_resume(resume_text)
    parsing_time = __import__('time').time() - start_time
    print(f"Resume parsing completed in {parsing_time:.2f} seconds")
    print(f"Extracted {len(parsed_resume)} fields from resume")
    
    # Test job description parsing
    print("\n2. Testing job description parsing...")
    start_time = __import__('time').time()
    parsed_jd = matcher.parse_job_description(jd_text)
    parsing_time = __import__('time').time() - start_time
    print(f"Job description parsing completed in {parsing_time:.2f} seconds")
    print(f"Extracted {len(parsed_jd)} fields from job description")
    
    # Test matching
    print("\n3. Testing resume-JD matching...")
    start_time = __import__('time').time()
    match_result = matcher.match_resume_to_jd(parsed_resume, parsed_jd)
    matching_time = __import__('time').time() - start_time
    print(f"Matching completed in {matching_time:.2f} seconds")
    
    # Print match results
    print("\n4. Match Results:")
    print(json.dumps(match_result, indent=2))
    
    # Save results to file
    with open('gpt4o_mini_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "model": matcher.model,
            "parsed_resume": parsed_resume,
            "parsed_jd": parsed_jd,
            "match_result": match_result,
            "performance": {
                "resume_parsing_time": parsing_time,
                "jd_parsing_time": parsing_time,
                "matching_time": matching_time,
                "total_time": parsing_time * 2 + matching_time
            }
        }, f, indent=2)
    
    print(f"\nResults saved to gpt4o_mini_results.json")

if __name__ == "__main__":
    test_gpt4o_mini() 