document.getElementById('signup-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const groqApiKey = document.getElementById('groq-api-key').value;

    const signupPanel = document.getElementById('signup-form');
    const loginPanel = document.getElementById('login-form');

    try {
        const response = await fetch('http://localhost:5000/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, username, password, groqApiKey }),
        });

        const data = await response.json();
        if (data.success) {
            alert('Account created successfully. Login to continue!');
            
            signupPanel.style.display = 'none';
            loginPanel.style.display = 'flex';

        } else {
            alert('An error occurred during signup. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during signup. Please try again.');
    }
});
