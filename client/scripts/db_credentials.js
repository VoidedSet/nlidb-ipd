document.getElementById('connect-db').addEventListener('submit', async function (event) {
    event.preventDefault();

    const host = document.getElementById('db-host').value;
    const dbName = document.getElementById('db-name').value;
    const username = document.getElementById('db-user').value;
    const password = document.getElementById('db-password').value;
    const groqApiKey = localStorage.getItem('groqApiKey');

    try {
        const response = await fetch('http://localhost:5000/credentials', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ host, dbName, username, password, groqApiKey }),
        });

        const data = await response.json();
        if (data.success) {
            alert('Database connected successfully. Redirecting to chat...');
            window.location.href = 'chat.html'; // Redirect to chat page
        } else {
            alert('An error occurred while connecting to the database. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while connecting to the database. Please try again.');
    }
});
