
        // Micro-interactions and subtle field focus behaviors
        document.querySelectorAll('input, select').forEach(element => {
            element.addEventListener('focus', () => {
                element.parentElement.querySelector('label')?.classList.add('text-primary');
            });
            element.addEventListener('blur', () => {
                element.parentElement.querySelector('label')?.classList.remove('text-primary');
            });
        });

        // Simple Password Toggle Simulation
        const passToggle = document.querySelector('[data-icon="visibility"]').parentElement;
        const passInput = document.getElementById('password');
        passToggle.addEventListener('click', () => {
            const isPass = passInput.type === 'password';
            passInput.type = isPass ? 'text' : 'password';
            passToggle.querySelector('span').innerText = isPass ? 'visibility_off' : 'visibility';
        });


