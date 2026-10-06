// The core app works without JavaScript. Only add submission feedback here.
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', event => {
    if (!form.checkValidity()) return;
    const button = event.submitter;
    if (button) {
      // Do not disable the submitter: its name/value identifies review vs rating.
      button.textContent = form.method.toLowerCase() === 'post' ? 'Saving…' : 'Finding fries…';
      button.setAttribute('aria-busy', 'true');
    }
  });
});
