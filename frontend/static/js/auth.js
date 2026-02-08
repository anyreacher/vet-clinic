
const API_BASE = ''; 

function getToken() {
  return localStorage.getItem('access_token');
}

function setToken(token) {
  if (token) localStorage.setItem('access_token', token);
  else localStorage.removeItem('access_token');
}

function fetchApi(path, options) {
  options = options || {};
  options.credentials = 'same-origin';
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;
  if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  options.headers = headers;
  return fetch(API_BASE + path, options).then(function(res) {
    if (res.status === 401 && path !== '/auth/token' && path !== '/auth/refresh') {
      return res.json().catch(function() { return {}; }).then(function(body) {
        return refreshToken().then(function() {
          return fetchApi(path, options);
        }).catch(function() {
          setToken(null);
          const err = new Error(body.detail || 'Session expired');
          err.status = 401;
          throw err;
        });
      });
    }
    if (!res.ok) {
      return res.json().catch(function() { return { detail: res.statusText }; }).then(function(body) {
        const err = new Error(body.detail || 'Request failed');
        err.status = res.status;
        throw err;
      });
    }
    return res.json ? res.json() : res;
  });
}

function refreshToken() {
  return fetch(API_BASE + '/auth/refresh', { method: 'POST', credentials: 'same-origin' })
    .then(function(res) {
      if (!res.ok) throw new Error('Refresh failed');
      return res.json();
    })
    .then(function(data) {
      if (data.access_token) setToken(data.access_token);
      return data;
    });
}

function register(body) {
  return fetchApi('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      username: body.username,
      password: body.password,
      email: body.email || null
    })
  });
}

function login(username, password) {
  const form = new FormData();
  form.append('username', username);
  form.append('password', password);
  return fetch(API_BASE + '/auth/token', {
    method: 'POST',
    credentials: 'same-origin',
    body: form
  }).then(function(res) {
    if (!res.ok) {
      return res.json().catch(function() { return {}; }).then(function(body) {
        const err = new Error(body.detail || 'Login failed');
        err.status = res.status;
        throw err;
      });
    }
    return res.json();
  });
}

function logout() {
  fetch(API_BASE + '/auth/logout', { method: 'POST', credentials: 'same-origin' }).catch(function() {});
  setToken(null);
  window.location.href = 'login.html';
}

window.auth = {
  getToken,
  setToken,
  register,
  login,
  logout,
  fetchApi,
  refreshToken
};
