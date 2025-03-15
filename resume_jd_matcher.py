import json
import logging
import os
from typing import Dict, Any, List, Tuple
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeJDMatcher:
    def __init__(self, api_key=None):
        """
        Initialize the ResumeJDMatcher with OpenAI API key.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, it will try to get from environment variable.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not provided. Please set the OPENAI_API_KEY environment variable or provide it during initialization.")
        
        self.client = OpenAI(api_key=self.api_key)
        # Set the model to use for all API calls
        self.model = "gpt-4o-mini"
        logger.info(f"Using OpenAI model: {self.model}")
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text to extract relevant information using OpenAI API.
        
        Args:
            resume_text (str): The text content of the resume
            
        Returns:
            Dict[str, Any]: Parsed resume data containing education, work experience, 
                           projects, skills, and total years of experience
        """
        system_prompt = "Extract the following details from the resume: Education, Work Experience, Projects, Skills, and Total Years of Experience."
        user_prompt = resume_text
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,  # Using GPT-4o mini for better efficiency
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3  # Lower temperature for more consistent extraction
            )
            
            parsed_resume = response.choices[0].message.content
            logger.info("Resume parsed successfully")
            
            # Try to convert the response to a structured format if it's not already
            try:
                structured_data = json.loads(self._clean_json_string(parsed_resume))
                return structured_data
            except json.JSONDecodeError:
                # If the response is not JSON, create a structured format manually
                logger.warning("Resume parsing response was not valid JSON, creating structured format manually")
                return {
                    "parsed_resume_text": parsed_resume,
                    "raw_resume": resume_text
                }
                
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return {"error": str(e), "raw_resume": resume_text}
    
    def parse_job_description(self, jd_text: str) -> Dict[str, Any]:
        """
        Parse job description text to extract relevant information using OpenAI API.
        
        Args:
            jd_text (str): The text content of the job description
            
        Returns:
            Dict[str, Any]: Parsed job description data containing required qualifications,
                           skills, and experience
        """
        system_prompt = "Identify and extract the required qualifications, skills, and experience from the job description."
        user_prompt = jd_text
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            parsed_jd = response.choices[0].message.content
            logger.info("Job description parsed successfully")
            
            # Try to convert the response to a structured format if it's not already
            try:
                structured_data = json.loads(self._clean_json_string(parsed_jd))
                return structured_data
            except json.JSONDecodeError:
                # If the response is not JSON, create a structured format manually
                logger.warning("Job description parsing response was not valid JSON, creating structured format manually")
                return {
                    "parsed_jd_text": parsed_jd,
                    "raw_jd": jd_text
                }
                
        except Exception as e:
            logger.error(f"Error parsing job description: {e}")
            return {"error": str(e), "raw_jd": jd_text}
    
    def match_resume_to_jd(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match the parsed resume against the parsed job description using OpenAI API.
        
        Args:
            resume_data (Dict[str, Any]): Parsed resume data
            jd_data (Dict[str, Any]): Parsed job description data
            
        Returns:
            Dict[str, Any]: Matching results with match levels and scores for each category
        """
        system_prompt = """
        Compare the candidate's resume with the job description and evaluate the match level and score for Education, Work and Project Experience, Skills, and Experience Years. Provide reasoning for each category.
        
        IMPORTANT EVALUATION GUIDELINES:
        
        1. EDUCATION:
           - Consider the RELEVANCE of the education field more than the specific degree name
           - A degree in a related field should score well, even if not an exact match
           - Example: For an AI/ML job, degrees in Robotics or Computer Engineering are HIGHLY relevant and should score 75-85%
           - Technical degrees should be considered very valuable for technical roles, regardless of the exact name
        
        2. WORK AND PROJECT EXPERIENCE:
           - VALUE TRANSFERABLE SKILLS highly - many skills are applicable across industries
           - Product management experience is valuable for product roles even in different industries
           - Technical program management experience shows technical understanding even if not direct hands-on development
           - Leadership roles in one industry often translate well to similar roles in other industries
           - CRITICAL: Experience with consumer-scale products (millions of users) should be considered EQUIVALENT to enterprise rollouts when the job mentions "scale"
           - AI/ML product experience should be weighted heavily for AI/ML roles, even if not in the exact same domain
           - Conversational AI experience (voice assistants, chatbots) is DIRECTLY RELEVANT to any job involving LLMs, chatbots, or conversational interfaces
        
        3. SKILLS:
           - Look for CORE SKILLS that transfer between roles (leadership, technical skills, domain knowledge)
           - For technical roles, value specific technical skills mentioned in the resume that match the job
           - For product/management roles, emphasize leadership, strategy, and cross-functional collaboration
           - IMPORTANT: Technical understanding and exposure to ML/AI concepts count significantly, even if not direct engineering experience
           - Any patent or coding experience should be weighted heavily when evaluating technical acumen
           - Experience with Python or other programming languages should count toward technical skills, even for product roles
        
        4. EXPERIENCE YEARS:
           - Consider both the quantity AND relevance of experience:
           - A candidate with many years of experience in an unrelated field should receive a LOW score (level 1-3)
           - A candidate with fewer years but highly relevant experience should receive a HIGHER score (level 4-5)
           - Value directly relevant experience highest, but also credit related experience in different industries
           - For role-specific requirements (e.g., "7+ years software engineering"), be precise about matching
           - CRITICAL: Leadership experience in adjacent domains should be counted more strongly 
        
        IMPORTANT: Calibrate your scoring based on these examples:
        - Google AI/ML Engineering Role: A candidate with TPM experience at Google on AI products should score around 75-80% (increased from previous 70%) as technical program management requires deep technical understanding
        - Product Management Roles: Experience in different industries should receive 65-75% scores if the product management skills are transferable (increased from 55-65%)
        - Gaming Industry: Product experience in other technical fields should score around 60% even without direct gaming experience (increased from 50%)
        - Conversational AI roles: Experience with voice assistants or chatbots should score 80-85% for conversational AI jobs, as these skills are directly transferable
        
        When providing reasoning, be EXTREMELY SPECIFIC and DETAILED about why a candidate didn't receive a higher score:
        - Identify SPECIFIC skills, experiences, or qualifications that are missing
        - Point out CONCRETE GAPS between the job requirements and the candidate's profile
        - Explain what would have made the candidate's experience more relevant to the position
        - For experience that is somewhat relevant but not perfect, explain EXACTLY what aspects are aligned and what aspects are misaligned
        
        Avoid vague statements like "candidate has some relevant experience." Instead, provide precise details like "candidate has experience with AI product management at Google but lacks direct hands-on ML engineering experience that would be critical for this role."
        
        For each category, use the entire range of scores (1-7) properly:
        - Scores of 1-2 should only be used for completely mismatched profiles
        - Scores of 3-4 should be used for partial matches with significant gaps
        - Scores of 5-6 should be used for strong matches with minor gaps
        - Score of 7 should be used for perfect matches
        
        Be thorough in your evaluation and provide detailed reasoning for each category.
        
        CRITICAL: Your output MUST be ONLY a valid JSON object with no additional text, comments, or explanations before or after the JSON. Do not wrap the JSON in markdown code blocks or any other formatting.
        """
        
        user_prompt = f"""
        PARSED RESUME:
        {json.dumps(resume_data, indent=2)}
        
        PARSED JOB DESCRIPTION:
        {json.dumps(jd_data, indent=2)}
        
        Please evaluate the match level (1-7, where 1 is lowest and 7 is highest) and match score (as a percentage) for each of the following categories:
        
        1. Education - Assess relevance of the field of study, not just the degree name. Robotics degrees are HIGHLY relevant for AI/ML positions and should score 75-85%, not just "somewhat relevant."
        
        2. Work and Project Experience - Value transferable skills across industries. Product management experience in one industry is valuable for product roles in other industries. Technical program management demonstrates technical understanding.
        
        IMPORTANT: When assessing experience, consider these critical points:
        - Experience with products at scale (millions of users) should be considered EQUIVALENT to enterprise rollouts
        - Experience with conversational AI (like Google Assistant) is DIRECTLY RELEVANT to any role involving LLMs, chatbots, or voice interfaces
        - Leadership roles in adjacent domains should be given stronger weight
        
        3. Skills - Look for core skills that transfer between roles. For technical positions, prioritize specific technical skills. For product roles, emphasize leadership and strategy skills. For technical roles, missing a key required framework or tool (e.g., TensorFlow for ML engineers, Unreal for game devs) should result in a skills match of 60-70%. If the candidate has foundational experience but lacks role-specific tools, they may score 70-80%.
        
        CRITICAL SKILLS ASSESSMENT:
        - Consider ANY coding experience as technical skill, even for product roles
        - Patent experience indicates technical depth and should be weighted accordingly
        - Technical understanding can come from program management, not just hands-on coding
        
        4. Experience Years - CRITICAL NOTE: Consider both quantity AND relevance. For specific requirements like "7+ years of software engineering," assess if the candidate truly has that exact experience. Recognize that leadership roles in one industry can be valuable in another, but direct, relevant experience should score highest.
        
        Then provide an overall match level and score. For each category and the final match, provide detailed reasoning.
        
        For any score below 6/7, you MUST provide specific details about what's missing or misaligned in the candidate's profile compared to the job requirements. Explain exactly what would need to be improved for a higher score.
        
        IMPORTANT CALIBRATION GUIDANCE:
        - For GOOGLE Senior Software Engineer AI/ML: TPMs in AI should typically score between 70-80%, depending on their level of hands-on ML development. If a TPM has AI experience but no ML software engineering experience, expect a score around 70-75%.
        - For product management roles outside the candidate's primary industry, expect a score between 65-75%. Candidates with general product experience but lacking key domain-specific expertise (e.g., monetization, gaming, AI, etc.) should score closer to 65-70%.
        - For conversational AI roles: Candidates with voice assistant or chatbot experience should score 80-85%, as the skills are directly transferable.
        - For Epic Games: Product experience from non-gaming industries should score between 50-60%, depending on the relevance of the transferable skills.
        
        IMPORTANT FORMATTING REQUIREMENTS:
        1. ONLY return a JSON object with NO additional text, explanation, or markdown formatting
        2. Do NOT include any text before or after the JSON object
        3. Ensure all quotes are double quotes (") not single quotes (')
        4. Ensure match_score values are always formatted as strings with percentage sign (e.g., "85%")
        5. Do NOT include any code block markers like ``` or ```json
        6. Do NOT include any extra explanation outside the reasoning fields
        
        Format your response as a JSON object with the following structure:
        {{
          "education": {{"match_level": 1-7, "match_score": "xx%", "reasoning": ""}},
          "work_and_project_experience": {{"match_level": 1-7, "match_score": "xx%", "reasoning": ""}},
          "skills": {{"match_level": 1-7, "match_score": "xx%", "reasoning": ""}},
          "experience_year": {{"match_level": 1-7, "match_score": "xx%", "reasoning": ""}},
          "Final_match": {{"match_level": 1-7, "Final_match_score": "xx%", "reasoning": ""}}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}  # Request JSON format explicitly if using LLMs that support this
            )
            
            match_result_text = response.choices[0].message.content
            logger.info("Resume-JD matching completed successfully")
            
            try:
                match_result = json.loads(self._clean_json_string(match_result_text))
                expected_keys = ["education", "work_and_project_experience", "skills", "experience_year", "Final_match"]
                for key in expected_keys:
                    if key not in match_result:
                        logger.warning(f"Missing expected key '{key}' in match result. Adding default value.")
                        if key == "Final_match":
                            match_result[key] = {"match_level": 1, "Final_match_score": "0%", "reasoning": "Missing data"}
                        else:
                            match_result[key] = {"match_level": 1, "match_score": "0%", "reasoning": "Missing data"}
                
                return match_result
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing match result JSON: {e}")
                logger.error(f"Received text: {match_result_text}")
                
                # Try to extract JSON from the text if possible
                match_result = self._extract_json_from_text(match_result_text)
                if match_result:
                    return match_result
                
                # If everything fails, return a valid JSON with default values
                return {
                    "education": {"match_level": 1, "match_score": "0%", "reasoning": f"Failed to parse response: {str(e)}"},
                    "work_and_project_experience": {"match_level": 1, "match_score": "0%", "reasoning": "JSON parsing error"},
                    "skills": {"match_level": 1, "match_score": "0%", "reasoning": "JSON parsing error"},
                    "experience_year": {"match_level": 1, "match_score": "0%", "reasoning": "JSON parsing error"},
                    "Final_match": {"match_level": 1, "Final_match_score": "0%", "reasoning": "JSON parsing error"}
                }
                
        except Exception as e:
            logger.error(f"Error matching resume to job description: {e}")
            # Return a valid JSON with error information instead of an error object
            return {
                "education": {"match_level": 1, "match_score": "0%", "reasoning": f"API Error: {str(e)}"},
                "work_and_project_experience": {"match_level": 1, "match_score": "0%", "reasoning": "Processing error"},
                "skills": {"match_level": 1, "match_score": "0%", "reasoning": "Processing error"},
                "experience_year": {"match_level": 1, "match_score": "0%", "reasoning": "Processing error"},
                "Final_match": {"match_level": 1, "Final_match_score": "0%", "reasoning": "Processing error"}
            }
    
    def _clean_json_string(self, json_string: str) -> str:
        """
        Clean a JSON string to make it more likely to parse correctly.
        
        Args:
            json_string (str): The JSON string to clean
            
        Returns:
            str: Cleaned JSON string
        """
        if not json_string:
            return "{}"
            
        # Try to extract JSON if it's embedded in markdown or other text
        if "```json" in json_string:
            # Extract JSON from markdown code block
            start = json_string.find("```json") + 7
            end = json_string.find("```", start)
            if end != -1:
                json_string = json_string[start:end].strip()
        elif "```" in json_string:
            # Extract from generic code block
            start = json_string.find("```") + 3
            end = json_string.find("```", start)
            if end != -1:
                json_string = json_string[start:end].strip()
                
        # Remove any non-JSON text before the first '{' and after the last '}'
        first_brace = json_string.find('{')
        if first_brace != -1:
            last_brace = json_string.rfind('}')
            if last_brace != -1 and last_brace > first_brace:
                json_string = json_string[first_brace:last_brace+1]
        
        # Replace single quotes with double quotes for JSON compatibility
        json_string = json_string.replace("'", '"')
        
        # Fix common JSON formatting issues
        json_string = json_string.replace("False", "false").replace("True", "true").replace("None", "null")
        
        # Fix common typos in JSON key names according to our expected structure
        if "Final_match_score" not in json_string and "final_match_score" in json_string.lower():
            json_string = json_string.replace("final_match_score", "Final_match_score")
            
        return json_string
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Try to extract a JSON object from text using various methods.
        
        Args:
            text (str): Text that may contain JSON
            
        Returns:
            Dict[str, Any]: Extracted JSON object or empty dict if extraction fails
        """
        # If text is empty, return empty dict
        if not text:
            return {}
        
        # First try regex-based extraction for more precision
        regex_result = self._extract_json_with_regex(text)
        if regex_result:
            return regex_result
        
        # Try multiple approaches to extract JSON
        try:
            # Look for text between curly braces
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = text[start:end]
                # Try to repair common JSON issues before parsing
                repaired_json = self._attempt_json_repair(json_str)
                try:
                    return json.loads(repaired_json)
                except:
                    # If repair failed, try original
                    return json.loads(json_str)
        except:
            pass
            
        # If that failed, try to identify and fix the most common JSON structural errors
        try:
            # Create a fallback JSON with the expected structure
            fallback_json = {
                "education": {"match_level": 1, "match_score": "0%", "reasoning": "Failed to parse"},
                "work_and_project_experience": {"match_level": 1, "match_score": "0%", "reasoning": "Failed to parse"},
                "skills": {"match_level": 1, "match_score": "0%", "reasoning": "Failed to parse"},
                "experience_year": {"match_level": 1, "match_score": "0%", "reasoning": "Failed to parse"},
                "Final_match": {"match_level": 1, "Final_match_score": "0%", "reasoning": "Failed to parse"}
            }
            
            # Try to extract each section separately if full JSON parsing fails
            if '"education"' in text:
                edu_start = text.find('"education"')
                next_section = min(x for x in [text.find('"work_and_project_experience"', edu_start), 
                                            text.find('"skills"', edu_start),
                                            text.find('"experience_year"', edu_start),
                                            text.find('"Final_match"', edu_start)] if x > 0)
                if next_section > 0:
                    # This would at least salvage one section
                    section_text = '{' + text[edu_start:next_section-1] + '}'
                    try:
                        section_json = json.loads(section_text)
                        fallback_json.update(section_json)
                    except:
                        pass
            
            return fallback_json
        except:
            # Last resort - return a valid JSON with error messages
            return {
                "education": {"match_level": 1, "match_score": "0%", "reasoning": "JSON parsing error"},
                "work_and_project_experience": {"match_level": 1, "match_score": "0%", "reasoning": "JSON parsing error"},
                "skills": {"match_level": 1, "match_score": "0%", "reasoning": "JSON parsing error"},
                "experience_year": {"match_level": 1, "match_score": "0%", "reasoning": "JSON parsing error"},
                "Final_match": {"match_level": 1, "Final_match_score": "0%", "reasoning": "JSON parsing error"}
            }
            
    def _extract_json_with_regex(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text using regular expressions for more precision.
        
        Args:
            text (str): Text that may contain JSON
            
        Returns:
            Dict[str, Any]: Extracted JSON object or empty dict if extraction fails
        """
        import re
        
        # Pattern to find JSON objects with proper nesting balance
        # This pattern looks for balanced curly braces with content between them
        pattern = r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})'
        matches = re.findall(pattern, text)
        
        if matches:
            # Try each match until we find valid JSON
            for potential_json in matches:
                try:
                    cleaned_json = self._clean_json_string(potential_json)
                    return json.loads(cleaned_json)
                except json.JSONDecodeError:
                    # If this match fails, try with repair
                    try:
                        repaired_json = self._attempt_json_repair(cleaned_json)
                        return json.loads(repaired_json)
                    except:
                        continue
        
        # Return empty dict if no valid JSON found
        return {}
        
    def _classify_json_error(self, json_string: str) -> Dict[str, bool]:
        """
        Classify the type of JSON error for better diagnostics.
        
        Args:
            json_string (str): The JSON string to analyze
            
        Returns:
            Dict[str, bool]: Dictionary with error type flags
        """
        import re
        
        error_types = {
            "missing_quotes": False,
            "unbalanced_braces": False,
            "trailing_comma": False,
            "invalid_property_name": False,
            "invalid_value": False
        }
        
        # Check for unbalanced braces
        if json_string.count('{') != json_string.count('}'):
            error_types["unbalanced_braces"] = True
        
        # Check for missing quotes around property names
        if re.search(r'[\{\,]\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', json_string):
            error_types["missing_quotes"] = True
        
        # Check for trailing commas
        if re.search(r',\s*[\}\]]', json_string):
            error_types["trailing_comma"] = True
        
        # Check for invalid property values
        if re.search(r':\s*$', json_string) or re.search(r':\s*,', json_string):
            error_types["invalid_value"] = True
        
        # Log detailed error information
        logger.error(f"JSON error classification: {error_types}")
        
        return error_types
        
    def _attempt_json_repair(self, json_string: str) -> str:
        """
        Attempt to repair common JSON formatting issues.
        
        Args:
            json_string (str): The potentially malformed JSON string
            
        Returns:
            str: Repaired JSON string
        """
        import re
        
        # Classify error types
        error_types = self._classify_json_error(json_string)
        
        # Fix missing quotes around property names
        if error_types["missing_quotes"]:
            json_string = re.sub(r'([\{\,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_string)
        
        # Remove trailing commas
        if error_types["trailing_comma"]:
            json_string = re.sub(r',(\s*[\}\]])', r'\1', json_string)
        
        # Balance braces if needed (simple case)
        if error_types["unbalanced_braces"]:
            open_count = json_string.count('{')
            close_count = json_string.count('}')
            if open_count > close_count:
                json_string += "}" * (open_count - close_count)
            elif close_count > open_count:
                json_string = "{" * (close_count - open_count) + json_string
        
        # Fix empty or invalid values
        if error_types["invalid_value"]:
            json_string = re.sub(r':\s*,', r': null,', json_string)
            json_string = re.sub(r':\s*$', r': null', json_string)
            json_string = re.sub(r':\s*\}', r': null}', json_string)
        
        return json_string
        
    def _update_prompt_based_on_errors(self, error_types: Dict[str, bool]) -> str:
        """
        Add specific formatting instructions based on observed error patterns.
        
        Args:
            error_types (Dict[str, bool]): Dictionary with error type flags
            
        Returns:
            str: Additional prompt instructions
        """
        additional_instructions = []
        
        if error_types["missing_quotes"]:
            additional_instructions.append("Make sure ALL property names are surrounded by double quotes.")
        
        if error_types["trailing_comma"]:
            additional_instructions.append("Do NOT include trailing commas after the last item in arrays or objects.")
        
        if error_types["unbalanced_braces"]:
            additional_instructions.append("Ensure all opening braces '{' have matching closing braces '}'.")
        
        if error_types["invalid_value"]:
            additional_instructions.append("Every property must have a valid value. Do not leave properties with empty values.")
        
        # Add these instructions to the prompt
        return "\n".join(additional_instructions)
        
    def validate_json_output(self, json_str: str) -> Dict[str, Any]:
        """
        Validate and parse a JSON string, with thorough error handling.
        
        Args:
            json_str (str): The JSON string to validate and parse
            
        Returns:
            Dict[str, Any]: Parsed JSON object or error information
        """
        if not json_str:
            return {"error": "Empty JSON string provided"}
        
        # Clean the JSON string first
        clean_json = self._clean_json_string(json_str)
        
        try:
            # Attempt to parse the JSON
            return json.loads(clean_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            
            # Attempt to repair the JSON
            repaired_json = self._attempt_json_repair(clean_json)
            try:
                return json.loads(repaired_json)
            except json.JSONDecodeError:
                # If repair fails, try regex extraction
                regex_result = self._extract_json_with_regex(json_str)
                if regex_result:
                    return regex_result
                
                # As a last resort, try to extract any JSON if possible
                extracted_json = self._extract_json_from_text(json_str)
                if extracted_json:
                    return extracted_json
            
            # Return detailed error information if all else fails
            error_classification = self._classify_json_error(clean_json)
            return {
                "error": "Invalid JSON format",
                "details": str(e),
                "error_types": error_classification,
                "position": e.pos,
                "line": e.lineno,
                "column": e.colno,
                "received_text": json_str[:100] + "..." if len(json_str) > 100 else json_str
            }
    
    def process_resume_and_jd(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Process a resume and job description pair to get matching results.
        
        Args:
            resume_text (str): The text content of the resume
            jd_text (str): The text content of the job description
            
        Returns:
            Dict[str, Any]: Complete processing results including parsed data and matching
        """
        # Parse the resume
        parsed_resume = self.parse_resume(resume_text)
        
        # Parse the job description
        parsed_jd = self.parse_job_description(jd_text)
        
        # Match the resume to the job description
        match_result = self.match_resume_to_jd(parsed_resume, parsed_jd)
        
        # Return the complete results
        return {
            "parsed_resume": parsed_resume,
            "parsed_job_description": parsed_jd,
            "matching_result": match_result
        }


# Example usage and testing function
def test_with_sample_data(position_index=None):
    """Test the ResumeJDMatcher with sample data
    
    Args:
        position_index (int, optional): Index of the job description to use (0-3).
                                      If None, will test all job descriptions.
    """
    matcher = ResumeJDMatcher()
    
    # Sample job descriptions for testing
    job_descriptions = [
        """
        Lead Product Manager, Monetization at Match Group
        
        About the Role:
        Match Group is seeking a Lead Product Manager to drive monetization strategies across our dating platforms. You will optimize revenue streams, develop pricing models, and work with cross-functional teams to implement innovative monetization features.
        
        Requirements:
        - 5+ years of product management experience with focus on monetization
        - Bachelor's degree in Business, Computer Science, or related field; MBA preferred
        - Strong understanding of subscription models, in-app purchases, and pricing strategies
        - Experience with A/B testing and data-driven decision making
        - Excellent communication and leadership skills
        - Knowledge of dating industry a plus
        """,
        
        """
        AI Solutions Engineer at Moveworks
        
        About the Role:
        Moveworks is looking for an AI Solutions Engineer to help design and implement AI-powered solutions for enterprise IT support. You will work with our AI models, integrate with client systems, and ensure smooth deployment of our conversational AI platform.
        
        Requirements:
        - 3+ years of software engineering experience
        - Bachelor's or Master's degree in Computer Science, AI, or related technical field
        - Strong programming skills in Python and JavaScript
        - Experience with NLP, machine learning, or conversational AI
        - Knowledge of enterprise IT systems and workflows
        - Strong problem-solving and communication skills
        """,
        
        """
        Game Systems Engineer at Epic Games
        
        About the Role:
        Epic Games is seeking a Game Systems Engineer to join our team working on next-generation gaming experiences. You will design and implement core gameplay systems, optimize performance, and collaborate with artists and designers to bring creative visions to life.
        
        Requirements:
        - 4+ years of game development experience
        - Bachelor's degree in Computer Science, Software Engineering, or related field
        - Proficient in C++ and game engine architecture
        - Experience with Unreal Engine preferred
        - Strong 3D math and physics simulation skills
        - Portfolio demonstrating relevant game development work
        - Passion for gaming and creating exceptional player experiences
        """,
        
        """
        Senior Software Engineer, AI/ML at Google
        
        About the Role:
        Google is looking for a Senior Software Engineer specializing in AI/ML to join our team. You will develop scalable ML systems, improve model training pipelines, and implement cutting-edge algorithms to solve complex problems across Google products.
        
        Requirements:
        - 7+ years of software engineering experience
        - 3+ years of experience with machine learning frameworks (TensorFlow, PyTorch)
        - MS or PhD in Computer Science, Machine Learning, or related technical field
        - Strong programming skills in Python and C++
        - Experience deploying ML models to production
        - Published research in ML/AI is a plus
        - Excellent problem-solving and collaboration skills
        """
    ]
    
    # Sample resume for testing
    sample_resume = """
    Education
    Carnegie Mellon University, School of Computer Science, Master of Science in Robotics
    Peking University, Bachelor of Science, Industrial Engineering

    Experience

    Lead a cross-functional team of 10, including AI researchers, engineers, designer, marketers, and HR, building the next generation AI interview products to boost hiring efficiency
    Launched an AI job-hunting platform delivering personalized job opportunities, attracting 2,000+ subscribers
    Operates a mentorship platform for professional skills coaching
    Senior Technical Program Manager at Google, Mountain View, CA
    04/2019–02/2023

    Established the on-device Google Assistant program, integrating AI and edge computing to minimize user friction and latency, launched at the Made by Google event, impacting over 10M home devices
    Led a cross-departmental project as product owner to develop a local Smart Home framework, equivalent to a Home Automation server, delivering a seamless local experience with 3X faster query execution
    Developed the roadmap for an AI-driven ranking engine to personalize content delivery on Smart Displays, boosting user engagement with the screen from 11% to 18%
    Served as the product owner for the Smart Displays portfolio, driving strategies, feature development, and quality
    Technical Product Manager at TuSimple, San Diego, CA
    03/2018–04/2019

    Served as the lead product manager and designed a series of software products which became the foundation supporting autonomous driving system's workflows and a fleet of trucks' operation
    Optimized the data pipeline from data collection to post-processing, reducing the data idle time by over 30%
    Created tags domain system for debrief and triage on the autonomous driving road test issues, which enabled algorithm modules' conditional benchmarks and tag-driven improvement
    Software Engineering Intern at Amazon Robotics, Boston, MA
    05/2017–09/2017

    Invented a technique using infrared camera and computer vision to capture finger touching points when human naturally grasping packages, filing a US patent application of my invention
    Developed a software application which automated the images capturing and 3D point clouds storage process
    Tutored operating team to work on my system, and wrote the code specifics as well as user manual for reference
    Founder & CEO of TP-Helper, Beijing, China
    09/2015–03/2017

    Assembled a cross-functional team of 6 to develop and operate an information exchange platform, enabling college students to find immediate help with everyday tasks
    Defined a user growth plan, reaching 30,000+ users and 6,000+ DAU within the first year, while generating $12,000 monthly revenue through VIP features and partnerships with local businesses
    Product Manager at Tencent Company, Shenzhen, China
    05/2015–09/2015

    Designed the reputation system and reporting feature to enhance user's gaming experience on Tencent Game Platform
    Launched the 4th anniversary program of League of Legends on WeChat platform, visualizing players' gaming records and exciting moments, attracting over 3 million viewing times
    Projects
    Marketing Articles Repurposing Tool for KOLs
    Landing Page Builder using AIGC Tools (GPT, Midjourney)
    GGV Capital Fellowship Program 2020
    Social Interactive Robot's Prototyping for Elderly People
    Product Design for Teaching Aids Simulator Based on Augmented Reality
    Skills & Interests
    Skills: Product Management, Project Management, Cross-Functional Team Leadership, Gen-AI, Data Analysis, Machine Learning, Deep Learning, Python, Matlab, Django, MySQL, R, Axure, JIRA
    Interests: Entrepreneurship, AI/Robotics, Bio-tech, Edu-tech, E-commerce
    """
    
    # Company names for file naming
    company_names = ["MatchGroup", "Moveworks", "EpicGames", "Google"]
    
    # If position_index is specified, test only that one
    if position_index is not None:
        position_index = max(0, min(position_index, len(job_descriptions) - 1))
        indices_to_test = [position_index]
    else:
        # Test all positions
        indices_to_test = range(len(job_descriptions))
    
    results = {}
    
    # Process each job description
    for idx in indices_to_test:
        # Get the job title for display
        job_title = job_descriptions[idx].strip().split('\n')[0].strip()
        print(f"\n{'='*80}\nTesting with position: {job_title}")
        print(f"{'='*80}\n")
        
        # Test with the selected job description
        result = matcher.process_resume_and_jd(sample_resume, job_descriptions[idx])
        results[idx] = result
        
        # Print the matching result
        if "matching_result" in result and "error" not in result["matching_result"]:
            print("\nMATCHING RESULT JSON:")
            print(f"{'='*80}")
            matching_json = result["matching_result"]
            print(json.dumps(matching_json, indent=2))
            print(f"{'='*80}\n")
            
            # Save the JSON to a file for easy access
            filename = f"matching_result_{company_names[idx]}.json"
            with open(filename, "w") as f:
                json.dump(matching_json, f, indent=2)
            print(f"The JSON result has been saved to '{filename}'")
        else:
            print("Error in matching:", result.get("matching_result", {}).get("error", "Unknown error"))
    
    return results


if __name__ == "__main__":
    # This will run a test for all job descriptions
    test_with_sample_data(None) 