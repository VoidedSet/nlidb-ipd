// Open the dialog when clicking on the user icon
document.getElementById('user-icon').addEventListener('click', openDialog);

function openDialog() {
  document.getElementById('dialog-overlay').style.display = 'flex';
}

function closeDialog() {
  document.getElementById('dialog-overlay').style.display = 'none';
}

// FIX: Changed the form ID to match chat.html ('connect-db')
document.getElementById('connect-db').addEventListener('submit', function(event) {
  event.preventDefault();

  const host = document.getElementById('db-host').value;
  const dbName = document.getElementById('db-name').value;
  const username = document.getElementById('db-user').value;
  const password = document.getElementById('db-password').value;

  fetch('http://localhost:5000/credentials', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    // FIX: Removed the groqApiKey as it's handled by the backend
    body: JSON.stringify({host, dbName, username, password}),
  })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          alert('Database connected successfully.');
          closeDialog();
        } else {
          alert('Failed to connect to the database. Please check credentials.');
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while saving credentials.');
      });
});

// A simple logout function example
function logout() {
  alert('Logged out!');
  // Here you would typically clear session data and redirect
  closeDialog();
}
