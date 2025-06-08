from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index
from flask_migrate import Migrate

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

# Category Model
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    products = db.relationship('Product', backref='category', lazy=True)
    
    # Add unique constraint on name
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_category_name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Product Model
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('idx_product_category_active', 'category_id', 'is_active'),
        Index('idx_product_price', 'price'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'stock_quantity': self.stock_quantity,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Chat Session Model
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Add index for session_id and created_at
    __table_args__ = (
        Index('idx_chat_session_created', 'session_id', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_database(app):
    """Initialize database with sample data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if categories already exist
            if Category.query.count() > 0:
                app.logger.info("Database already initialized with sample data")
                return
            
            # Insert sample categories
            categories_data = [
                ("Electronics", "Smartphones, laptops, tablets, and more"),
                ("Clothing", "Fashion and apparel for all ages"),
                ("Books", "Fiction, non-fiction, textbooks, and magazines"),
                ("Home & Garden", "Furniture, decor, and gardening supplies"),
                ("Sports", "Athletic equipment and sportswear")
            ]
            
            categories = []
            for name, description in categories_data:
                try:
                    category = Category(name=name, description=description)
                    categories.append(category)
                    db.session.add(category)
                except Exception as e:
                    app.logger.error(f"Error adding category {name}: {str(e)}")
                    continue
            
            # Commit categories first
            try:
                db.session.commit()
            except Exception as e:
                app.logger.error(f"Error committing categories: {str(e)}")
                db.session.rollback()
                return
            
            # Insert sample products
            products_data = [
                ("iPhone 15 Pro", "Latest Apple smartphone with advanced camera system", 999.99, 50, 1, "https://example.com/iphone15.jpg"),
                ("Samsung Galaxy S24", "Android flagship with AI features", 899.99, 30, 1, None),
                ("MacBook Air M3", "Lightweight laptop with Apple Silicon", 1299.99, 20, 1, None),
                ("Sony WH-1000XM5", "Noise-canceling wireless headphones", 399.99, 40, 1, None),
                
                ("Levi's 501 Jeans", "Classic straight-leg denim jeans", 89.99, 100, 2, None),
                ("Nike Air Max 90", "Iconic running shoes with air cushioning", 129.99, 75, 2, None),
                ("Adidas Hoodie", "Comfortable cotton blend hoodie", 59.99, 60, 2, None),
                
                ("The Great Gatsby", "Classic American novel by F. Scott Fitzgerald", 12.99, 200, 3, None),
                ("Python Programming Guide", "Comprehensive guide to Python development", 49.99, 80, 3, None),
                
                ("IKEA Coffee Table", "Modern minimalist coffee table", 199.99, 25, 4, None),
                ("Philips LED Bulbs", "Energy-efficient smart LED bulbs pack of 4", 39.99, 150, 4, None),
                
                ("Wilson Tennis Racket", "Professional grade tennis racket", 159.99, 35, 5, None),
                ("Nike Basketball", "Official size basketball", 29.99, 90, 5, None),
            ]
            
            for name, description, price, stock, category_id, image_url in products_data:
                try:
                    product = Product(
                        name=name,
                        description=description,
                        price=price,
                        stock_quantity=stock,
                        category_id=category_id,
                        image_url=image_url,
                        is_active=True
                    )
                    db.session.add(product)
                except Exception as e:
                    app.logger.error(f"Error adding product {name}: {str(e)}")
                    continue
            
            # Commit all changes
            try:
                db.session.commit()
                app.logger.info("Database initialized successfully with sample data!")
            except Exception as e:
                app.logger.error(f"Error committing products: {str(e)}")
                db.session.rollback()
                
        except Exception as e:
            app.logger.error(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

# Helper functions for backward compatibility
def fetch_all_categories():
    """Fetch all categories as dictionaries"""
    try:
        categories = Category.query.all()
        return [category.to_dict() for category in categories]
    except Exception as e:
        app.logger.error(f"Error fetching categories: {str(e)}")
        return []

def fetch_products_by_category(category_id):
    """Fetch products by category as dictionaries"""
    try:
        products = Product.query.filter_by(category_id=category_id, is_active=True).all()
        return [product.to_dict() for product in products]
    except Exception as e:
        app.logger.error(f"Error fetching products for category {category_id}: {str(e)}")
        return []

def save_chat_session(session_id, user_message, bot_response):
    """Save chat session to database"""
    try:
        chat_session = ChatSession(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response
        )
        db.session.add(chat_session)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving chat session: {str(e)}")
        return False