const nav = document.getElementById('nav');
const guestMessage = document.getElementById('guest-message');
const userGreeting = document.getElementById('user-greeting');
const userGreetingText = document.getElementById('user-greeting-text');

if (nav) {
  function link(href, text) {
    const a = document.createElement('a');
    a.setAttribute('href', href);
    a.textContent = text;
    return a;
  }

  nav.replaceChildren();

  if (window.auth && window.auth.getToken()) {
    const logoutLink = link('login.html', 'Log out');
    logoutLink.addEventListener('click', function(e) {
      e.preventDefault();
      window.auth.logout();
    });
    nav.appendChild(logoutLink);
  } else {
    nav.appendChild(link('login.html', 'Log in'));
    nav.appendChild(document.createTextNode(' · '));
    nav.appendChild(link('register.html', 'Register'));
  }
}

if (guestMessage && userGreeting && userGreetingText) {
  if (window.auth && window.auth.getToken()) {
    guestMessage.hidden = true;
    window.auth.fetchApi('/auth/me')
      .then(function(user) {
        userGreetingText.textContent = 'Здравствуйте, ' + user.username + '!';
        userGreeting.hidden = false;
      })
      .catch(function() {
        userGreetingText.textContent = 'Здравствуйте!';
        userGreeting.hidden = false;
      });
  } else {
    guestMessage.hidden = false;
    userGreeting.hidden = true;
  }
}
