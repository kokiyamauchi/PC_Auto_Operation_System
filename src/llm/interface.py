import requests
import json
import base64
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

class BaseLLMInterface(ABC):
    @abstractmethod
    def run(self, prompt: str, image_path: str = None) -> List[str]:
        pass

class OpenAIInterface(BaseLLMInterface):
    def __init__(self, api_key: str):
        self.api_endpoint = "https://api.openai.com/v1/chat/completions"
        self.vision_endpoint = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
    def run(self, prompt: str, image_path: str = None) -> List[str]:
        try:
            if image_path:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                payload = {
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", 
                                 "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    "max_tokens": 1024
                }
                current_endpoint = self.vision_endpoint
            else:
                payload = {
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                current_endpoint = self.api_endpoint
                
            response = requests.post(
                current_endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            return json.loads(content)
        except Exception as e:
            print(f"Error in OpenAI request: {str(e)}")
            return []

class ClaudeInterface(BaseLLMInterface):
    def __init__(self, api_key: str):
        self.api_endpoint = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

    def run(self, prompt: str, image_path: str = None) -> List[str]:
        try:
            messages = [{"role": "user", "content": prompt}]
            if image_path:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image", "source": {"type": "base64", 
                                               "media_type": "image/jpeg",
                                               "data": base64_image}}
                ]
            
            payload = {
                "model": "claude-3-opus-20240229",
                "messages": messages,
                "max_tokens": 1024
            }
            
            response = requests.post(
                self.api_endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            content = response_data['content'][0]['text']
            return json.loads(content)
        except Exception as e:
            print(f"Error in Claude request: {str(e)}")
            return []

class GeminiInterface(BaseLLMInterface):
    def __init__(self, api_key: str):
        self.api_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.vision_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
        self.api_key = api_key
        
    def run(self, prompt: str, image_path: str = None) -> List[str]:
        try:
            if image_path:
                with open(image_path, "rb") as image_file:
                    image_bytes = image_file.read()
                
                payload = {
                    "contents": [{
                        "parts":[
                            {"text": prompt},
                            {"inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64.b64encode(image_bytes).decode('utf-8')
                            }}
                        ]
                    }]
                }
                current_endpoint = self.vision_endpoint
            else:
                payload = {
                    "contents": [{"parts":[{"text": prompt}]}]
                }
                current_endpoint = self.api_endpoint
                
            response = requests.post(
                f"{current_endpoint}?key={self.api_key}",
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            content = response_data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content)
        except Exception as e:
            print(f"Error in Gemini request: {str(e)}")
            return []

class LLMInterface:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider.lower()
        self.interfaces = {
            "openai": OpenAIInterface,
            "claude": ClaudeInterface,
            "gemini": GeminiInterface
        }
        if self.provider not in self.interfaces:
            raise ValueError(f"Unsupported provider: {provider}")
        self.interface = self.interfaces[self.provider](api_key)
        
    def run(self, prompt: str, image_path: str = None) -> List[str]:
        return self.interface.run(prompt, image_path)