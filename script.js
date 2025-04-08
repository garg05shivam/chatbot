document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    
    // Generate a unique session ID for this conversation
    const sessionId = generateSessionId();
    
    // Add a loading animation at startup
    showLoadingAnimation();
    
    // Function to generate a random session ID
    function generateSessionId() {
        return 'session_' + Math.random().toString(36).substring(2, 15);
    }
    
    // Function to show a loading animation at startup
    function showLoadingAnimation() {
        const loadingAnimation = document.createElement('div');
        loadingAnimation.classList.add('loading-animation');
        loadingAnimation.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Initializing History Storyteller AI...</div>
        `;
        chatMessages.appendChild(loadingAnimation);
        
        // Remove loading animation after a delay and show greeting
        setTimeout(() => {
            loadingAnimation.remove();
            // Add initial greeting with typewriter effect
            addMessageWithTypewriter("Hello! I'm your History Storyteller. I can share fascinating stories about historical events, cultural heritage, ancient civilizations, and interesting tales from the past. 📚 What would you like to learn about today?");
        }, 1500);
    }

    // Function to add a message to the chat with optional typewriter effect
    function addMessage(message, isUser = false, useTypewriter = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', isUser ? 'user' : 'bot');
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        if (useTypewriter && !isUser) {
            messageContent.textContent = '';
            messageDiv.appendChild(messageContent);
            chatMessages.appendChild(messageDiv);
            typeWriter(messageContent, message, 0, 30);
        } else {
            messageContent.textContent = message;
            messageDiv.appendChild(messageContent);
            chatMessages.appendChild(messageDiv);
        }
        
        // Add sound effect for new messages
        playMessageSound(isUser);
        
        // Scroll to the bottom
        scrollToBottom();
    }
    
    // Function for typewriter effect
    function typeWriter(element, text, index, speed) {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(() => typeWriter(element, text, index, speed), speed);
        }
        scrollToBottom();
    }
    
    // Function to add message with typewriter effect
    function addMessageWithTypewriter(message, isUser = false) {
        addMessage(message, isUser, true);
    }
    
    // Function to play message sound
    function playMessageSound(isUser) {
        // You can implement actual sound here if desired
        // This is just a placeholder for the functionality
        console.log(`Playing ${isUser ? 'send' : 'receive'} message sound`);
    }
    
    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('typing-indicator');
        indicator.id = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            indicator.appendChild(dot);
        }
        
        chatMessages.appendChild(indicator);
        scrollToBottom();
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Function to send message to the server
    async function sendMessage(message) {
        try {
            showTypingIndicator();
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            removeTypingIndicator();
            
            if (response.ok) {
                addMessageWithTypewriter(data.response);
            } else {
                addMessageWithTypewriter('Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            removeTypingIndicator();
            addMessageWithTypewriter('Network error. Please check your connection and try again.');
            console.error('Error sending message:', error);
        } finally {
            // Always re-enable input and focus it
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    }

    // Handle send button click
    sendButton.addEventListener('click', () => {
        sendUserMessage();
    });

    // Handle Enter key press
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendUserMessage();
        }
    });
    
    // Function to handle sending user message
    function sendUserMessage() {
        const message = userInput.value.trim();
        
        if (message) {
            // Disable input while processing
            userInput.disabled = true;
            sendButton.disabled = true;
            
            addMessage(message, true);
            userInput.value = '';
            
            sendMessage(message).finally(() => {
                // Re-enable input after processing
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            });
        }
    }
    
    // Focus input field on startup
    setTimeout(() => {
        userInput.focus();
    }, 2000);
}); 