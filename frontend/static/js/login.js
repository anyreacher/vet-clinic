const form = document.getElementById('login-form');
const errEl = document.getElementById('login-error');
if (form && errEl) {
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    errEl.hidden = true;
    errEl.textContent = '';

    const username = form.username.value.trim();
    const password = form.password.value;
    if (!username || !password) return;

    window.auth.login(username, password)
      .then(function(data) {
        window.auth.setToken(data.access_token);
        window.location.href = 'index.html';
      })
      .catch(function(err) {
        errEl.textContent = err.message || 'Login failed';
        errEl.hidden = false;
      });
  });
}
