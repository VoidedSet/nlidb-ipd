// Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_TIMEOUT = 120000; // 2 minutes

// DOM Elements
const messagesArea = document.getElementById('messagesArea');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const clearHistoryBtn = document.getElementById('clear-history');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const closeModal = document.querySelector('.close-modal');

// Radio buttons for source selection
const sourceRadios = document.querySelectorAll('input[name="source"]');
const mysqlConfig = document.getElementById('mysql-config');
const csvConfig = document.getElementById('csv-config');
const connectDbBtn = document.getElementById('connect-db');
const uploadCsvBtn = document.getElementById('upload-csv');
const dbNameInput = document.getElementById('db-name');
const dbUserInput = document.getElementById('db-user');
const dbPassInput = document.getElementById('db-pass');
const csvFileInput = document.getElementById('csv-file');
const dbStatus = document.getElementById('db-status');
const csvStatus = document.getElementById('csv-status');

// State
let messageHistory = [];
let isLoading = false;
let currentCsvFile = null;  // Track current CSV file name

// ===== INITIALIZATION =====

document.addEventListener('DOMContentLoaded', () => {
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isLoading) {
            sendMessage();
        }
    });

    clearHistoryBtn.addEventListener('click', clearHistory);

    // Source selection
    sourceRadios.forEach(radio => {
        radio.addEventListener('change', handleSourceChange);
    });

    connectDbBtn.addEventListener('click', connectDatabase);
    uploadCsvBtn.addEventListener('click', uploadCSV);
    
    // Load any saved connection on page load
    loadSavedConnection();

    // Modal
    closeModal.addEventListener('click', () => closeImageModal());
    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) closeImageModal();
    });

    // Load message history from localStorage
    loadMessageHistory();
});

// ===== MESSAGE HANDLING =====

function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || isLoading) return;

    // Add user message
    addMessage('user', text);
    messageInput.value = '';
    messageInput.focus();

    // Send to API
    fetchChatResponse(text);
}

function addMessage(role, content) {
    // Remove welcome message if first message
    if (messageHistory.length === 0) {
        messagesArea.innerHTML = '';
    }

    const messageObj = { role, content, timestamp: new Date().toISOString() };
    messageHistory.push(messageObj);
    renderMessage(messageObj);
    saveMessageHistory();
    scrollToBottom();
}

function renderMessage(messageObj) {
    const { role, content } = messageObj;
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;

    if (role === 'user') {
        // User message
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = content;
        messageEl.appendChild(bubble);
    } else if (role === 'assistant') {
        // Assistant message
        if (typeof content === 'string') {
            // Simple text response
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.textContent = content;
            messageEl.appendChild(bubble);
        } else {
            // Complex response object
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            const contentDiv = document.createElement('div');
            contentDiv.className = 'response-content';

            // Main answer
            if (content.answer) {
                const answerDiv = document.createElement('div');
                answerDiv.className = 'response-answer';
                answerDiv.innerHTML = formatMarkdown(content.answer);
                contentDiv.appendChild(answerDiv);
            }

            // Thinking process (for EDA tasks)
            if (content.steps && content.steps.length > 0) {
                const thinkingSection = document.createElement('div');
                thinkingSection.className = 'thinking-section';

                const toggle = document.createElement('div');
                toggle.className = 'thinking-toggle collapsed';
                toggle.innerHTML = '<span class="thinking-toggle-icon">▶</span> View Thinking Process';
                toggle.style.cursor = 'pointer';

                const details = document.createElement('div');
                details.className = 'thinking-details';

                content.steps.forEach((step, index) => {
                    const stepDiv = document.createElement('div');
                    stepDiv.className = 'step';

                    let stepHTML = `<div class="step-header">Attempt ${step.attempt}</div>`;
                    stepHTML += `<div class="step-thought">${step.thought}</div>`;

                    if (step.code) {
                        stepHTML += `<div class="step-code"><strong>Code:</strong><pre>${escapeHtml(step.code)}</pre></div>`;
                    }

                    if (step.error) {
                        stepHTML += `<div class="step-error"><strong>Error:</strong> ${escapeHtml(step.error)}</div>`;
                    }

                    if (step.output) {
                        stepHTML += `<div class="step-output"><strong>Output:</strong><pre>${escapeHtml(step.output)}</pre></div>`;
                    }

                    stepDiv.innerHTML = stepHTML;
                    details.appendChild(stepDiv);
                });

                toggle.addEventListener('click', () => {
                    toggle.classList.toggle('collapsed');
                    details.classList.toggle('expanded');
                });

                thinkingSection.appendChild(toggle);
                thinkingSection.appendChild(details);
                contentDiv.appendChild(thinkingSection);
            }

            // Data table
            if (content.dataframe) {
                try {
                    const data = JSON.parse(content.dataframe);
                    if (Array.isArray(data) && data.length > 0) {
                        const tableSection = document.createElement('div');
                        tableSection.className = 'data-table-section';

                        const caption = document.createElement('div');
                        caption.className = 'data-table-caption';
                        caption.textContent = '📊 Data Preview:';
                        tableSection.appendChild(caption);

                        const table = createDataTable(data);
                        tableSection.appendChild(table);
                        contentDiv.appendChild(tableSection);
                    }
                } catch (e) {
                    console.error('Error parsing dataframe:', e);
                }
            }

            // Image
            if (content.image) {
                const imageSection = document.createElement('div');
                imageSection.className = 'image-section';

                const caption = document.createElement('div');
                caption.className = 'image-caption';
                caption.textContent = '📈 Generated Visualization:';
                imageSection.appendChild(caption);

                const imgContainer = document.createElement('div');
                imgContainer.className = 'image-container';
                imgContainer.style.cursor = 'pointer';

                const img = document.createElement('img');
                img.src = `data:image/png;base64,${content.image}`;
                img.alt = 'Visualization';

                img.addEventListener('click', () => openImageModal(img.src));

                imgContainer.appendChild(img);
                imgContainer.addEventListener('click', () => openImageModal(img.src));

                imageSection.appendChild(imgContainer);
                contentDiv.appendChild(imageSection);
            }

            bubble.appendChild(contentDiv);
            messageEl.appendChild(bubble);
        }
    } else if (role === 'error') {
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = content;
        messageEl.className += ' error';
        messageEl.appendChild(bubble);
    }

    messagesArea.appendChild(messageEl);
}

