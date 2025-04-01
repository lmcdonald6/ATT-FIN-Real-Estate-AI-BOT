// Chat functionality
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
});

function initializeChat() {
    const chatButton = document.getElementById('chat-button');
    const chatContainer = document.getElementById('chat-container');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');

    // Toggle chat
    chatButton.addEventListener('click', () => {
        chatContainer.classList.toggle('hidden');
        if (!chatContainer.classList.contains('hidden')) {
            chatInput.focus();
        }
    });

    // Send message on enter
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send message on button click
    sendButton.addEventListener('click', sendMessage);

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage('user', message);
        chatInput.value = '';

        // Get AI response
        processMessage(message);
    }

    async function processMessage(message) {
        try {
            // Show typing indicator
            showTypingIndicator();

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator();

            // Add AI response
            addMessage('ai', data.response);

            // Handle any actions
            if (data.actions && data.actions.length > 0) {
                handleActions(data.actions);
            }

        } catch (error) {
            console.error('Error processing message:', error);
            removeTypingIndicator();
            addMessage('error', 'Sorry, I encountered an error. Please try again.');
        }
    }

    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message-bubble ${type === 'user' ? 'ml-auto bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'} p-3 rounded-lg`;

        if (type === 'error') {
            messageDiv.className = 'message-bubble mx-auto bg-red-100 text-red-800 p-3 rounded-lg';
        }

        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'message-bubble bg-gray-100 text-gray-800 p-3 rounded-lg flex space-x-1';
        indicator.innerHTML = `
            <span class="typing-dot animate-bounce">.</span>
            <span class="typing-dot animate-bounce" style="animation-delay: 0.2s">.</span>
            <span class="typing-dot animate-bounce" style="animation-delay: 0.4s">.</span>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function handleActions(actions) {
        actions.forEach(action => {
            switch (action.type) {
                case 'property_search':
                    // Trigger property search
                    searchProperties();
                    break;
                case 'market_analysis':
                    // Update market analysis charts
                    updateMarketAnalysis();
                    break;
                case 'investment_analysis':
                    // Show investment analysis section
                    showInvestmentAnalysis();
                    break;
            }
        });
    }

    async function updateMarketAnalysis() {
        try {
            const response = await fetch('/api/market/analysis');
            const data = await response.json();
            
            // Update charts with new data
            updateCharts(data);
            
            // Scroll to market analysis section
            document.querySelector('.market-analysis').scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error('Error updating market analysis:', error);
            addMessage('error', 'Failed to update market analysis. Please try again.');
        }
    }

    function showInvestmentAnalysis() {
        const section = document.querySelector('.investment-analysis');
        section.classList.remove('hidden');
        section.scrollIntoView({ behavior: 'smooth' });
    }

    // Add initial greeting
    setTimeout(() => {
        addMessage('ai', 'Hello! I\'m your AI real estate assistant. How can I help you today?');
    }, 500);
}

// Update charts with new data
function updateCharts(data) {
    // Update Price Trends
    const priceTrendsUpdate = {
        x: data.price_trends.dates,
        y: data.price_trends.prices
    };
    Plotly.update('price-trends', priceTrendsUpdate);

    // Update Market Stats
    const marketStatsUpdate = {
        values: data.market_stats.values,
        labels: data.market_stats.labels
    };
    Plotly.update('market-stats', marketStatsUpdate);
}
