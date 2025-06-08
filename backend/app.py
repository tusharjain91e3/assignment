from urllib.parse import quote_plus
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, Product, Category, ChatSession, init_database
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import uuid
from datetime import datetime, timedelta
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate required environment variables
required_env_vars = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE', 'OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# MySQL Database Configuration
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = quote_plus(os.getenv('MYSQL_PASSWORD'))  # encode special chars like '@'
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

# Construct database URI
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize database with app
db.init_app(app)

# Initialize OpenAI client with better error handling
client = None
try:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Initialize OpenAI client with minimal configuration
    client = OpenAI(api_key=api_key)
    
    # Test the API key with a simple request
    try:
        models = client.models.list()
        logger.info("OpenAI client initialized successfully")
    except Exception as test_error:
        logger.warning(f"OpenAI API test failed: {test_error}")
        # Continue anyway - the client might still work for chat completions
        
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    # Set client to None and handle gracefully in the chatbot
    client = None

class EcommerceChatbot:
    def __init__(self):
        self.system_prompt = """
        You are an intelligent ecommerce chatbot assistant. Your role is to help customers find products, answer questions about inventory, and provide excellent customer service.
        
        You have access to a product database with the following categories:
        - Electronics (smartphones, laptops, headphones, etc.)
        - Clothing (jeans, shoes, hoodies, etc.)
        - Books (fiction, programming guides, etc.)
        - Home & Garden (furniture, LED bulbs, decor, etc.)
        - Sports (tennis rackets, basketballs, equipment, etc.)
        
        Your responses should be:
        1. Helpful and friendly
        2. Focused on understanding customer needs
        3. Specific about product recommendations
        4. Include relevant product details when available
        
        When customers ask about products:
        - Ask clarifying questions if needed
        - Suggest alternatives if exact matches aren't available
        - Mention price ranges when relevant
        - Be enthusiastic about helping them find what they need
        
        Always respond in a conversational, helpful tone.
        """
    
    def get_products_context(self, search_query=None, category=None, price_range=None):
        """Get relevant products from database for context"""
        try:
            query = Product.query.filter(Product.is_active == True)
            
            # Apply search filters
            if search_query:
                search_terms = search_query.lower().split()
                for term in search_terms:
                    query = query.filter(
                        db.or_(
                            Product.name.ilike(f"%{term}%"),
                            Product.description.ilike(f"%{term}%")
                        )
                    )
            
            if category:
                query = query.join(Category).filter(Category.name.ilike(f"%{category}%"))
            
            if price_range:
                min_price, max_price = price_range
                if min_price is not None:
                    query = query.filter(Product.price >= min_price)
                if max_price is not None:
                    query = query.filter(Product.price <= max_price)
            
            products = query.limit(10).all()
            return [product.to_dict() for product in products]
        except Exception as e:
            logger.error(f"Error getting products context: {e}")
            return []
    
    def extract_intent_and_filters(self, message):
        """Extract search intent and filters from user message"""
        message_lower = message.lower()
        
        # Extract price range
        price_pattern = r'\$?(\d+(?:\.\d{2})?)'
        prices = re.findall(price_pattern, message_lower)
        price_range = None
        
        if len(prices) >= 2:
            price_range = (float(prices[0]), float(prices[1]))
        elif len(prices) == 1:
            if any(word in message_lower for word in ['under', 'below', 'less than']):
                price_range = (0, float(prices[0]))
            elif any(word in message_lower for word in ['over', 'above', 'more than']):
                price_range = (float(prices[0]), 999999)
        
        # Extract category intent
        category_keywords = {
            'electronics': ['phone', 'smartphone', 'laptop', 'computer', 'headphone', 'tablet', 'electronics'],
            'clothing': ['clothes', 'jeans', 'shoes', 'shirt', 'hoodie', 'dress', 'clothing', 'fashion'],
            'books': ['book', 'novel', 'guide', 'manual', 'reading'],
            'home & garden': ['furniture', 'table', 'chair', 'bulb', 'light', 'home', 'garden'],
            'sports': ['sports', 'tennis', 'basketball', 'racket', 'ball', 'athletic', 'fitness']
        }
        
        detected_category = None
        for category, keywords in category_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_category = category
                break
        
        return {
            'search_query': message,
            'category': detected_category,
            'price_range': price_range
        }
    
    def get_fallback_response(self, message, relevant_products):
        """Generate a fallback response when OpenAI is not available"""
        message_lower = message.lower()
        
        # Simple greeting responses
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! Welcome to our store. How can I help you find the perfect product today?"
        
        # Product search responses
        if relevant_products:
            response = "I found some products that might interest you:\n\n"
            for i, product in enumerate(relevant_products[:3], 1):
                response += f"{i}. **{product['name']}** - ${product['price']}\n"
                response += f"   {product['description'][:100]}...\n\n"
            response += "Would you like more details about any of these products?"
            return response
        
        # Category-based responses
        if any(keyword in message_lower for keyword in ['electronics', 'phone', 'laptop', 'computer']):
            return "We have a great selection of electronics including smartphones, laptops, headphones, and more. What specific type of electronic device are you looking for?"
        
        if any(keyword in message_lower for keyword in ['clothing', 'clothes', 'fashion', 'wear']):
            return "Our clothing section has everything from casual wear to formal attire. Are you looking for something specific like jeans, shoes, or hoodies?"
        
        if any(keyword in message_lower for keyword in ['book', 'reading', 'novel']):
            return "We have a wonderful collection of books including fiction, non-fiction, and technical guides. What genre interests you?"
        
        # Default response
        return "I'd be happy to help you find what you're looking for! We have products in Electronics, Clothing, Books, Home & Garden, and Sports. What are you interested in?"
    
    def process_message(self, message, session_id=None):
        """Process user message using OpenAI GPT or fallback"""
        try:
            # Extract filters and get relevant products
            filters = self.extract_intent_and_filters(message)
            relevant_products = self.get_products_context(
                search_query=filters['search_query'],
                category=filters['category'],
                price_range=filters['price_range']
            )
            
            # Try OpenAI if available
            if client:
                try:
                    # Prepare context for OpenAI
                    products_context = ""
                    if relevant_products:
                        products_context = "Here are some relevant products from our inventory:\n"
                        for product in relevant_products[:5]:  # Limit to top 5 products
                            products_context += f"- {product['name']}: ${product['price']} - {product['description'][:100]}...\n"
                    else:
                        products_context = "No specific products found matching the query, but we have Electronics, Clothing, Books, Home & Garden, and Sports categories available."
                    
                    # Create OpenAI prompt
                    user_prompt = f"""
                    Customer message: "{message}"
                    
                    Available products context:
                    {products_context}
                    
                    Please respond as a helpful ecommerce chatbot. If relevant products are available, mention them specifically. If not, suggest alternatives or ask clarifying questions to help the customer find what they need.
                    """
                    
                    # Call OpenAI API
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=300,
                        temperature=0.7
                    )
                    
                    bot_response = response.choices[0].message.content.strip()
                    
                    return {
                        "reply": bot_response,
                        "products": relevant_products,
                        "intent": "ai_processed",
                        "filters_applied": filters
                    }
                    
                except Exception as openai_error:
                    logger.error(f"OpenAI API Error: {openai_error}")
                    # Fall through to fallback response
            
            # Use fallback response
            fallback_response = self.get_fallback_response(message, relevant_products)
            
            return {
                "reply": fallback_response,
                "products": relevant_products,
                "intent": "fallback_processed",
                "filters_applied": filters
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "reply": "I'm having trouble processing your request right now. Could you please try again or contact our support team?",
                "products": [],
                "intent": "error"
            }

