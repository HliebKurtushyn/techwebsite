document.getElementById('signUpForm').addEventListener('submit', function(event) {
    const password = document.getElementById('password');
    const passwordConfirm = document.getElementById('confirmPassword');

    if (password.value !== passwordConfirm.value) {
        event.preventDefault();
        alert('Passwords do not match!');
    }
});