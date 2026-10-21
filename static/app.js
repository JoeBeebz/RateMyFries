// Keep the core forms usable without JavaScript.
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', event => {
    if (!form.checkValidity()) return;
    const button = event.submitter;
    if (button) {
      button.textContent = form.method.toLowerCase() === 'post' ? 'Saving…' : 'Finding fries…';
      button.setAttribute('aria-busy', 'true');
    }
  });
});

const csrf = document.querySelector('meta[name="csrf-token"]').content;
document.querySelectorAll('[data-address]').forEach((input, inputNumber) => {
  const wrapper = document.createElement('div');
  wrapper.className = 'address-suggestions';
  const list = document.createElement('ul');
  list.id = `address-suggestions-${inputNumber}`;
  list.setAttribute('role', 'listbox');
  list.hidden = true;
  const status = document.createElement('p');
  status.className = 'muted suggestion-status';
  status.id = `address-status-${inputNumber}`;
  status.setAttribute('role', 'status');
  wrapper.append(list, status);
  input.after(wrapper);
  input.setAttribute('role', 'combobox');
  input.setAttribute('aria-autocomplete', 'list');
  input.setAttribute('aria-controls', list.id);
  input.setAttribute('aria-describedby', status.id);
  input.setAttribute('aria-expanded', 'false');
  input.setAttribute('autocomplete', 'off');
  let timer, controller, version = 0, active = -1;
  let sessionToken = crypto.randomUUID();
  const close = () => {
    list.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
    active = -1;
  };
  const choose = option => {
    input.value = option.textContent;
    sessionToken = crypto.randomUUID();
    input.dispatchEvent(new Event('change', {bubbles: true}));
    close();
    status.textContent = 'Address selected.';
  };
  input.addEventListener('input', () => {
    clearTimeout(timer);
    controller?.abort();
    const currentVersion = ++version;
    close();
    status.textContent = '';
    if (input.value.trim().length < 3) return;
    timer = setTimeout(async () => {
      controller = new AbortController();
      status.textContent = 'Finding addresses…';
      try {
        const body = new URLSearchParams({input: input.value.trim(), token: sessionToken, csrf});
        const response = await fetch('/api/address-suggestions', {method: 'POST', body, signal: controller.signal});
        const data = await response.json();
        if (currentVersion !== version) return;
        if (!response.ok) throw new Error(data.error || 'Address suggestions are unavailable. Enter your address manually.');
        list.replaceChildren();
        data.suggestions.forEach((text, index) => {
          const option = document.createElement('li');
          option.id = `${list.id}-${index}`;
          option.setAttribute('role', 'option');
          option.setAttribute('aria-selected', 'false');
          option.textContent = text;
          option.addEventListener('mousedown', event => event.preventDefault());
          option.addEventListener('click', () => choose(option));
          list.append(option);
        });
        list.hidden = !list.children.length;
        input.setAttribute('aria-expanded', String(!list.hidden));
        status.textContent = list.hidden ? 'No suggestions. You can enter an address manually.' : `${list.children.length} suggestions. Use arrow keys and Enter. Addresses by Google Maps.`;
      } catch (error) {
        if (error.name !== 'AbortError' && currentVersion === version) status.textContent = error.message;
      }
    }, 350);
  });
  input.addEventListener('keydown', event => {
    if (event.key === 'Escape') { ++version; controller?.abort(); clearTimeout(timer); close(); }
    if (list.hidden) return;
    const options = [...list.children];
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      active = (active + (event.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
      options.forEach((option, index) => option.setAttribute('aria-selected', String(index === active)));
      input.setAttribute('aria-activedescendant', options[active].id);
    }
    if (event.key === 'Enter' && active >= 0) { event.preventDefault(); choose(options[active]); }
  });
  input.addEventListener('blur', () => { ++version; clearTimeout(timer); controller?.abort(); close(); });
});

const search = document.querySelector('#discovery-search');
if (search) {
  const status = document.querySelector('#location-status');
  const address = search.elements.address;
  const clearDevice = () => { search.elements.lat.value = ''; search.elements.lon.value = ''; };
  address.addEventListener('input', () => { clearDevice(); if (search.elements.use_saved) search.elements.use_saved.checked = false; });
  search.elements.use_saved?.addEventListener('change', () => { clearDevice(); address.value = ''; });
  document.querySelector('#use-location').addEventListener('click', () => {
    if (!navigator.geolocation) { status.textContent = 'Device location is unavailable. Enter an address instead.'; return; }
    status.textContent = 'Waiting for your location permission…';
    navigator.geolocation.getCurrentPosition(position => {
      address.value = '';
      if (search.elements.use_saved) search.elements.use_saved.checked = false;
      search.elements.lat.value = position.coords.latitude;
      search.elements.lon.value = position.coords.longitude;
      if (!search.elements.radius.value) search.elements.radius.value = '10';
      status.textContent = 'Current location is ready. Select Find fries to search nearby.';
    }, () => { clearDevice(); status.textContent = 'We could not access your location. Enter an address or use your saved profile address.'; }, {timeout: 10000, maximumAge: 60000});
  });
}
