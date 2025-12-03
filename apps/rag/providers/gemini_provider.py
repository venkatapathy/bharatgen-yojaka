"""
Gemini LLM provider using Google's Generative AI.
"""
import google.generativeai as genai
import time
import json
import mimetypes
from typing import Dict, Any, Optional
from ..interfaces import BaseLLM
from django.conf import settings

class GeminiProvider(BaseLLM):
    """Gemini language model provider."""
    
    def __init__(self, model: str = "gemini-2.0-flash", api_key: Optional[str] = None):
        """
        Initialize Gemini provider.
        
        Args:
            model: Gemini model name (default: gemini-2.0-flash)
            api_key: Google API key (defaults to settings.GEMINI_API_KEY)
        """
        self.model_name = model
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided and not found in settings (GEMINI_API_KEY)")
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Gemini."""
        try:
            start_time = time.time()
            
            # Combine system prompt and user prompt if system prompt is provided
            # Gemini supports system instructions in recent versions, but keeping it simple for now
            # or we can use the system_instruction argument if using the latest SDK
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # Handle system prompt by prepending or using system_instruction if supported
            # For flash models, we can often pass it in the model init, but here we init once.
            # We'll prepend it to the prompt for simplicity and compatibility
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                **kwargs
            )
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "text": response.text,
                "model": self.model_name,
                "tokens_used": 0, # Gemini doesn't always return token counts easily in simple response
                "generation_time_ms": generation_time_ms,
                "finish_reason": "stop",
            }
            
        except Exception as e:
            return {
                "text": f"Error generating response: {str(e)}",
                "model": self.model_name,
                "tokens_used": 0,
                "generation_time_ms": 0,
                "finish_reason": "error",
                "error": str(e)
            }
    
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Stream text generation using Gemini."""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                stream=True,
                generation_config=generation_config,
                **kwargs
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {str(e)}"

    def evaluate_speaking_audio(self, audio_file_path: str, reference_text: str) -> Dict[str, Any]:
        """
        Evaluate speaking audio against reference text using Gemini.
        
        Args:
            audio_file_path: Path to the local audio file
            reference_text: The text the user was trying to speak
            
        Returns:
            Dict containing grade (0-100) and feedback text
        """
        try:
            # Determine mime type
            mime_type, _ = mimetypes.guess_type(audio_file_path)
            if not mime_type:
                mime_type = "audio/wav"  # Fallback
                
            # Upload file to Gemini
            # Note: large files might need more robust handling, but for short clips this is fine
            uploaded_file = genai.upload_file(path=audio_file_path, mime_type=mime_type)
            
            # Construct prompt
            prompt = (
                "You are an experienced language teacher. A student's audio is provided as a file attached to this request.\n"
                f"Target text: \"{reference_text}\".\n\n"
                "Please listen to the audio and evaluate the student's spoken response with two outputs in JSON exactly like:\n"
                '{"grade": <number 0-100>, "feedback": "<brief feedback (1-2 paragraphs)>"}\n\n'
                "Grading criteria (approx):\n"
                " - Pronunciation accuracy: 40%\n"
                " - Fluency and organization: 20%\n"
                " - Accuracy against target text: 40%\n\n"
                "Keep the JSON compact and valid. Only output the JSON.\n"
            )
            
            # Generate content
            # We pass the prompt string and the file object
            response = self.model.generate_content(
                [prompt, uploaded_file],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=500
                )
            )
            
            text_response = response.text
            
            # Clean up JSON if needed (sometimes models add markdown code blocks)
            clean_json = text_response.replace('```json', '').replace('```', '').strip()
            
            try:
                result = json.loads(clean_json)
                return {
                    "grade": result.get("grade", 0),
                    "feedback": result.get("feedback", "No feedback provided."),
                    "raw_response": text_response
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "grade": 0,
                    "feedback": text_response,
                    "raw_response": text_response
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "grade": 0,
                "feedback": f"Error evaluating audio: {str(e)}"
            }
