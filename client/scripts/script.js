// document.addEventListener('DOMContentLoaded', function() {
//     const centerIcon = document.getElementById('greet');
//     const optionsDiv = document.getElementById('options');
//     const chatBox = document.getElementById('chat-box');
//     const userInput = document.getElementById('user-input');
//     const sendButton = document.getElementById('send-button');

//     // Handle input focus to hide options and show chat box
//     userInput.addEventListener('focus', function() {
//         centerIcon.classList.add('hidden')
//         optionsDiv.classList.add('hidden');
//         chatBox.style.display = 'flex';
//         userInput.focus(); // Ensure input is focused
//     });

//     // Handle send button click
//     sendButton.addEventListener('click', function() {
//         const message = userInput.value.trim();
//         if (message) {
//             const messageElement = document.createElement('div');
//             messageElement.textContent = message;
//             chatBox.appendChild(messageElement);
//             userInput.value = '';
//             chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to latest message
//         }
//     });

//     // Optionally, handle enter key for sending messages
//     userInput.addEventListener('keypress', function(e) {
//         if (e.key === 'Enter') {
//             sendButton.click();
//         }
//     });
// });


document.addEventListener('DOMContentLoaded', function() {
    const centerIcon = document.getElementById('greet');
    const optionsDiv = document.getElementById('options');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Ensure chat box is hidden initially
    chatBox.style.display = 'none';

    // Handle input focus → hide greeting + options, show chat box
    userInput.addEventListener('focus', function() {
        centerIcon.classList.add('hidden');
        optionsDiv.classList.add('hidden');
        chatBox.style.display = 'flex';
    });

    // Function to append messages
    function appendMessage(text, sender = 'user') {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender); // 'message user' or 'message bot'
        messageElement.textContent = text;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    }

    // Handle send button click
    sendButton.addEventListener('click', function() {
        const message = userInput.value.trim();
        if (message) {
            appendMessage(message, 'user');
            userInput.value = '';
            // TODO: call backend/AI here and append bot response:
            // appendMessage("Bot reply goes here", 'bot');
        }
    });

    // Handle enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // prevent new line
            sendButton.click();
        }
    });
});