# Initialize chatbot
chatbot = EcommerceChatbot()

# Routes
@app.route('/')
def home():
    return jsonify({
        "message": "Ecommerce Chatbot Backend is running!",
        "version": "2.0",
        "ai_powered": client is not None,
        "endpoints": {
            "chat": "/api/chat",
            "products": "/api/products",
            "categories": "/api/categories",
            "search": "/api/search"
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
            
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Validate session_id format
        try:
            uuid.UUID(session_id)
        except ValueError:
            return jsonify({"error": "Invalid session ID format"}), 400
        
        # Process message with chatbot
        try:
            response = chatbot.process_message(user_message, session_id)
        except Exception as e:
            app.logger.error(f"Error processing message: {str(e)}")
            return jsonify({
                "error": "Failed to process message",
                "details": str(e) if app.debug else "Internal server error"
            }), 500
        
        # Save chat session to database
        try:
            chat_session = ChatSession(
                session_id=session_id,
                user_message=user_message,
                bot_response=response['reply']
            )
            db.session.add(chat_session)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Failed to save chat session: {str(e)}")
            db.session.rollback()
            # Continue with the response even if saving fails
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e) if app.debug else "An unexpected error occurred"
        }), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category_id = request.args.get('category_id', type=int)
        
        query = Product.query.filter(Product.is_active == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "products": [product.to_dict() for product in products.items],
            "total": products.total,
            "page": page,
            "per_page": per_page,
            "pages": products.pages
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_products():
    try:
        query_param = request.args.get('q', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        category_id = request.args.get('category_id', type=int)
        
        query = Product.query.filter(Product.is_active == True)
        
        if query_param:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f"%{query_param}%"),
                    Product.description.ilike(f"%{query_param}%")
                )
            )
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
            
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
            
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        products = query.limit(20).all()
        
        return jsonify([product.to_dict() for product in products])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    try:
        chats = ChatSession.query.filter_by(session_id=session_id).order_by(ChatSession.created_at).all()
        return jsonify([chat.to_dict() for chat in chats])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "openai": "configured" if client else "not configured"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Initialize database with sample data
    with app.app_context():
        init_database(app)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)