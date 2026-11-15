# core/llm_client.py

import logging
from typing import List
from ollama import Client

logger = logging.getLogger(__name__)

class LLMClient:
    """
    A wrapper around the Ollama client to handle model listing and JSON extraction.
    """
    
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host
        self.client = Client(host=self.host, trust_env=False)

    def is_available(self) -> bool:
        """Checks if the Ollama server is running and accessible."""
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama is not available: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """
        Returns a list of locally installed model names.
        Handles both dict responses (old library) and Pydantic objects (new library).
        """
        try:
            response = self.client.list()
            models_list = []
            
            # 1. Получаем список моделей (dict или объект)
            if isinstance(response, dict):
                raw_models = response.get('models', [])
            else:
                raw_models = getattr(response, 'models', [])
                
            # 2. Извлекаем имена
            for model in raw_models:
                if isinstance(model, dict):
                    name = model.get('name') or model.get('model')
                else:
                    name = getattr(model, 'name', None) or getattr(model, 'model', None)
                
                if name:
                    models_list.append(name)
                    
            return models_list
        except Exception as e:
            logger.error(f"Failed to fetch models: {e}")
            return []

    def generate_json(self, prompt: str, system_prompt: str, model_name: str) -> str:
        """
        Sends a prompt to the LLM and forces it to return JSON format.
        """
        logger.info(f"Sending request to model: {model_name}")
        try:
            response = self.client.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                format="json", 
                options={"temperature": 0.1}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise RuntimeError(f"LLM generation failed: {e}")