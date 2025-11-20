document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signUpForm');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const errorDiv = document.getElementById('password-match-error');

    form.addEventListener('submit', function(event) {
        // Очищаємо попередні помилки
        errorDiv.classList.add('hidden');
        
        if (password.value.length < 6) {
            alert('Password must be at least 6 characters long.');
            event.preventDefault();
            return;
        }

        if (password.value !== confirmPassword.value) {
            errorDiv.classList.remove('hidden');
            event.preventDefault(); // Зупиняємо відправку форми
            // Додатково можна очистити поля паролів
            password.value = '';
            confirmPassword.value = '';
            password.focus();
        }
    });
});