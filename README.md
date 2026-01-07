# Chatbot Flask

Un chatbot simple développé avec Flask pour répondre aux questions fréquentes concernant un hôtel.

## 📋 Description

Ce projet est un chatbot conversationnel basé sur Flask qui peut répondre à diverses questions concernant :
- Les informations sur l'hôtel
- Les disponibilités de chambres
- Les horaires de check-in/check-out
- Les tarifs
- Les services disponibles (WiFi, parking, nourriture, taxi)
- Les attractions touristiques à proximité

## 🚀 Fonctionnalités

- Interface web intuitive
- Réponses en temps réel
- Design responsive
- Gestion simple des conversations
- Module de web scraping inclus

## 📁 Structure du projet
```
orbique/
├── chatbot-flask/
│   ├── app.py              # Application Flask principale
│   ├── static/
│   │   ├── script.js       # Logique JavaScript
│   │   └── style.css       # Styles CSS
│   └── templates/
│       └── index.html      # Interface utilisateur
├── main.py                 # Point d'entrée principal
├── README.md               # Documentation
└── WebScraping/
    ├── books.txt           # Données extraites
    └── webscraping.py      # Script de web scraping
```

## 🛠️ Technologies utilisées

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Web Scraping**: Python (BeautifulSoup ou Requests)

## 📦 Installation

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/orbique.git
cd orbique
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
   - Windows :
```bash
   venv\Scripts\activate
```
   - Linux/Mac :
```bash
   source venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install flask
```

## 🚀 Utilisation

1. Naviguez vers le dossier chatbot-flask :
```bash
cd chatbot-flask
```

2. Lancez l'application :
```bash
python app.py
```

3. Ouvrez votre navigateur et accédez à :
```
http://localhost:5000
```

4. Commencez à discuter avec le chatbot !

## 💬 Exemples de questions

- "Hello" - Pour saluer le bot
- "What is your name?" - Pour connaître le nom du bot
- "Are rooms available?" - Pour vérifier la disponibilité
- "What is the price?" - Pour connaître les tarifs
- "Do you have WiFi?" - Pour les services disponibles
- "What are the tourist places?" - Pour les attractions touristiques

## 🔧 Configuration

Pour personnaliser le chatbot, modifiez la fonction `chatBot()` dans le fichier `app.py` pour ajouter de nouvelles réponses ou modifier les réponses existantes.

## 📝 Remarques

- Le chatbot utilise une logique simple basée sur des mots-clés
- Les réponses sont prédéfinies dans le code
- Pour une version plus avancée, envisagez d'utiliser le NLP (Natural Language Processing)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## 👤 Auteur

Développé par [Votre Nom]

## 📞 Contact

Pour toute question ou suggestion, n'hésitez pas à me contacter.

---

⭐ Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile !