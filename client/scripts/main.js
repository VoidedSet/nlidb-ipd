document.addEventListener('DOMContentLoaded', function () {
    const speechButton = document.getElementById('speech-btn');
    const userInput = document.getElementById('user-input');
    const chatBox = document.querySelector('.chat-box');
    const ttsButton = document.getElementById('tts-btn');

    const OLLAMA_API_URL = 'http://localhost:5000/chat';
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


// document.addEventListener("DOMContentLoaded", function () {
//   const chatBox = document.getElementById("chat-box");
//   const userInput = document.getElementById("user-input");
//   const sendButton = document.getElementById("send-button");
//   const speechButton = document.getElementById("speech-button");

//   // --- Chat history
//   let chatHistory = JSON.parse(localStorage.getItem("chatHistory") || "[]");

//   // --- Speech recognition setup
//   const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
//   const recognition = new SpeechRecognition();
//   recognition.continuous = false;
//   recognition.interimResults = false;
//   recognition.lang = "en-US";

//   let isListening = false;

//   recognition.onstart = () => {
//     isListening = true;
//     speechButton.classList.add("listening"); // 🔴 show mic active
//   };

//   recognition.onend = () => {
//     isListening = false;
//     speechButton.classList.remove("listening"); // ⚪ reset mic state
//   };

//   recognition.onresult = function (event) {
//     const transcript = event.results[0][0].transcript;
//     userInput.value = transcript;
//     sendQuery(transcript);
//   };

//   speechButton.addEventListener("click", function () {
//     if (!isListening) {
//       recognition.start();
//     } else {
//       recognition.stop();
//     }
//   });

//   // --- Auto-scroll helper
//   function scrollToBottom() {
//     chatBox.scrollTop = chatBox.scrollHeight;
//   }

//   // --- Add messages to chat UI
//   function appendMessage(role, text) {
//     const messageElement = document.createElement("div");
//     messageElement.classList.add("message", role);
//     messageElement.innerText = text;
//     chatBox.appendChild(messageElement);
//     scrollToBottom();
//   }

//   // --- Save history
//   function saveHistory() {
//     localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
//   }

//   // --- Send query to Ollama
//   async function sendQuery(query) {
//     if (!query.trim()) return;

//     // Add user message to UI
//     appendMessage("user", query);
//     userInput.value = "";

//     // Save user message
//     chatHistory.push({ role: "user", content: query });

//     try {
//       const response = await fetch("http://localhost:11434/api/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({
//           model: "llama3.2:1b",
//           messages: [
//             {
//               role: "system",
//               content:
//                 "You are an AI assistant disguised as a clumsy intern in an IT company who is still learning SQL.",
//             },
//             ...chatHistory,
//           ],
//         }),
//       });

//       const data = await response.json();

//       // Handle different response formats
//       const botReply =
//         data?.message?.content ||
//         data?.messages?.[0]?.content ||
//         "⚠️ No response received.";

//       // Save bot message
//       chatHistory.push({ role: "assistant", content: botReply });
//       saveHistory();

//       // Show bot message
//       appendMessage("bot", botReply);

//       // Speak out bot reply
//       const utterance = new SpeechSynthesisUtterance(botReply);
//       window.speechSynthesis.speak(utterance);
//     } catch (error) {
//       console.error("Error:", error);
//       appendMessage("bot", "⚠️ Failed to connect to Ollama server.");
//     }
//   }

//   // --- Event listeners
//   sendButton.addEventListener("click", () => {
//     sendQuery(userInput.value);
//   });

//   userInput.addEventListener("keydown", function (event) {
//     if (event.key === "Enter" && userInput.value.trim() !== "") {
//       event.preventDefault(); // prevent accidental new line
//       sendQuery(userInput.value);
//     }
//   });

//   // --- Restore chat history on load
//   if (chatHistory.length > 0) {
//     chatHistory.forEach((msg) => appendMessage(msg.role, msg.content));
//   }
// });
