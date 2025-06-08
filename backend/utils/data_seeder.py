from models import db, Category, Product
import json

class DataSeeder:
    @staticmethod
    def seed_categories():
        """Seed comprehensive category data"""
        categories_data = [
            {
                "name": "Electronics",
                "description": "Electronic devices and accessories",
                "children": [
                    {"name": "Smartphones", "description": "Mobile phones and accessories"},
                    {"name": "Laptops", "description": "Laptop computers and accessories"},
                    {"name": "Tablets", "description": "Tablet computers"},
                    {"name": "Audio", "description": "Headphones, speakers, and audio equipment"},
                    {"name": "Gaming", "description": "Gaming consoles and accessories"}
                ]
            },
            {
                "name": "Clothing",
                "description": "Fashion and apparel",
                "children": [
                    {"name": "Men's Clothing", "description": "Clothing for men"},
                    {"name": "Women's Clothing", "description": "Clothing for women"},
                    {"name": "Kids' Clothing", "description": "Clothing for children"},
                    {"name": "Shoes", "description": "Footwear for all ages"},
                    {"name": "Accessories", "description": "Fashion accessories"}
                ]
            },
            {
                "name": "Home & Garden",
                "description": "Home improvement and gardening supplies",
                "children": [
                    {"name": "Furniture", "description": "Home furniture"},
                    {"name": "Kitchen", "description": "Kitchen appliances and tools"},
                    {"name": "Garden", "description": "Gardening tools and supplies"},
                    {"name": "Decor", "description": "Home decoration items"}
                ]
            },
            {
                "name": "Books",
                "description": "Books and educational materials",
                "children": [
                    {"name": "Fiction", "description": "Fiction books"},
                    {"name": "Non-Fiction", "description": "Non-fiction books"},
                    {"name": "Educational", "description": "Educational and academic books"},
                    {"name": "Children's Books", "description": "Books for children"}
                ]
            }
        ]
        
        for cat_data in categories_data:
            # Create parent category
            parent_cat = Category(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.session.add(parent_cat)
            db.session.flush()  # Get the ID
            
            # Create child categories
            for child_data in cat_data.get("children", []):
                child_cat = Category(
                    name=child_data["name"],
                    description=child_data["description"],
                    parent_id=parent_cat.id
                )
                db.session.add(child_cat)
        
        db.session.commit()
    
    @staticmethod
    def seed_products():
        """Seed comprehensive product data"""
        # This would contain hundreds of products
        # For brevity, showing structure
        products_data = [
            {
                "name": "Premium Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 299.99,
                "discount_price": 249.99,
                "sku": "PWH001",
                "stock_quantity": 100,
                "category": "Audio",
                "brand": "AudioTech",
                "rating": 4.5,
                "review_count": 245,
                "tags": ["wireless", "headphones", "noise-cancellation", "premium"],
                "specifications": {
                    "battery_life": "30 hours",
                    "connectivity": "Bluetooth 5.0",
                    "noise_cancellation": "Active"
                }
            }
            # Add more products...
        ]
        
        for prod_data in products_data:
            # Find category
            category = Category.query.filter_by(name=prod_data["category"]).first()
            if not category:
                continue
            
            product = Product(
                name=prod_data["name"],
                description=prod_data["description"],
                price=prod_data["price"],
                discount_price=prod_data.get("discount_price"),
                sku=prod_data["sku"],
                stock_quantity=prod_data["stock_quantity"],
                category_id=category.id,
                brand=prod_data["brand"],
                rating=prod_data["rating"],
                review_count=prod_data["review_count"],
                tags=json.dumps(prod_data["tags"]),
                specifications=json.dumps(prod_data["specifications"]),
                is_featured=prod_data.get("is_featured", False)
            )
            db.session.add(product)
        
        db.session.commit()

# ===================================

# CLI Commands (manage.py)
import click
from flask.cli import with_appcontext
from utils.data_seeder import DataSeeder

@click.command()
@with_appcontext
def seed_data():
    """Seed the database with sample data"""
    try:
        DataSeeder.seed_categories()
        DataSeeder.seed_products()
        click.echo("Database seeded successfully!")
    except Exception as e:
        click.echo(f"Error seeding database: {e}")

@click.command()
@with_appcontext
def reset_db():
    """Reset the database"""
    try:
        db.drop_all()
        db.create_all()
        click.echo("Database reset successfully!")
    except Exception as e:
        click.echo(f"Error resetting database: {e}")

# Register commands
def register_commands(app):
    app.cli.add_command(seed_data)
    app.cli.add_command(reset_db)

if __name__ == '__main__':
    from datetime import datetime
    app = create_app()
    register_commands(app)
    app.run(debug=True, host='0.0.0.0', port=5000)