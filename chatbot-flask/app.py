from flask import Flask, render_template, request, jsonify
import re
from datetime import datetime
import logging
import uuid
from database import (
    init_database, 
    save_conversation, 
    get_conversation_history, 
    get_statistics,
    search_conversations
)

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)

# Initialisation de la base de données au démarrage
init_database()

# Base de connaissances améliorée avec synonymes et variations
KNOWLEDGE_BASE = {
    'greeting': {
        'patterns': ['hello', 'hi', 'hey', 'bonjour', 'salut', 'good morning', 'good evening'],
        'responses': {
            'en': 'Hello! 👋 How can I help you today?',
            'fr': 'Bonjour ! 👋 Comment puis-je vous aider ?'
        }
    },
    'name': {
        'patterns': ['name', 'who are you', 'your name', 'nom', 'qui es-tu', 'qui êtes-vous'],
        'responses': {
            'en': 'My name is Hotel Assistant 🤖. I\'m here to help you with hotel information.',
            'fr': 'Je m\'appelle Assistant Hôtel 🤖. Je suis là pour vous aider avec les informations de l\'hôtel.'
        }
    },
    'age': {
        'patterns': ['old', 'age', 'âge', 'quel âge'],
        'responses': {
            'en': 'I\'m a virtual assistant, so I don\'t have an age! 😊',
            'fr': 'Je suis un assistant virtuel, donc je n\'ai pas d\'âge ! 😊'
        }
    },
    'availability': {
        'patterns': ['available', 'rooms', 'vacancy', 'chambres', 'disponible', 'libre'],
        'responses': {
            'en': 'Yes! 🛏️ We have 5 rooms available right now.',
            'fr': 'Oui ! 🛏️ Nous avons 5 chambres disponibles en ce moment.'
        }
    },
    'checkin': {
        'patterns': ['check-in', 'check in', 'arrival', 'arrivée', 'heure d\'arrivée'],
        'responses': {
            'en': 'Check-in time is at 12:00 PM (noon) 🕐',
            'fr': 'L\'heure d\'arrivée est à 12h00 (midi) 🕐'
        }
    },
    'checkout': {
        'patterns': ['check-out', 'check out', 'departure', 'départ', 'heure de départ'],
        'responses': {
            'en': 'Check-out time is at 11:00 AM 🕚',
            'fr': 'L\'heure de départ est à 11h00 🕚'
        }
    },
    'price': {
        'patterns': ['price', 'cost', 'rent', 'charge', 'fee', 'prix', 'coût', 'tarif', 'combien'],
        'responses': {
            'en': '💰 Our room rate is ₹1,500 for 24 hours.',
            'fr': '💰 Le tarif de notre chambre est de ₹1,500 pour 24 heures.'
        }
    },
    'tourism': {
        'patterns': ['tourist', 'attractions', 'visit', 'places', 'see', 'touristique', 'visiter', 'lieu'],
        'responses': {
            'en': '🗺️ Nearby attractions include: Taj Mahal, India Gate, Lotus Temple, and many more amazing places!',
            'fr': '🗺️ Les attractions à proximité incluent : Taj Mahal, India Gate, Lotus Temple, et bien d\'autres lieux magnifiques !'
        }
    },
    'cab': {
        'patterns': ['cab', 'taxi', 'transport', 'car'],
        'responses': {
            'en': '🚕 Yes, we provide taxi service at ₹12/KM.',
            'fr': '🚕 Oui, nous fournissons un service de taxi à ₹12/KM.'
        }
    },
    'food': {
        'patterns': ['food', 'restaurant', 'meal', 'dining', 'eat', 'nourriture', 'restaurant', 'repas', 'manger'],
        'responses': {
            'en': '🍽️ Yes, we have an excellent restaurant with diverse cuisine!',
            'fr': '🍽️ Oui, nous avons un excellent restaurant avec une cuisine variée !'
        }
    },
    'wifi': {
        'patterns': ['wifi', 'internet', 'connection'],
        'responses': {
            'en': '📶 Yes, free high-speed WiFi is available throughout the hotel.',
            'fr': '📶 Oui, le WiFi haut débit gratuit est disponible dans tout l\'hôtel.'
        }
    },
    'payment': {
        'patterns': ['payment', 'pay', 'methods', 'paiement', 'payer', 'moyens'],
        'responses': {
            'en': '💳 We accept UPI and Cash payments.',
            'fr': '💳 Nous acceptons les paiements UPI et en espèces.'
        }
    },
    'cancellation': {
        'patterns': ['cancel', 'refund', 'annulation', 'remboursement'],
        'responses': {
            'en': '✅ We offer free cancellation!',
            'fr': '✅ Nous offrons une annulation gratuite !'
        }
    },
    'parking': {
        'patterns': ['parking', 'park', 'car park', 'stationnement'],
        'responses': {
            'en': '🚗 Yes, free parking is available right in front of your room.',
            'fr': '🚗 Oui, un parking gratuit est disponible juste devant votre chambre.'
        }
    },
    'goodbye': {
        'patterns': ['bye', 'goodbye', 'see you', 'au revoir', 'à bientôt', 'adieu'],
        'responses': {
            'en': '👋 Goodbye! Have a great day! Feel free to come back anytime.',
            'fr': '👋 Au revoir ! Bonne journée ! N\'hésitez pas à revenir quand vous voulez.'
        }
    },
    'thanks': {
        'patterns': ['thank', 'thanks', 'merci', 'thank you'],
        'responses': {
            'en': '😊 You\'re welcome! Happy to help!',
            'fr': '😊 Je vous en prie ! Ravi de vous aider !'
        }
    },
    'help': {
        'patterns': ['help', 'aide', 'assist', 'support'],
        'responses': {
            'en': 'I can help you with: room availability, prices, check-in/out times, services (WiFi, parking, food, taxi), tourist places, and payment methods. What would you like to know?',
            'fr': 'Je peux vous aider avec : disponibilité des chambres, prix, horaires d\'arrivée/départ, services (WiFi, parking, nourriture, taxi), lieux touristiques et moyens de paiement. Que voulez-vous savoir ?'
        }
    }
}

