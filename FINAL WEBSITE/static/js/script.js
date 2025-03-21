// Smooth Scroll to Sections
function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({ behavior: "smooth" });
}

// Registration Form Submission
document.getElementById("registration-form").addEventListener("submit", function(event) {
    event.preventDefault();
    document.getElementById("registration-form").reset();
    document.getElementById("success-message").classList.remove("hidden");
});

    document.getElementById('registration-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        
        const formData = {
            name: document.getElementById('name').value,
            'email': document.getElementById('email').value,
            'address': document.getElementById('address').value,
            'phone': document.getElementById('phone').value,
            'method': document.getElementById('method').value
        };

        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById('success-message').classList.remove('hidden');
            }
        })
        .catch(error => console.error('Error:', error));
    });
