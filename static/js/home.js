const nav = document.querySelector('nav');

const observer = new ResizeObserver(entries => {
  const height = entries[0].contentRect.height;
  document.documentElement.style.setProperty('--nav-height', `${height}px`);
});

observer.observe(nav);