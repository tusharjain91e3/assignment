
from flask import Blueprint, request, jsonify
from models import db, ChatSession, Product, Category
from services.ai_service import AIService
import uuid
import json

chat_bp = Blueprint('chat', __name__)
ai_service = AIService()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with AI integration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        session_id = data.get('session_id') or str(uuid.uuid4())
        
        # Extract intent
        intent = ai_service.extract_intent(user_message)
        
        # Get context based on intent
        context = {}
        if intent == 'search':
            # Get some sample products for context
            sample_products = Product.query.filter(Product.is_active == True)\
                                         .limit(3).all()
            context['sample_products'] = [p.to_dict() for p in sample_products]
        
        # Generate AI response
        bot_response = ai_service.generate_response(user_message, context)
        
        # Save to database
        chat_entry = ChatSession(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            intent=intent,
            context_data=json.dumps(context) if context else None
        )
        db.session.add(chat_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'bot_response': bot_response,
            'intent': intent,
            'message_id': chat_entry.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@chat_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for session"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400
        
        messages = ChatSession.query.filter_by(session_id=session_id)\
                                  .order_by(ChatSession.timestamp.asc())\
                                  .all()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message_count': len(messages),
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@chat_bp.route('/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400
        
        deleted_count = ChatSession.query.filter_by(session_id=session_id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} messages',
            'session_id': session_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
