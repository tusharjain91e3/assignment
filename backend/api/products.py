from flask import Blueprint, request, jsonify
from models import db, Product, Category
from sqlalchemy import or_, and_, desc, asc
from config import Config

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get products with filtering, sorting, and pagination"""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', Config.PRODUCTS_PER_PAGE, type=int), 100)
        
        # Filters
        category_id = request.args.get('category_id', type=int)
        brand = request.args.get('brand')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        in_stock = request.args.get('in_stock', 'false').lower() == 'true'
        featured = request.args.get('featured', 'false').lower() == 'true'
        
        # Sorting
        sort_by = request.args.get('sort_by', 'name')  # name, price, rating, created_at
        sort_order = request.args.get('sort_order', 'asc')  # asc, desc
        
        # Build query
        query = Product.query.filter(Product.is_active == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if brand:
            query = query.filter(Product.brand.ilike(f'%{brand}%'))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        
        if featured:
            query = query.filter(Product.is_featured == True)
        
        # Apply sorting
        if sort_by == 'price':
            order_column = Product.price
        elif sort_by == 'rating':
            order_column = Product.rating
        elif sort_by == 'created_at':
            order_column = Product.created_at
        else:
            order_column = Product.name
        
        if sort_order == 'desc':
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        
        # Execute query with pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        products = pagination.items
        
        return jsonify({
            'success': True,
            'products': [product.to_dict(include_category=True) for product in products],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product by ID"""
    try:
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'success': True,
            'product': product.to_dict(include_category=True)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@products_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        products = Product.query.filter(
            and_(Product.is_active == True, Product.is_featured == True)
        ).order_by(desc(Product.rating)).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(products),
            'products': [product.to_dict(include_category=True) for product in products]
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@products_bp.route('/products/recommendations', methods=['GET'])
def get_recommendations():
    """Get product recommendations"""
    try:
        category_id = request.args.get('category_id', type=int)
        product_id = request.args.get('exclude_product_id', type=int)
        limit = request.args.get('limit', 5, type=int)
        
        query = Product.query.filter(Product.is_active == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if product_id:
            query = query.filter(Product.id != product_id)
        
        # Recommend based on rating and popularity
        products = query.order_by(desc(Product.rating), desc(Product.review_count))\
                      .limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(products),
            'recommendations': [product.to_dict(include_category=True) for product in products]
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500