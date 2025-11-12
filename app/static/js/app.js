const panels = {
  login: document.getElementById('login-panel'),
  register: document.getElementById('register-panel'),
  home: document.getElementById('home-panel'),
};

const navButtons = {
  login: document.getElementById('nav-login'),
  register: document.getElementById('nav-register'),
  home: document.getElementById('nav-home'),
  logout: document.getElementById('nav-logout'),
};

const statusPanel = document.getElementById('status-panel');
const dashboardGrid = document.getElementById('dashboard-grid');
const homeGreeting = document.getElementById('home-greeting');
const homeSubtitle = document.getElementById('home-subtitle');

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const homeLogout = document.getElementById('home-logout');

function toggleHidden(element, shouldHide) {
  element.classList.toggle('hidden', shouldHide);
}

function showPanel(panelName) {
  Object.entries(panels).forEach(([name, element]) => {
    toggleHidden(element, name !== panelName);
  });

  const isAuthenticated = panelName === 'home';
  toggleHidden(navButtons.login, isAuthenticated);
  toggleHidden(navButtons.register, isAuthenticated);
  toggleHidden(navButtons.home, !isAuthenticated);
  toggleHidden(navButtons.logout, !isAuthenticated);
}

function showStatus(message, tone = 'info') {
  if (!message) {
    statusPanel.textContent = '';
    toggleHidden(statusPanel, true);
    return;
  }

  statusPanel.textContent = message;
  statusPanel.dataset.tone = tone;
  toggleHidden(statusPanel, false);
}

async function apiFetch(endpoint, options = {}) {
  const response = await fetch(`/api${endpoint}`, {
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch (err) {
    // Ignore JSON parsing errors and keep payload as null
  }

  if (!response.ok) {
    const errorMessage = payload?.error || '요청을 처리하지 못했습니다.';
    throw new Error(errorMessage);
  }

  return payload;
}

function renderDashboard(dashboard) {
  dashboardGrid.innerHTML = '';
  if (!Array.isArray(dashboard) || dashboard.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'muted';
    empty.textContent = '표시할 대시보드 정보가 없습니다.';
    dashboardGrid.appendChild(empty);
    return;
  }

  dashboard.forEach((card) => {
    const panel = document.createElement('article');
    panel.className = 'panel';

    const icon = document.createElement('div');
    icon.className = 'panel-icon';
    icon.textContent = card.icon || 'ℹ️';

    const title = document.createElement('h2');
    title.textContent = card.title;

    const description = document.createElement('p');
    description.className = 'muted';
    description.textContent = card.description;

    panel.appendChild(icon);
    panel.appendChild(title);
    panel.appendChild(description);
    dashboardGrid.appendChild(panel);
  });
}

async function loadHome() {
  try {
    const data = await apiFetch('/home', { method: 'GET' });
    const { user, dashboard } = data;
    const displayName = user?.name || user?.username || '사용자';
    homeGreeting.textContent = `${displayName}님, 환영합니다!`;
    homeSubtitle.textContent = '방문자 응대를 위한 최신 정보를 확인하세요.';
    renderDashboard(dashboard);
    showPanel('home');
    showStatus('메인 화면으로 이동했습니다.', 'success');
  } catch (error) {
    showStatus(error.message, 'error');
    showPanel('login');
  }
}

async function checkSession() {
  try {
    const data = await apiFetch('/session', { method: 'GET' });
    if (data.authenticated) {
      await loadHome();
    } else {
      showPanel('login');
    }
  } catch (error) {
    showStatus(error.message, 'error');
    showPanel('login');
  }
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  showStatus('로그인 중입니다...', 'info');

  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    await apiFetch('/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    loginForm.reset();
    await loadHome();
    showStatus('성공적으로 로그인했습니다.', 'success');
  } catch (error) {
    showStatus(error.message, 'error');
  }
});

registerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  showStatus('회원가입을 진행 중입니다...', 'info');

  const formData = new FormData(registerForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    await apiFetch('/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    registerForm.reset();
    showStatus('회원가입이 완료되었습니다. 로그인해주세요.', 'success');
    showPanel('login');
  } catch (error) {
    showStatus(error.message, 'error');
  }
});

navButtons.login.addEventListener('click', () => {
  showStatus('로그인을 진행해주세요.', 'info');
  showPanel('login');
});

navButtons.register.addEventListener('click', () => {
  showStatus('아이디와 이메일을 포함한 회원가입 정보를 입력해주세요.', 'info');
  showPanel('register');
});

navButtons.home.addEventListener('click', () => {
  loadHome();
});

async function logout() {
  try {
    await apiFetch('/logout', { method: 'POST' });
  } catch (error) {
    // Even if logout fails, continue to clear UI state
    console.warn(error);
  }
  showStatus('로그아웃되었습니다.', 'info');
  showPanel('login');
}

navButtons.logout.addEventListener('click', logout);
homeLogout.addEventListener('click', logout);

document.querySelectorAll('.form-helper .link-button').forEach((button) => {
  button.addEventListener('click', () => {
    const target = button.dataset.target;
    showPanel(target);
  });
});

checkSession();
