document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.favorite-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const btn = form.querySelector('.favorite-btn');
                const icon = btn.querySelector('i');
                if (data.favorited) {
                    icon.className = 'bi bi-heart-fill';
                    btn.classList.remove('btn-outline-warning');
                    btn.classList.add('btn-warning');
                    form.setAttribute('data-favorited', 'true');
                } else {
                    icon.className = 'bi bi-heart';
                    btn.classList.remove('btn-warning');
                    btn.classList.add('btn-outline-warning');
                    form.setAttribute('data-favorited', 'false');
                    // If on favorites page, remove the card from DOM
                    const card = form.closest('.col-md-4');
                    if (card && window.location.pathname.includes('favorites')) {
                        card.remove();
                    }
                }
                // Always keep the color yellow
                btn.style.color = '#ffc107';
                btn.style.borderColor = '#ffc107';
            });
        });
    });
}); 