
from flask import Blueprint, request, jsonify
from models import db, Product, Category, SearchLog
from sqlalchemy import or_, and_, desc, func
from config import Config

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_products():
    """Search products with advanced filtering"""
    try:
        # Search parameters
        query = request.args.get('q', '').strip()
        category_id = request.args.get('category_id', type=int)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', Config.SEARCH_RESULTS_PER_PAGE, type=int), 50)
        
        # Filters
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        brand = request.args.get('brand')
        min_rating = request.args.get('min_rating', type=float)
        in_stock = request.args.get('in_stock', 'false').lower() == 'true'
        
        # Sorting
        sort_by = request.args.get('sort_by', 'relevance')  # relevance, price, rating, name
        sort_order = request.args.get('sort_order', 'desc')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Build search query
        search_query = Product.query.filter(Product.is_active == True)
        
        # Text search across multiple fields
        search_terms = query.split()
        for term in search_terms:
            search_query = search_query.filter(
                or_(
                    Product.name.ilike(f'%{term}%'),
                    Product.description.ilike(f'%{term}%'),
                    Product.brand.ilike(f'%{term}%'),
                    Product.tags.ilike(f'%{term}%')
                )
            )
        
        # Apply filters
        if category_id:
            search_query = search_query.filter(Product.category_id == category_id)
        
        if brand:
            search_query = search_query.filter(Product.brand.ilike(f'%{brand}%'))
        
        if min_price is not None:
            search_query = search_query.filter(Product.price >= min_price)
        
        if max_price is not None:
            search_query = search_query.filter(Product.price <= max_price)
        
        if min_rating is not None:
            search_query = search_query.filter(Product.rating >= min_rating)
        
        if in_stock:
            search_query = search_query.filter(Product.stock_quantity > 0)
        
        # Apply sorting
        if sort_by == 'price':
            order_column = Product.price
        elif sort_by == 'rating':
            order_column = Product.rating
        elif sort_by == 'name':
            order_column = Product.name
        else:  # relevance
            order_column = Product.rating  # Simple relevance based on rating
        
        if sort_order == 'asc':
            search_query = search_query.order_by(order_column.asc())
        else:
            search_query = search_query.order_by(order_column.desc())
        
        # Execute search with pagination
        pagination = search_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        products = pagination.items
        
        # Log search
        try:
            search_log = SearchLog(
                query=query,
                results_count=pagination.total,
                session_id=request.args.get('session_id'),
                ip_address=request.remote_addr
            )
            db.session.add(search_log)
            db.session.commit()
        except:
            pass  # Don't fail if logging fails
        
        return jsonify({
            'success': True,
            'query': query,
            'results': [product.to_dict(include_category=True) for product in products],
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

@search_bp.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions based on popular searches"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            })
        
        # Get product name suggestions
        product_suggestions = db.session.query(Product.name)\
                                      .filter(and_(
                                          Product.is_active == True,
                                          Product.name.ilike(f'%{query}%')
                                      ))\
                                      .limit(limit//2).all()
        
        # Get brand suggestions
        brand_suggestions = db.session.query(Product.brand)\
                                    .filter(and_(
                                        Product.is_active == True,
                                        Product.brand.ilike(f'%{query}%'),
                                        Product.brand.isnot(None)
                                    ))\
                                    .distinct()\
                                    .limit(limit//2).all()
        
        suggestions = []
        suggestions.extend([p[0] for p in product_suggestions])
        suggestions.extend([b[0] for b in brand_suggestions])
        
        return jsonify({
            'success': True,
            'query': query,
            'suggestions': list(set(suggestions))[:limit]
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@search_bp.route('/search/popular', methods=['GET'])
def get_popular_searches():
    """Get popular search terms"""
    try:
        limit = request.args.get('limit', 10, type=int)
        days = request.args.get('days', 7, type=int)
        
        # Get popular searches from last N days
        from datetime import datetime, timedelta
        since_date = datetime.utcnow() - timedelta(days=days)
        
        popular_searches = db.session.query(
            SearchLog.query,
            func.count(SearchLog.id).label('search_count')
        ).filter(SearchLog.timestamp >= since_date)\
         .group_by(SearchLog.query)\
         .order_by(desc('search_count'))\
         .limit(limit).all()
        
        return jsonify({
            'success': True,
            'popular_searches': [
                {
                    'query': search.query,
                    'count': search.search_count
                } for search in popular_searches
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

