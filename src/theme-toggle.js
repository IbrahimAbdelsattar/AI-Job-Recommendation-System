document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  const toggles = document.querySelectorAll('.theme-toggle');

  if (!toggles.length) {
    return;
  }

  const setTheme = (theme) => {
    const isDark = theme === 'dark';
    body.classList.toggle('dark-mode', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  };

  const storedTheme = localStorage.getItem('theme');
  if (storedTheme === 'dark') {
    setTheme('dark');
  }

  toggles.forEach((toggle) => {
    toggle.addEventListener('click', () => {
      const newTheme = body.classList.contains('dark-mode') ? 'light' : 'dark';
      setTheme(newTheme);
    });
  });
});

