document.addEventListener('DOMContentLoaded', function() {
    // Éléments DOM
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const typingIndicator = document.getElementById('typing-indicator');
    const messageCountElement = document.getElementById('message-count');
    const clearChatBtn = document.getElementById('clear-chat');
    const toggleSoundBtn = document.getElementById('toggle-sound');
    const soundIcon = document.getElementById('sound-icon');
    const suggestionsButtons = document.querySelectorAll('.suggestion-btn');

    // État de l'application
    let messageCount = 0;
    let soundEnabled = true;
    const STORAGE_KEY = 'chatbot_history';
    const SOUND_KEY = 'chatbot_sound_enabled';

    // Sons (Web Audio API - sons simples)
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();

    /**
     * Joue un son de notification
     */
    function playNotificationSound() {
        if (!soundEnabled) return;
        
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }

    /**
     * Joue un son d'envoi
     */
    function playSendSound() {
        if (!soundEnabled) return;
        
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 600;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    }

    /**
     * Charge les préférences utilisateur
     */
    function loadPreferences() {
        const savedSound = localStorage.getItem(SOUND_KEY);
        if (savedSound !== null) {
            soundEnabled = savedSound === 'true';
            updateSoundIcon();
        }
    }

    /**
     * Met à jour l'icône du son
     */
    function updateSoundIcon() {
        soundIcon.textContent = soundEnabled ? '🔊' : '🔇';
        toggleSoundBtn.title = soundEnabled ? 'Désactiver les sons' : 'Activer les sons';
    }

    /**
     * Active/désactive le son
     */
    toggleSoundBtn.addEventListener('click', function() {
        soundEnabled = !soundEnabled;
        localStorage.setItem(SOUND_KEY, soundEnabled);
        updateSoundIcon();
        
        // Feedback visuel
        this.classList.add('notification-blink');
        setTimeout(() => this.classList.remove('notification-blink'), 1500);
        
        if (soundEnabled) {
            playNotificationSound();
        }
    });

    /**
     * Formate l'heure actuelle
     */
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    /**
     * Met à jour le compteur de messages
     */
    function updateMessageCount() {
        messageCount++;
        messageCountElement.textContent = messageCount;
    }

    /**
     * Sauvegarde l'historique dans localStorage
     */
    function saveToHistory(message, sender) {
        const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        history.push({
            message: message,
            sender: sender,
            timestamp: new Date().toISOString()
        });
        
        // Limite à 100 messages
        if (history.length > 100) {
            history.shift();
        }
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    }

    /**
     * Charge l'historique depuis localStorage
     */
    function loadHistory() {
        const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        
        // Vider le chat window sauf le message de bienvenue
        const welcomeMessage = chatWindow.querySelector('.message.bot');
        chatWindow.innerHTML = '';
        if (welcomeMessage) {
            chatWindow.appendChild(welcomeMessage);
        }
        
        // Charger les messages de l'historique
        history.forEach(item => {
            appendMessage(item.message, item.sender, false, new Date(item.timestamp));
        });
        
        // Mettre à jour le compteur
        messageCount = history.length;
        messageCountElement.textContent = messageCount;
    }

    /**
     * Efface l'historique
     */
    clearChatBtn.addEventListener('click', function() {
        if (confirm('Êtes-vous sûr de vouloir effacer toute la conversation ?')) {
            localStorage.removeItem(STORAGE_KEY);
            
            // Garder uniquement le message de bienvenue
            const welcomeMessage = chatWindow.querySelector('.message.bot');
            chatWindow.innerHTML = '';
            if (welcomeMessage) {
                chatWindow.appendChild(welcomeMessage);
            }
            
            messageCount = 0;
            messageCountElement.textContent = messageCount;
            
            // Feedback visuel
            this.classList.add('notification-blink');
            setTimeout(() => this.classList.remove('notification-blink'), 1500);
        }
    });

    /**
     * Ajoute un message dans la fenêtre de chat
     */
    function appendMessage(text, sender, saveHistory = true, customTime = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + sender;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Avatar
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'bot' ? '🤖' : '👤';
        
        // Bulle de message
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        
        // Horodatage
        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = customTime ? customTime.toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        }) : getCurrentTime();
        
        bubble.appendChild(paragraph);
        bubble.appendChild(timestamp);
        messageContent.appendChild(avatar);
        messageContent.appendChild(bubble);
        messageDiv.appendChild(messageContent);
        
        chatWindow.appendChild(messageDiv);
        scrollToBottom();
        
        // Sauvegarder dans l'historique
        if (saveHistory) {
            saveToHistory(text, sender);
            updateMessageCount();
        }
        
        // Jouer un son pour les messages du bot
        if (sender === 'bot' && saveHistory) {
            playNotificationSound();
        }
    }

    /**
     * Fait défiler la fenêtre de chat vers le bas
     */
    function scrollToBottom() {
        chatWindow.scrollTo({
            top: chatWindow.scrollHeight,
            behavior: 'smooth'
        });
    }

    /**
     * Affiche l'indicateur "le bot est en train d'écrire..."
     */
    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        scrollToBottom();
    }

    /**
     * Cache l'indicateur "le bot est en train d'écrire..."
     */
    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    /**
     * Désactive le formulaire pendant l'envoi
     */
    function disableForm() {
        userInput.disabled = true;
        chatForm.querySelector('button[type="submit"]').disabled = true;
        suggestionsButtons.forEach(btn => btn.disabled = true);
    }

    /**
     * Réactive le formulaire après la réponse
     */
    function enableForm() {
        userInput.disabled = false;
        chatForm.querySelector('button[type="submit"]').disabled = false;
        suggestionsButtons.forEach(btn => btn.disabled = false);
        userInput.focus();
    }

    /**
     * Envoie un message au chatbot
     */
    function sendMessage(message) {
        if (!message.trim()) return;
        
        // Afficher le message de l'utilisateur
        appendMessage(message, 'user');
        playSendSound();
        
        // Désactiver le formulaire pendant le traitement
        disableForm();
        
        // Afficher l'indicateur "typing..."
        showTypingIndicator();
        
        // Envoyer le message au serveur
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur réseau');
            }
            return response.json();
        })
        .then(data => {
            // Simuler un délai de réponse (plus naturel)
            setTimeout(() => {
                hideTypingIndicator();
                appendMessage(data.reply, 'bot');
                enableForm();
            }, 500 + Math.random() * 500);
        })
        .catch(error => {
            console.error('Erreur:', error);
            hideTypingIndicator();
            appendMessage('Désolé, une erreur s\'est produite. Veuillez réessayer.', 'bot');
            enableForm();
        });
    }

    /**
     * Gère la soumission du formulaire
     */
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        userInput.value = '';
        sendMessage(message);
    });

    /**
     * Gère les clics sur les boutons de suggestions
     */
    suggestionsButtons.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.getAttribute('data-message');
            userInput.value = message;
            sendMessage(message);
            userInput.value = '';
        });
    });

    /**
     * Permet d'envoyer le message avec Ctrl+Enter
     */
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    /**
     * Animation de l'input quand l'utilisateur tape
     */
    let typingTimeout;
    userInput.addEventListener('input', function() {
        clearTimeout(typingTimeout);
        this.style.borderColor = '#667eea';
        
        typingTimeout = setTimeout(() => {
            this.style.borderColor = '#e2e8f0';
        }, 1000);
    });

    // Initialisation
    loadPreferences();
    loadHistory();
    userInput.focus();
    
    console.log('💬 Chatbot initialisé avec succès !');
    console.log('📊 Historique chargé:', messageCount, 'messages');
});