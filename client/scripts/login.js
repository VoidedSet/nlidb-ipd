document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('usernameL').value;
    const password = document.getElementById('passwordL').value;

    const loginPanel = document.getElementById('login-form');
    const dbPanel = document.getElementById('connect-db');

    try {
        const response = await fetch('http://localhost:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        if (data.success) {
            // Store the Groq API key in local storage for later use
            localStorage.setItem('groqApiKey', data.groqApiKey);
            alert('Login successful. Redirecting to database credentials page...');
            
            loginPanel.style.display = 'none';
            dbPanel.style.display = 'flex';
            // Redirect to database credentials page
        } else {
            alert('Invalid username or password. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login. Please try again.');
    }
});
