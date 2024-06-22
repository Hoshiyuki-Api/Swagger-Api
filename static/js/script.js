document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting

        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        // Send a POST request to the server with username and password
        fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'username=' + encodeURIComponent(username) + '&password=' + encodeURIComponent(password)
        })
        .then(response => {
            if (response.ok) {
                // Redirect to dashboard.html after successful login
                window.location.href = '/dashboard';
            } else if (response.status === 403) {
                // Apikey Expired, display error message
                document.getElementById('login-message').innerText = 'Apikey Telah Expired';
            } else {
                // Login failed, display error message
                document.getElementById('login-message').innerText = 'Login Gagal';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});