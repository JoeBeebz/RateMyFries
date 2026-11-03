// Keep the core forms usable without JavaScript.
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', event => {
    if (!form.checkValidity()) return;
    const button = event.submitter;
    if (button) {
      button.textContent = form.id === 'discovery-search' || form.method.toLowerCase() === 'get' ? 'Finding fries…' : 'Saving…';
      button.setAttribute('aria-busy', 'true');
    }
  });
});

const csrf = document.querySelector('meta[name="csrf-token"]').content;

function addressSessionToken() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  // randomUUID requires HTTPS; getRandomValues also works on the class LAN site.
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

document.querySelectorAll('[data-address]').forEach((input, inputNumber) => {
  const label = input.labels?.[0]?.textContent.trim();
  if (label) input.setAttribute('aria-label', label);
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
  let sessionToken = addressSessionToken();
  const close = () => {
    list.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
    active = -1;
  };
  const choose = option => {
    input.value = option.textContent;
    sessionToken = addressSessionToken();
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
  let locationVersion = 0;
  const button = document.querySelector('#use-location');
  const clearDevice = () => { search.elements.lat.value = ''; search.elements.lon.value = ''; };
  const cancelLocation = () => {
    ++locationVersion;
    clearDevice();
    button.removeAttribute('aria-busy');
    status.textContent = '';
  };
  const useAddress = () => {
    cancelLocation();
    if (search.elements.use_saved) search.elements.use_saved.checked = false;
  };
  address.addEventListener('input', useAddress);
  address.addEventListener('change', useAddress);
  search.elements.use_saved?.addEventListener('change', () => { cancelLocation(); address.value = ''; });
  button.addEventListener('click', () => {
    const currentVersion = ++locationVersion;
    clearDevice();
    if (!window.isSecureContext) {
      status.textContent = 'Current location needs a secure connection. Enter an address instead, or open the site through HTTPS or localhost.';
      return;
    }
    if (!navigator.geolocation) { status.textContent = 'Device location is unavailable. Enter an address instead.'; return; }
    button.setAttribute('aria-busy', 'true');
    status.textContent = 'Waiting for your location permission…';
    navigator.geolocation.getCurrentPosition(position => {
      if (currentVersion !== locationVersion) return;
      button.removeAttribute('aria-busy');
      address.value = '';
      if (search.elements.use_saved) search.elements.use_saved.checked = false;
      search.elements.lat.value = position.coords.latitude;
      search.elements.lon.value = position.coords.longitude;
      if (!search.elements.radius.value) search.elements.radius.value = '10';
      status.textContent = 'Current location is ready. Select Find fries to search nearby.';
    }, () => {
      if (currentVersion !== locationVersion) return;
      button.removeAttribute('aria-busy');
      clearDevice();
      status.textContent = 'We could not access your location. Enter an address or use your saved profile address.';
    }, {timeout: 10000, maximumAge: 60000});
  });
}
