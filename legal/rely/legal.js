// Mobile navigation uses the same homepage menu, without loading product or login scripts.
const toggle = document.getElementById('navToggle');
const links = document.getElementById('navLinks');
function setMenu(open) {
  links.classList.toggle('open', open);
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? '收起菜单' : '展开菜单');
}
if (toggle && links) {
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  links.addEventListener('click', (event) => { if (event.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      toggle.focus();
    }
  });
  window.matchMedia('(min-width: 841px)').addEventListener('change', () => setMenu(false));
}
