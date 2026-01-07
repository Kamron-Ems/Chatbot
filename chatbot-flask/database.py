import sqlite3
from datetime import datetime
import logging

DATABASE_NAME = 'chatbot.db'

def init_database():
    """Initialise la base de données avec les tables nécessaires"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Table pour les conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                language TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            )
        ''')
        
        # Table pour les statistiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_messages INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialiser les stats si vide
        cursor.execute('SELECT COUNT(*) FROM statistics')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO statistics (total_messages, total_sessions) VALUES (0, 0)')
        
        conn.commit()
        conn.close()
        
        logging.info("✅ Base de données initialisée avec succès")
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'initialisation de la base de données : {str(e)}")
        raise

def save_conversation(user_message, bot_response, language='en', session_id=None):
    """Sauvegarde une conversation dans la base de données"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_message, bot_response, language, session_id)
            VALUES (?, ?, ?, ?)
        ''', (user_message, bot_response, language, session_id))
        
        # Mettre à jour les statistiques
        cursor.execute('''
            UPDATE statistics 
            SET total_messages = total_messages + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info(f"💾 Conversation sauvegardée : {user_message[:30]}...")
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la sauvegarde : {str(e)}")

def get_conversation_history(limit=50):
    """Récupère l'historique des conversations"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, language, timestamp
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return [
            {
                'user_message': conv[0],
                'bot_response': conv[1],
                'language': conv[2],
                'timestamp': conv[3]
            }
            for conv in conversations
        ]
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la récupération de l'historique : {str(e)}")
        return []

def get_statistics():
    """Récupère les statistiques d'utilisation"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Stats générales
        cursor.execute('SELECT total_messages, last_updated FROM statistics WHERE id = 1')
        stats = cursor.fetchone()
        
        # Messages par langue
        cursor.execute('''
            SELECT language, COUNT(*) as count
            FROM conversations
            GROUP BY language
        ''')
        messages_by_language = dict(cursor.fetchall())
        
        # Messages aujourd'hui
        cursor.execute('''
            SELECT COUNT(*)
            FROM conversations
            WHERE DATE(timestamp) = DATE('now')
        ''')
        messages_today = cursor.fetchone()[0]
        
        # Messages cette semaine
        cursor.execute('''
            SELECT COUNT(*)
            FROM conversations
            WHERE DATE(timestamp) >= DATE('now', '-7 days')
        ''')
        messages_this_week = cursor.fetchone()[0]
        
        # Top 5 des questions (mots-clés)
        cursor.execute('''
            SELECT user_message, COUNT(*) as count
            FROM conversations
            GROUP BY LOWER(user_message)
            ORDER BY count DESC
            LIMIT 5
        ''')
        top_questions = [
            {'question': q[0], 'count': q[1]}
            for q in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'total_messages': stats[0] if stats else 0,
            'last_updated': stats[1] if stats else None,
            'messages_by_language': messages_by_language,
            'messages_today': messages_today,
            'messages_this_week': messages_this_week,
            'top_questions': top_questions
        }
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la récupération des statistiques : {str(e)}")
        return {
            'total_messages': 0,
            'messages_by_language': {},
            'messages_today': 0,
            'messages_this_week': 0,
            'top_questions': []
        }

def clear_old_conversations(days=30):
    """Supprime les conversations plus anciennes que X jours"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM conversations
            WHERE DATE(timestamp) < DATE('now', '-' || ? || ' days')
        ''', (days,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logging.info(f"🗑️ {deleted_count} anciennes conversations supprimées")
        return deleted_count
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la suppression : {str(e)}")
        return 0

def search_conversations(keyword, limit=20):
    """Recherche dans les conversations"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, timestamp
            FROM conversations
            WHERE user_message LIKE ? OR bot_response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{keyword}%', f'%{keyword}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'user_message': r[0],
                'bot_response': r[1],
                'timestamp': r[2]
            }
            for r in results
        ]
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la recherche : {str(e)}")
        return []