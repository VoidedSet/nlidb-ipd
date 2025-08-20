

// Example: Open the dialog when clicking on the user icon
document.getElementById('user-icon').addEventListener('click', openDialog);

function openDialog() {
    document.getElementById('dialog-overlay').style.display = 'flex';
}

function closeDialog() {
    document.getElementById('dialog-overlay').style.display = 'none';
}

// Example: Open the dialog when clicking on the user icon
document.getElementById('user-icon').addEventListener('click', openDialog);

document.getElementById('credentials-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const host = document.getElementById('db-host').value;
    const dbName = document.getElementById('db-name').value;
    const username = document.getElementById('db-user').value;
    const password = document.getElementById('db-password').value;
    const groqApiKey = document.getElementById('groq-api-key').value;

    fetch('http://localhost:5000/credentials', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            host,
            dbName,
            username,
            password,
            groqApiKey
        }),
    })
    .then(response => response.json())
    .then(data => {
        alert('Credentials saved successfully.');
        closeDialog();
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while saving credentials.');
    });
});
