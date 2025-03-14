#!/usr/bin/env python
import argparse
import json
import os
from dotenv import load_dotenv
from resume_jd_matcher import ResumeJDMatcher

# Load environment variables from .env file if it exists
load_dotenv()

def read_file_content(file_path):
    """Read content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Resume-Job Description Matching Tool')
    parser.add_argument('--resume', type=str, help='Path to resume text file')
    parser.add_argument('--jd', type=str, help='Path to job description text file')
    parser.add_argument('--output', type=str, help='Path to save output JSON (optional)')
    parser.add_argument('--api-key', type=str, help='OpenAI API key (optional, can use OPENAI_API_KEY env var)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Command for testing with sample data
    test_parser = subparsers.add_parser('test', help='Run with sample test data')
    test_parser.add_argument('--position', type=int, choices=[0, 1, 2, 3], 
                            default=3, help='Job position to test (0-3, default: 3)')
    
    return parser.parse_args()

def main():
    """Main function to run the resume-job description matcher."""
    args = parse_args()
    
    # Initialize the matcher with API key
    matcher = ResumeJDMatcher(api_key=args.api_key)
    
    if args.command == 'test':
        # Import the test function and run it
        from resume_jd_matcher import test_with_sample_data
        print("Running test with sample data...")
        position = getattr(args, 'position', 3)  # Default to position 3 if not specified
        test_with_sample_data(position_index=position)
        return
    
    # Check if resume and job description files are provided
    if not args.resume or not args.jd:
        print("Error: Both resume and job description files must be provided.")
        print("Use --resume and --jd arguments to specify file paths.")
        print("Or use 'test' command to run with sample data: python cli.py test")
        return
    
    # Read the resume content
    resume_content = read_file_content(args.resume)
    if not resume_content:
        return
    
    # Read the job description content
    jd_content = read_file_content(args.jd)
    if not jd_content:
        return
    
    print("Processing resume and job description...")
    result = matcher.process_resume_and_jd(resume_content, jd_content)
    
    # Print the matching result
    if "matching_result" in result and "error" not in result["matching_result"]:
        print("\nMatching Result:")
        print(json.dumps(result["matching_result"], indent=2))
        
        # Save output to file if requested
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                print(f"\nFull results saved to {args.output}")
            except Exception as e:
                print(f"Error saving output: {e}")
    else:
        print("Error in matching:", result.get("matching_result", {}).get("error", "Unknown error"))

if __name__ == "__main__":
    main() 