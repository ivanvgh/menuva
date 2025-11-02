// 💬 Chat auto-scroll and input behavior
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chat-input');
  const form = document.getElementById('chat-form');
  const chatBox = document.getElementById('chat-box');

  if (!input || !form || !chatBox) return;

  // Submit with Enter key
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
  });

  // Auto-scroll on new message
  document.body.addEventListener('htmx:afterSwap', (evt) => {
    if (evt.detail.target.id === 'chat-box') {
      chatBox.scrollTop = chatBox.scrollHeight;
      input.value = '';
      input.focus();
    }
  });
});
