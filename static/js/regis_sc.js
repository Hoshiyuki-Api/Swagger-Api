document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var form = this;
    var formData = new FormData(form);
    
    fetch('/auth/register', {
        method: 'POST',
        body: formData
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            document.getElementById('message').innerHTML = '<div id="error">' + data.error + '</div>';
        } else {
            document.getElementById('message').innerHTML = '<div id="success">' + data.message + '</div>';
            form.reset();
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
});