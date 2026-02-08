const form = document.getElementById('register-form');
const errEl = document.getElementById('register-error');
if (form && errEl) {
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    errEl.hidden = true;
    errEl.textContent = '';

    const username = form.username.value.trim();
    const email = form.email.value.trim() || null;
    const password = form.password.value;
    if (!username || !password) return;

    window.auth.register({ username, password, email })
      .then(function() {
        window.location.href = 'login.html';
      })
      .catch(function(err) {
        errEl.textContent = err.message || 'Registration failed';
        errEl.hidden = false;
      });
  });
}
