"""
Service for generating dynamic quizzes and providing feedback using RAG.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from apps.rag.pipeline import get_rag_pipeline
from apps.learning.models import Content, Module

logger = logging.getLogger(__name__)

class QuizGenerator:
    """Generates quizzes and provides feedback using RAG pipeline."""
    
    def __init__(self):
        self.rag = get_rag_pipeline()
    
    def generate_quiz(self, content_id: int, num_questions: int = 5, difficulty: str = 'intermediate') -> Dict[str, Any]:
        """
        Generate a quiz based on specific content.
        
        Args:
            content_id: ID of the content to base the quiz on
            num_questions: Number of questions to generate
            difficulty: Difficulty level of the quiz
            
        Returns:
            Dictionary containing list of questions
        """
        try:
            content = Content.objects.get(id=content_id)
            
            # Construct context from content
            context_text = ""
            if content.text_content:
                context_text += content.text_content + "\n\n"
            if content.slides_content:
                 # Extract text from slides if available
                slides = content.slides_content.get('slides', [])
                for slide in slides:
                    context_text += f"{slide.get('title', '')}: {slide.get('content', '')}\n"
            
            # Fallback to RAG retrieval if content text is minimal or for enrichment
            if len(context_text) < 100:
                rag_results = self.rag.retrieve(
                    query=f"concepts in {content.title}",
                    top_k=3,
                    filter_dict={"content_id": content_id}
                )
                for doc in rag_results:
                    context_text += doc['text'] + "\n"

            prompt = f"""
            Generate a {difficulty} level quiz with {num_questions} multiple-choice questions based on the following text.
            
            Text content:
            {context_text[:3000]}  # Limit context length
            
            Return the response ONLY as a valid JSON object with this structure:
            {{
                "questions": [
                    {{
                        "id": 1,
                        "question": "Question text here",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": "Why this is correct"
                    }}
                ]
            }}
            """
            
            response = self.rag.llm.generate(
                prompt=prompt,
                system_prompt="You are an educational AI that creates accurate and relevant quizzes. Output ONLY JSON.",
                temperature=0.3, # Lower temperature for more consistent formatting
                max_tokens=2000
            )
            
            # Parse JSON response
            try:
                # Clean up potential markdown code blocks
                response_text = response['content'].strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                    
                quiz_data = json.loads(response_text)
                return quiz_data
            except json.JSONDecodeError:
                logger.error(f"Failed to decode quiz JSON: {response['content']}")
                return {"error": "Failed to generate valid quiz format", "raw_response": response['content']}
                
        except Content.DoesNotExist:
            return {"error": "Content not found"}
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            return {"error": str(e)}

    def evaluate_answer(self, question: str, user_answer: str, correct_answer: str, context: str = "") -> Dict[str, Any]:
        """
        Evaluate a user's answer and provide immersive feedback.
        
        Args:
            question: The question text
            user_answer: The answer provided by the user
            correct_answer: The correct answer
            context: Optional context to help with explanation
            
        Returns:
            Feedback dictionary
        """
        prompt = f"""
        The user answered a quiz question. Provide immersive, educational feedback.
        
        Question: {question}
        User Answer: {user_answer}
        Correct Answer: {correct_answer}
        Context: {context}
        
        If the answer is correct, congratulate them and reinforce the concept.
        If incorrect, explain why it's wrong and guide them to the correct understanding without being discouraging.
        """
        
        response = self.rag.llm.generate(
            prompt=prompt,
            system_prompt="You are a supportive and knowledgeable tutor.",
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "is_correct": user_answer.strip().lower() == correct_answer.strip().lower(), # Simple check, could be smarter
            "feedback": response['content']
        }

