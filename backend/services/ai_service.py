import openai
import json
from config import Config

class AIService:
    def __init__(self):
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
    
    def generate_response(self, user_message, context=None):
        """Generate AI response for user message"""
        try:
            if not Config.OPENAI_API_KEY:
                return self._fallback_response(user_message, context)
            
            system_prompt = self._get_system_prompt()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if context:
                context_msg = f"Context: {json.dumps(context)}"
                messages.insert(-1, {"role": "assistant", "content": context_msg})
            
            response = openai.ChatCompletion.create(
                model=Config.AI_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI Service Error: {e}")
            return self._fallback_response(user_message, context)
    
    def _get_system_prompt(self):
        return """You are a helpful ecommerce assistant. You help customers:
        - Search for products
        - Get product information
        - Make recommendations
        - Answer questions about orders, shipping, returns
        - Provide general shopping assistance
        
        Be friendly, helpful, and concise. If you need more information, ask clarifying questions."""
    
    def _fallback_response(self, user_message, context=None):
        """Fallback response when AI service is unavailable"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['search', 'find', 'looking for']):
            return "I'd be happy to help you search for products! What are you looking for?"
        elif any(word in message_lower for word in ['price', 'cost', 'expensive']):
            return "I can help you find products within your budget. What's your price range?"
        elif any(word in message_lower for word in ['recommend', 'suggest', 'best']):
            return "I'd love to recommend some products! What category are you interested in?"
        else:
            return "Thank you for your message! How can I help you with your shopping today?"
    
    def extract_intent(self, user_message):
        """Extract intent from user message"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['search', 'find', 'looking for', 'show me']):
            return 'search'
        elif any(word in message_lower for word in ['recommend', 'suggest', 'best', 'popular']):
            return 'recommendation'
        elif any(word in message_lower for word in ['price', 'cost', 'cheap', 'expensive', 'budget']):
            return 'price_inquiry'
        elif any(word in message_lower for word in ['available', 'stock', 'in stock']):
            return 'availability'
        else:
            return 'general'