# Mots français courants pour la détection de langue
FRENCH_WORDS = [
    'bonjour', 'merci', 'oui', 'non', 'salut', 'aide', 'comment', 'quoi', 
    'où', 'quand', 'pourquoi', 'combien', 'quel', 'quelle', 'est-ce', 
    'chambres', 'prix', 'disponible', 'heure'
]

def detect_language(text):
    """Détecte si le texte est en français ou anglais"""
    text_lower = text.lower()
    french_count = sum(1 for word in FRENCH_WORDS if word in text_lower)
    return 'fr' if french_count > 0 else 'en'

def normalize_text(text):
    """Normalise le texte pour la comparaison"""
    text = text.lower()
    text = re.sub(r'[?!.]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def find_best_match(user_input):
    """Trouve la meilleure correspondance dans la base de connaissances"""
    normalized_input = normalize_text(user_input)
    
    for category, data in KNOWLEDGE_BASE.items():
        for pattern in data['patterns']:
            if pattern in normalized_input:
                return category
    
    return None

def chatBot(user_input, session_id=None):
    """Fonction principale du chatbot avec NLP amélioré"""
    try:
        logging.info(f"Question reçue : {user_input}")
        
        # Détection de la langue
        lang = detect_language(user_input)
        logging.info(f"Langue détectée : {lang}")
        
        # Recherche de la meilleure correspondance
        category = find_best_match(user_input)
        
        if category:
            response = KNOWLEDGE_BASE[category]['responses'][lang]
            logging.info(f"Réponse trouvée (catégorie: {category})")
        else:
            default_responses = {
                'en': "I'm sorry, I don't have information about that. 😔 You can ask me about: rooms, prices, check-in/out, WiFi, parking, food, taxi, or tourist places.",
                'fr': "Désolé, je n'ai pas d'informations à ce sujet. 😔 Vous pouvez me poser des questions sur : chambres, prix, arrivée/départ, WiFi, parking, nourriture, taxi ou lieux touristiques."
            }
            logging.warning(f"Aucune correspondance trouvée pour : {user_input}")
            response = default_responses[lang]
        
        # Sauvegarder la conversation dans la base de données
        save_conversation(user_input, response, lang, session_id)
        
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans chatBot : {str(e)}")
        return "Sorry, an error occurred. Please try again. / Désolé, une erreur s'est produite. Veuillez réessayer."

@app.route("/")
def index():
    """Page d'accueil"""
    logging.info("Page d'accueil chargée")
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint API pour le chat"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            logging.warning("Requête invalide : message manquant")
            return jsonify({
                'error': 'Message is required',
                'reply': 'Please send a message. / Veuillez envoyer un message.'
            }), 400
        
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id", str(uuid.uuid4()))
        
        if not user_message:
            logging.warning("Message vide reçu")
            return jsonify({
                'error': 'Empty message',
                'reply': 'Please send a non-empty message. / Veuillez envoyer un message non vide.'
            }), 400
        
        # Génération de la réponse
        bot_reply = chatBot(user_message, session_id)
        
        logging.info(f"Réponse envoyée : {bot_reply[:50]}...")
        
        return jsonify({
            'reply': bot_reply,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })
        
    except Exception as e:
        logging.error(f"Erreur dans /chat : {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'reply': 'An error occurred. Please try again. / Une erreur s\'est produite. Veuillez réessayer.'
        }), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    """Récupère l'historique des conversations"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_conversation_history(limit)
        
        return jsonify({
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        logging.error(f"Erreur dans /api/history : {str(e)}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Récupère les statistiques d'utilisation"""
    try:
        stats = get_statistics()
        
        return jsonify({
            'statistics': stats,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Erreur dans /api/stats : {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.route("/api/search", methods=["GET"])
def search():
    """Recherche dans les conversations"""
    try:
        keyword = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not keyword:
            return jsonify({'error': 'Search keyword is required'}), 400
        
        results = search_conversations(keyword, limit)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'keyword': keyword
        })
        
    except Exception as e:
        logging.error(f"Erreur dans /api/search : {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404"""
    logging.warning(f"Page non trouvée : {request.url}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500"""
    logging.error(f"Erreur serveur : {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    logging.info("🚀 Démarrage du chatbot Flask avec base de données...")
    app.run(debug=True, host='0.0.0.0', port=5000)






# from flask import Flask, render_template, request, jsonify
# import re
# from datetime import datetime
# import logging

# app = Flask(__name__)

# # Configuration du logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('chatbot.log'),
#         logging.StreamHandler()
#     ]
# )

# # Base de connaissances améliorée avec synonymes et variations
# KNOWLEDGE_BASE = {
#     'greeting': {
#         'patterns': ['hello', 'hi', 'hey', 'bonjour', 'salut', 'good morning', 'good evening'],
#         'responses': {
#             'en': 'Hello! 👋 How can I help you today?',
#             'fr': 'Bonjour ! 👋 Comment puis-je vous aider ?'
#         }
#     },
#     'name': {
#         'patterns': ['name', 'who are you', 'your name', 'nom', 'qui es-tu', 'qui êtes-vous'],
#         'responses': {
#             'en': 'My name is Hotel Assistant 🤖. I\'m here to help you with hotel information.',
#             'fr': 'Je m\'appelle Assistant Hôtel 🤖. Je suis là pour vous aider avec les informations de l\'hôtel.'
#         }
#     },
#     'age': {
#         'patterns': ['old', 'age', 'âge', 'quel âge'],
#         'responses': {
#             'en': 'I\'m a virtual assistant, so I don\'t have an age! 😊',
#             'fr': 'Je suis un assistant virtuel, donc je n\'ai pas d\'âge ! 😊'
#         }
#     },
#     'availability': {
#         'patterns': ['available', 'rooms', 'vacancy', 'chambres', 'disponible', 'libre'],
#         'responses': {
#             'en': 'Yes! 🛏️ We have 5 rooms available right now.',
#             'fr': 'Oui ! 🛏️ Nous avons 5 chambres disponibles en ce moment.'
#         }
#     },
#     'checkin': {
#         'patterns': ['check-in', 'check in', 'arrival', 'arrivée', 'heure d\'arrivée'],
#         'responses': {
#             'en': 'Check-in time is at 12:00 PM (noon) 🕐',
#             'fr': 'L\'heure d\'arrivée est à 12h00 (midi) 🕐'
#         }
#     },
#     'checkout': {
#         'patterns': ['check-out', 'check out', 'departure', 'départ', 'heure de départ'],
#         'responses': {
#             'en': 'Check-out time is at 11:00 AM 🕚',
#             'fr': 'L\'heure de départ est à 11h00 🕚'
#         }
#     },
#     'price': {
#         'patterns': ['price', 'cost', 'rent', 'charge', 'fee', 'prix', 'coût', 'tarif', 'combien'],
#         'responses': {
#             'en': '💰 Our room rate is ₹1,500 for 24 hours.',
#             'fr': '💰 Le tarif de notre chambre est de ₹1,500 pour 24 heures.'
#         }
#     },
#     'tourism': {
#         'patterns': ['tourist', 'attractions', 'visit', 'places', 'see', 'touristique', 'visiter', 'lieu'],
#         'responses': {
#             'en': '🗺️ Nearby attractions include: Taj Mahal, India Gate, Lotus Temple, and many more amazing places!',
#             'fr': '🗺️ Les attractions à proximité incluent : Taj Mahal, India Gate, Lotus Temple, et bien d\'autres lieux magnifiques !'
#         }
#     },
#     'cab': {
#         'patterns': ['cab', 'taxi', 'transport', 'car'],
#         'responses': {
#             'en': '🚕 Yes, we provide taxi service at ₹12/KM.',
#             'fr': '🚕 Oui, nous fournissons un service de taxi à ₹12/KM.'
#         }
#     },
#     'food': {
#         'patterns': ['food', 'restaurant', 'meal', 'dining', 'eat', 'nourriture', 'restaurant', 'repas', 'manger'],
#         'responses': {
#             'en': '🍽️ Yes, we have an excellent restaurant with diverse cuisine!',
#             'fr': '🍽️ Oui, nous avons un excellent restaurant avec une cuisine variée !'
#         }
#     },
#     'wifi': {
#         'patterns': ['wifi', 'internet', 'connection'],
#         'responses': {
#             'en': '📶 Yes, free high-speed WiFi is available throughout the hotel.',
#             'fr': '📶 Oui, le WiFi haut débit gratuit est disponible dans tout l\'hôtel.'
#         }
#     },
#     'payment': {
#         'patterns': ['payment', 'pay', 'methods', 'paiement', 'payer', 'moyens'],
#         'responses': {
#             'en': '💳 We accept UPI and Cash payments.',
#             'fr': '💳 Nous acceptons les paiements UPI et en espèces.'
#         }
#     },
#     'cancellation': {
#         'patterns': ['cancel', 'refund', 'annulation', 'remboursement'],
#         'responses': {
#             'en': '✅ We offer free cancellation!',
#             'fr': '✅ Nous offrons une annulation gratuite !'
#         }
#     },
#     'parking': {
#         'patterns': ['parking', 'park', 'car park', 'stationnement'],
#         'responses': {
#             'en': '🚗 Yes, free parking is available right in front of your room.',
#             'fr': '🚗 Oui, un parking gratuit est disponible juste devant votre chambre.'
#         }
#     },
#     'goodbye': {
#         'patterns': ['bye', 'goodbye', 'see you', 'au revoir', 'à bientôt', 'adieu'],
#         'responses': {
#             'en': '👋 Goodbye! Have a great day! Feel free to come back anytime.',
#             'fr': '👋 Au revoir ! Bonne journée ! N\'hésitez pas à revenir quand vous voulez.'
#         }
#     },
#     'thanks': {
#         'patterns': ['thank', 'thanks', 'merci', 'thank you'],
#         'responses': {
#             'en': '😊 You\'re welcome! Happy to help!',
#             'fr': '😊 Je vous en prie ! Ravi de vous aider !'
#         }
#     },
#     'help': {
#         'patterns': ['help', 'aide', 'assist', 'support'],
#         'responses': {
#             'en': 'I can help you with: room availability, prices, check-in/out times, services (WiFi, parking, food, taxi), tourist places, and payment methods. What would you like to know?',
#             'fr': 'Je peux vous aider avec : disponibilité des chambres, prix, horaires d\'arrivée/départ, services (WiFi, parking, nourriture, taxi), lieux touristiques et moyens de paiement. Que voulez-vous savoir ?'
#         }
#     }
# }

# # Mots français courants pour la détection de langue
# FRENCH_WORDS = [
#     'bonjour', 'merci', 'oui', 'non', 'salut', 'aide', 'comment', 'quoi', 
#     'où', 'quand', 'pourquoi', 'combien', 'quel', 'quelle', 'est-ce', 
#     'chambres', 'prix', 'disponible', 'heure'
# ]

# def detect_language(text):
#     """Détecte si le texte est en français ou anglais"""
#     text_lower = text.lower()
#     french_count = sum(1 for word in FRENCH_WORDS if word in text_lower)
#     return 'fr' if french_count > 0 else 'en'

# def normalize_text(text):
#     """Normalise le texte pour la comparaison"""
#     # Convertir en minuscules
#     text = text.lower()
#     # Supprimer la ponctuation excessive
#     text = re.sub(r'[?!.]+', ' ', text)
#     # Supprimer les espaces multiples
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# def find_best_match(user_input):
#     """Trouve la meilleure correspondance dans la base de connaissances"""
#     normalized_input = normalize_text(user_input)
    
#     # Recherche par mots-clés
#     for category, data in KNOWLEDGE_BASE.items():
#         for pattern in data['patterns']:
#             if pattern in normalized_input:
#                 return category
    
#     return None

# def chatBot(user_input):
#     """Fonction principale du chatbot avec NLP amélioré"""
#     try:
#         # Log de la question
#         logging.info(f"Question reçue : {user_input}")
        
#         # Détection de la langue
#         lang = detect_language(user_input)
#         logging.info(f"Langue détectée : {lang}")
        
#         # Recherche de la meilleure correspondance
#         category = find_best_match(user_input)
        
#         if category:
#             response = KNOWLEDGE_BASE[category]['responses'][lang]
#             logging.info(f"Réponse trouvée (catégorie: {category})")
#             return response
        
#         # Réponse par défaut si aucune correspondance
#         default_responses = {
#             'en': "I'm sorry, I don't have information about that. 😔 You can ask me about: rooms, prices, check-in/out, WiFi, parking, food, taxi, or tourist places.",
#             'fr': "Désolé, je n'ai pas d'informations à ce sujet. 😔 Vous pouvez me poser des questions sur : chambres, prix, arrivée/départ, WiFi, parking, nourriture, taxi ou lieux touristiques."
#         }
        
#         logging.warning(f"Aucune correspondance trouvée pour : {user_input}")
#         return default_responses[lang]
        
#     except Exception as e:
#         logging.error(f"Erreur dans chatBot : {str(e)}")
#         return "Sorry, an error occurred. Please try again. / Désolé, une erreur s'est produite. Veuillez réessayer."

# @app.route("/")
# def index():
#     """Page d'accueil"""
#     logging.info("Page d'accueil chargée")
#     return render_template("index.html")

# @app.route("/chat", methods=["POST"])
# def chat():
#     """Endpoint API pour le chat"""
#     try:
#         # Récupération du message
#         data = request.get_json()
        
#         if not data or 'message' not in data:
#             logging.warning("Requête invalide : message manquant")
#             return jsonify({
#                 'error': 'Message is required',
#                 'reply': 'Please send a message. / Veuillez envoyer un message.'
#             }), 400
        
#         user_message = data.get("message", "").strip()
        
#         if not user_message:
#             logging.warning("Message vide reçu")
#             return jsonify({
#                 'error': 'Empty message',
#                 'reply': 'Please send a non-empty message. / Veuillez envoyer un message non vide.'
#             }), 400
        
#         # Génération de la réponse
#         bot_reply = chatBot(user_message)
        
#         # Log de la réponse
#         logging.info(f"Réponse envoyée : {bot_reply[:50]}...")
        
#         return jsonify({
#             'reply': bot_reply,
#             'timestamp': datetime.now().isoformat()
#         })
        
#     except Exception as e:
#         logging.error(f"Erreur dans /chat : {str(e)}")
#         return jsonify({
#             'error': 'Internal server error',
#             'reply': 'An error occurred. Please try again. / Une erreur s\'est produite. Veuillez réessayer.'
#         }), 500

# @app.errorhandler(404)
# def not_found(error):
#     """Gestionnaire d'erreur 404"""
#     logging.warning(f"Page non trouvée : {request.url}")
#     return jsonify({'error': 'Not found'}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     """Gestionnaire d'erreur 500"""
#     logging.error(f"Erreur serveur : {str(error)}")
#     return jsonify({'error': 'Internal server error'}), 500

# if __name__ == "__main__":
#     logging.info("🚀 Démarrage du chatbot Flask...")
#     app.run(debug=True, host='0.0.0.0', port=5000)