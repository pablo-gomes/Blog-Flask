function togglePasswordVisibility(iconElement) {
    const passwordInput = document.getElementById('senha');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        iconElement.textContent = '🔐';
    } else {
        passwordInput.type = 'password';
        iconElement.textContent = '🔒';
    }
}
