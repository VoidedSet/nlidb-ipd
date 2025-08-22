document.addEventListener('DOMContentLoaded', function() {
  const speechButton = document.getElementById('speech-btn');
  const userInput = document.getElementById('user-input');
  const chatBox = document.querySelector('.chat-box');
  const ttsButton = document.getElementById('tts-btn');

  // FIX: Changed the API URL to point to your backend server
  const API_URL = 'http://localhost:5000/chat';
  let isListening = false;
  let chatHistory = [];

  // --- Speech Recognition Fix ---
  // Check if the browser supports the Web Speech API
  const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = true;

    speechButton.addEventListener('click', function() {
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
    };

    recognition.onresult = function(event) {
      const transcript = event.results[event.results.length - 1][0].transcript;
      userInput.value = transcript;
    };
  } else {
    // If not supported, hide the button so the user can't click it
    speechButton.style.display = 'none';
    console.warn('Speech recognition is not supported in this browser.');
  }
  // --- End of Speech Recognition Fix ---


  ttsButton.addEventListener('click', function() {
    const lastResponse = chatBox.querySelector('.bot-response:last-child');
    if (lastResponse) {
      const responseText = lastResponse.textContent || lastResponse.innerText;
      const utterance = new SpeechSynthesisUtterance(responseText);
      window.speechSynthesis.speak(utterance);
    }
  });

  async function sendQuery(userQuery) {
    if (!userQuery.trim()) return;

    chatBox.innerHTML +=
        `<div class="query-items1"><div class="query-items-child"></div><blockquote class="user-query">${
            userQuery}</blockquote></div>`;
    userInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    chatHistory.push({role: 'user', content: userQuery});

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        // FIX: Sending the correct JSON body that the backend expects
        body: JSON.stringify({userQuery: userQuery, chatHistory: chatHistory})
      });

      if (!response.ok) {
        // Provide more detail on HTTP errors
        const errorBody = await response.json();
        throw new Error(`HTTP error! Status: ${response.status} - ${
            errorBody.formattedResponse || 'No details'}`);
      }

      const data = await response.json();
      // FIX: Parsing the correct response property from the backend
      if (data && data.formattedResponse) {
        const botReply = data.formattedResponse.trim();
        chatHistory.push({role: 'assistant', content: botReply});
        chatBox.innerHTML +=
            `<div class="query-items2"><div class="query-items-item"></div><blockquote class="bot-response">${
                botReply}</blockquote></div>`;
      } else {
        throw new Error('Unexpected response structure.');
      }
    } catch (error) {
      console.error('Error:', error);
      chatBox.innerHTML +=
          `<div class="query-items2"><div class="query-items-item"></div><blockquote class="error-response"><strong>Error!</strong><p>${
              error.message}</p></blockquote></div>`;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Use the send button from chat.html
  document.getElementById('send-button')
      .addEventListener('click', () => sendQuery(userInput.value));

  userInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      sendQuery(userInput.value);
    }
  });
});
