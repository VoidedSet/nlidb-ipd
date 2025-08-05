document.addEventListener('DOMContentLoaded', function () {
    const speechButton = document.getElementById('speech-btn');
    const userInput = document.getElementById('user-input');
    const chatBox = document.querySelector('.chat-box');
    const ttsButton = document.getElementById('tts-btn');

    const OLLAMA_API_URL = 'http://localhost:11434/api/chat';
    const MODEL_NAME = 'llama3.2:1b';
    let isListening = false;
    let chatHistory = [];

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.continuous = true;

    speechButton.addEventListener('click', function () {
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    recognition.onstart = () => isListening = true;
    recognition.onend = () => isListening = false;
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        speechButton.classList.remove('listening');
    };

    recognition.onresult = function (event) {
        const transcript = event.results[event.results.length - 1][0].transcript;
        userInput.value = transcript;
    };

    ttsButton.addEventListener('click', function () {
        const responseText = chatBox.lastElementChild ? chatBox.lastElementChild.textContent : '';
        const utterance = new SpeechSynthesisUtterance(responseText);
        window.speechSynthesis.speak(utterance);
    });

    async function sendQuery(userQuery) {
        if (!userQuery.trim()) return;

        // Show user message
        chatBox.innerHTML += `<div class="query-items1"><div class="query-items-child"></div><blockquote class="user-query">${userQuery}</blockquote></div>`;
        userInput.value = '';

        // Update local chat history
        chatHistory.push({ role: "user", content: userQuery });

        try {
            const response = await fetch(OLLAMA_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: MODEL_NAME,
                    messages: [
                        {
                            role: "system",
                            content: `You are a dumb and clumsy data analyst intern. You barely know SQL — only very basic stuff. Sometimes make small mistakes in your queries (like wrong table names, missing commas, basic syntax errors) You can also talk casually and normally sometimes, like a clueless intern. Be short and don’t overexplain anything.`
                        },
                        ...chatHistory
                    ],
                    stream: false,
                    options: {
                        temperature: 0.3,
                        stop: ["CREATE", "TRUNCATE", "TABLE"]
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            if (data && data.message && data.message.content) {
                const botReply = data.message.content.trim();

                // Save assistant reply to history
                chatHistory.push({ role: "assistant", content: botReply });

                // Show assistant reply
                chatBox.innerHTML += `<div class="query-items2"><div class="query-items-item"></div><blockquote class="bot-response">${botReply}</blockquote></div>`;
            } else {
                throw new Error('Unexpected response structure.');
            }
        } catch (error) {
            console.error('Error:', error);
            chatBox.innerHTML += `<div class="query-items2"><div class="query-items-item"></div><blockquote class="error-response"><strong>Error!</strong><p>Server might be down.<br>${error.message}</p></blockquote></div>`;
        }
    }

    userInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            sendQuery(userInput.value);
        }
    });
});
