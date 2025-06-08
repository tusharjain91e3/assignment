from flask import Blueprint, request, jsonify
from models import db, Category
from sqlalchemy import or_

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories with optional filtering"""
    try:
        # Query parameters
        parent_id = request.args.get('parent_id', type=int)
        include_children = request.args.get('include_children', 'false').lower() == 'true'
        include_products = request.args.get('include_products', 'false').lower() == 'true'
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Build query
        query = Category.query
        
        if active_only:
            query = query.filter(Category.is_active == True)
        
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        else:
            # Get root categories by default
            query = query.filter(Category.parent_id.is_(None))
        
        categories = query.order_by(Category.name).all()
        
        return jsonify({
            'success': True,
            'count': len(categories),
            'categories': [cat.to_dict(include_children, include_products) for cat in categories]
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get specific category by ID"""
    try:
        include_children = request.args.get('include_children', 'false').lower() == 'true'
        include_products = request.args.get('include_products', 'false').lower() == 'true'
        
        category = Category.query.filter_by(id=category_id, is_active=True).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify({
            'success': True,
            'category': category.to_dict(include_children, include_products)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@categories_bp.route('/categories/tree', methods=['GET'])
def get_category_tree():
    """Get full category tree structure"""
    try:
        def build_tree(parent_id=None):
            categories = Category.query.filter_by(parent_id=parent_id, is_active=True)\
                                    .order_by(Category.name).all()
            
            tree = []
            for category in categories:
                cat_dict = category.to_dict()
                cat_dict['children'] = build_tree(category.id)
                tree.append(cat_dict)
            
            return tree
        
        tree = build_tree()
        
        return jsonify({
            'success': True,
            'category_tree': tree
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
