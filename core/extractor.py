# core/extractor.py

import json
import logging
from typing import Dict, Any
from json_repair import repair_json
from core.llm_client import LLMClient

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """
    Handles the logic of formatting the prompt, calling the LLM,
    and safely parsing the JSON response.
    """
    
    def __init__(self):
        self.llm = LLMClient()
        
        # The system prompt is crucial. It sets the persona and strict rules.
        self.system_prompt = (
            "You are an expert data extraction assistant. "
            "Your task is to extract specific fields from the provided document text. "
            "You MUST respond with ONLY a valid JSON object. "
            "Do NOT include any explanations, markdown formatting (like ```json), or extra text. "
            "If a field cannot be found in the text, use null (without quotes)."
        )

    def extract_data(self, text: str, custom_prompt: str, model_name: str) -> Dict[str, Any]:
        """
        Extracts structured data from raw text using the specified LLM.
        
        :param text: The raw text extracted from the PDF/DOCX.
        :param custom_prompt: The user's instructions (e.g., "Extract invoice number and total amount").
        :param model_name: The Ollama model to use (e.g., 'llama3.1').
        :return: A dictionary containing the extracted data.
        """
        # We truncate text to ~30,000 chars to avoid overwhelming small local models 
        # and blowing up the context window. Real-world PDFs can be huge.
        safe_text = text[:30000] if len(text) > 30000 else text
        
        user_message = (
            f"DOCUMENT TEXT:\n{safe_text}\n\n"
            f"EXTRACTION TASK:\n{custom_prompt}\n\n"
            f"Return ONLY the JSON object."
        )

        # Get raw response from LLM
        raw_response = self.llm.generate_json(
            prompt=user_message,
            system_prompt=self.system_prompt,
            model_name=model_name
        )
        
        logger.debug(f"Raw LLM response: {raw_response}")

        # Parse JSON safely
        return self._parse_json_safely(raw_response)

    def _parse_json_safely(self, raw_text: str) -> Dict[str, Any]:
        """
        Attempts to parse JSON. If the LLM hallucinated markdown or broke the JSON,
        we use json_repair to fix it.
        """
        # 1. Try standard parsing
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            logger.warning("Standard JSON parsing failed. Attempting repair...")

        # 2. Try json_repair (This library is a lifesaver for local LLMs)
        try:
            repaired_obj = repair_json(raw_text, return_objects=True)
            if isinstance(repaired_obj, dict):
                logger.info("JSON successfully repaired.")
                return repaired_obj
        except Exception as e:
            logger.error(f"json_repair failed: {e}")

        # 3. If all else fails, raise an error
        raise ValueError(f"Could not parse JSON from LLM output. Raw output was: {raw_text[:100]}...")


# ==========================================
# TEST BLOCK (Run this file directly to test)
# ==========================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("--- Testing Core Engine ---")
    
    extractor = DocumentExtractor()
    
    # 1. Check Ollama
    if not extractor.llm.is_available():
        print("ERROR: Ollama is not running. Please start Ollama.")
        exit(1)
        
    models = extractor.llm.get_available_models()
    print(f"Available models: {models}")
    
    if not models:
        print("ERROR: No models found. Please run 'ollama pull llama3.1'")
        exit(1)
        
    # 2. Test Data
    sample_text = """
    INVOICE #INV-2023-001
    Date: October 25, 2023
    From: Acme Corp, 123 Main St.
    To: Globex Inc.
    Total Amount: $5,450.00
    Tax: $450.00
    """
    
    prompt = "Extract the invoice number, date, sender, receiver, and total amount."
    
    # We'll use the first available model for the test
    test_model = models[0] 
    print(f"\nTesting extraction with model: {test_model}")
    
    try:
        result = extractor.extract_data(sample_text, prompt, test_model)
        print("\n✅ Extraction Successful!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n❌ Error: {e}")