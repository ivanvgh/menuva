// ✅ Category tab switching for menu chips
function bindCategoryTabs() {
  const chips = document.querySelectorAll('.chip');
  const tabs = document.querySelectorAll('.category-tab');
  if (!chips.length) return;

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      // deactivate all
      chips.forEach(c => c.classList.remove('active'));
      tabs.forEach(t => t.classList.remove('active'));

      // activate target
      chip.classList.add('active');
      const target = document.getElementById(chip.dataset.tab);
      if (target) target.classList.add('active');

      // scroll to top of menu
      document.querySelector('.menu-container')?.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
}