function createDataTable(data) {
    const table = document.createElement('table');
    table.className = 'data-table';

    // Get columns from first row
    const columns = Object.keys(data[0]);

    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create body (limit to 100 rows for performance)
    const tbody = document.createElement('tbody');
    data.slice(0, 100).forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            let value = row[col];
            if (value === null || value === undefined) {
                value = '-';
            } else if (typeof value === 'number') {
                value = value.toFixed(2);
            }
            td.textContent = String(value).substring(0, 100);
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    return table;
}

function formatMarkdown(text) {
    if (!text) return '';

    // Escape HTML first
    let html = escapeHtml(text);

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    // Lists
    html = html.replace(/^\* (.*?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    return html;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ===== API COMMUNICATION =====

async function fetchChatResponse(userMessage) {
    isLoading = true;
    loadingIndicator.style.display = 'flex';

    try {
        const dbUrl = sessionStorage.getItem('dbUrl');
        const payload = { text: userMessage };
        
        if (dbUrl) {
            payload.db_url = dbUrl;
            console.log('[Frontend] Sending with DB URL:', dbUrl);
        } else {
            console.log('[Frontend] No DB URL - using default/CSV');
        }
        
        if (currentCsvFile) {
            payload.csv_source = currentCsvFile;
            console.log('[Frontend] Using CSV:', currentCsvFile);
        }
        
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Process response based on type
        if (data.type === 'sql') {
            addMessage('assistant', data.answer);
        } else if (data.type === 'eda') {
            addMessage('assistant', {
                answer: data.answer,
                steps: data.steps,
                image: data.image,
                dataframe: data.dataframe
            });
        } else if (data.type === 'error') {
            addMessage('error', data.answer);
        } else {
            addMessage('assistant', data);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('error', `Connection failed: ${error.message}. Make sure the API is running at ${API_BASE_URL}`);
    } finally {
        isLoading = false;
        loadingIndicator.style.display = 'none';
        messageInput.focus();
    }
}

// ===== DATA SOURCE CONFIGURATION =====

function handleSourceChange(e) {
    if (e.target.value === 'mysql') {
        mysqlConfig.style.display = 'flex';
        csvConfig.style.display = 'none';
        currentCsvFile = null;  // Clear CSV source when switching to MySQL
    } else {
        mysqlConfig.style.display = 'none';
        csvConfig.style.display = 'flex';
        sessionStorage.removeItem('dbUrl');  // Clear DB URL when switching to CSV
    }
}

function loadSavedConnection() {
    const saved = sessionStorage.getItem('dbUrl');
    if (saved) {
        updateStatus(dbStatus, 'Active connection found', 'connected');
        connectDbBtn.innerHTML = '✓ Connected<br><small style="font-size:11px">Click to change</small>';
    }
}

function connectDatabase() {
    // If already connected, allow to change
    if (sessionStorage.getItem('dbUrl')) {
        // Reset UI to allow new connection
        dbNameInput.disabled = false;
        dbUserInput.disabled = false;
        dbPassInput.disabled = false;
        connectDbBtn.textContent = 'Connect';
        connectDbBtn.disabled = false;
        dbNameInput.value = '';
        dbUserInput.value = 'root';
        dbPassInput.value = '';
        sessionStorage.removeItem('dbUrl');
        currentCsvFile = null;
        updateStatus(dbStatus, 'Connection cleared - enter new credentials', 'error');
        console.log('[DB] Connection reset');
        return;
    }
    
    const dbName = dbNameInput.value.trim();
    const dbUser = dbUserInput.value.trim() || 'root';
    const dbPass = dbPassInput.value.trim();

    if (!dbName) {
        updateStatus(dbStatus, 'Please enter a database name', 'error');
        return;
    }

    // Construct the database URL
    const dbUrl = dbPass 
        ? `mysql+mysqlconnector://${dbUser}:${dbPass}@localhost:3306/${dbName}`
        : `mysql+mysqlconnector://${dbUser}@localhost:3306/${dbName}`;

    console.log('[Frontend] DB Connection Attempt:', dbName, 'User:', dbUser);
    console.log('[Frontend] DB URL:', dbUrl);
    
    // Store in session
    sessionStorage.setItem('dbUrl', dbUrl);
    currentCsvFile = null;  // Clear CSV when connecting to DB

    updateStatus(dbStatus, `✓ Connected to "${dbName}"`, 'connected');
    dbNameInput.disabled = true;
    dbUserInput.disabled = true;
    dbPassInput.disabled = true;
    connectDbBtn.innerHTML = '✓ Connected<br><small style="font-size:11px">Click to change</small>';
    connectDbBtn.disabled = false;  // Allow clicking to change
}

function uploadCSV() {
    const file = csvFileInput.files[0];
    if (!file) {
        updateStatus(csvStatus, 'Please select a CSV file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch(`${API_BASE_URL}/upload-csv`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            currentCsvFile = data.filename;
            updateStatus(csvStatus, `✓ Uploaded: ${data.filename} (${data.rows} rows)`, 'connected');
            uploadCsvBtn.textContent = '✓ Uploaded';
            uploadCsvBtn.disabled = true;
        } else {
            updateStatus(csvStatus, `Error: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        updateStatus(csvStatus, `Upload failed: ${error.message}`, 'error');
    });
}

function updateStatus(element, message, status) {
    element.textContent = message;
    element.className = `status-indicator ${status}`;
}

// ===== MODAL =====

function openImageModal(src) {
    modalImage.src = src;
    imageModal.style.display = 'flex';
}

function closeImageModal() {
    imageModal.style.display = 'none';
}

// ===== HISTORY MANAGEMENT =====

function saveMessageHistory() {
    // Save only text content for localStorage (not complex objects)
    const simplified = messageHistory.map(msg => ({
        role: msg.role,
        content: typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content),
        timestamp: msg.timestamp
    }));
    localStorage.setItem('querifyHistory', JSON.stringify(simplified));
}

function loadMessageHistory() {
    const saved = localStorage.getItem('querifyHistory');
    if (saved) {
        try {
            const history = JSON.parse(saved);
            messageHistory = history.map(msg => ({
                ...msg,
                content: typeof msg.content === 'string' && msg.content.startsWith('{')
                    ? JSON.parse(msg.content)
                    : msg.content
            }));

            // Render all messages
            messagesArea.innerHTML = '';
            messageHistory.forEach(msg => renderMessage(msg));
            scrollToBottom();
        } catch (e) {
            console.error('Error loading history:', e);
        }
    }
}

function clearHistory() {
    if (confirm('Are you sure you want to clear all messages?')) {
        messageHistory = [];
        messagesArea.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🧠</div>
                <h3>Welcome to Querify 2.0</h3>
                <p>Ask questions about your data. I'll analyze them using SQL queries or advanced data exploration.</p>
            </div>
        `;
        localStorage.removeItem('querifyHistory');
    }
}

// ===== UTILITY =====

function scrollToBottom() {
    setTimeout(() => {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }, 100);
}
