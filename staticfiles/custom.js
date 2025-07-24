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
                const btn = form.querySelector('.favorite-btn i');
                if (data.favorited) {
                    btn.className = 'bi bi-heart-fill';
                    form.querySelector('.favorite-btn').classList.remove('btn-outline-warning');
                    form.querySelector('.favorite-btn').classList.add('btn-warning');
                    form.setAttribute('data-favorited', 'true');
                } else {
                    btn.className = 'bi bi-heart';
                    form.querySelector('.favorite-btn').classList.remove('btn-warning');
                    form.querySelector('.favorite-btn').classList.add('btn-outline-warning');
                    form.setAttribute('data-favorited', 'false');
                }
            });
        });
    });
}); 