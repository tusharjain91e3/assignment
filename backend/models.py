from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for subcategories
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self, include_children=False, include_products=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
        
        if include_children:
            data['children'] = [child.to_dict() for child in self.children if child.is_active]
        
        if include_products:
            data['products'] = [product.to_dict() for product in self.products if product.is_active]
            
        return data

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2))
    sku = db.Column(db.String(100), unique=True, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    image_urls = db.Column(db.Text)  # JSON string of image URLs
    tags = db.Column(db.Text)  # JSON string of tags
    specifications = db.Column(db.Text)  # JSON string of specifications
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_category=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'discount_price': float(self.discount_price) if self.discount_price else None,
            'sku': self.sku,
            'stock_quantity': self.stock_quantity,
            'category_id': self.category_id,
            'brand': self.brand,
            'rating': self.rating,
            'review_count': self.review_count,
            'image_urls': json.loads(self.image_urls) if self.image_urls else [],
            'tags': json.loads(self.tags) if self.tags else [],
            'specifications': json.loads(self.specifications) if self.specifications else {},
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'in_stock': self.stock_quantity > 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_category and self.category:
            data['category'] = self.category.to_dict()
            
        return data

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(100))  # search, product_info, recommendation, etc.
    context_data = db.Column(db.Text)  # JSON string for additional context
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'intent': self.intent,
            'context_data': json.loads(self.context_data) if self.context_data else {},
            'timestamp': self.timestamp.isoformat()
        }

class SearchLog(db.Model):
    __tablename__ = 'search_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(255), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    session_id = db.Column(db.String(36))
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
