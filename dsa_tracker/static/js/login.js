function togglePassword() {
            const passInput = document.getElementById('password');
            const toggleIcon = document.getElementById('pass-toggle-icon');

            if (passInput.type === 'password') {
                passInput.type = 'text';
                toggleIcon.textContent = 'visibility_off';
            } else {
                passInput.type = 'password';
                toggleIcon.textContent = 'visibility';
            }
        }

        // Simple enter animation for page elements
        document.addEventListener("DOMContentLoaded", () => {

    const alerts =
        document.querySelectorAll(
            ".flash-message"
        );

    alerts.forEach(alert => {

        setTimeout(() => {

            alert.style.transition =
                "opacity 0.5s ease";

            alert.style.opacity = "0";

            setTimeout(() => {
                alert.remove();
            }, 500);

        }, 3000);

    });

});