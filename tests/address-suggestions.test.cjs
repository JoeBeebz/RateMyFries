const assert = require('node:assert/strict');
const {webcrypto} = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../static/app.js'), 'utf8');
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

function element() {
  return {
    value: '', content: 'csrf-test', children: [], listeners: {}, attributes: {},
    append(...items) { this.children.push(...items); },
    after(wrapper) { this.wrapper = wrapper; },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    addEventListener(name, handler) {
      const previous = this.listeners[name];
      this.listeners[name] = event => { previous?.(event); return handler(event); };
    },
    dispatchEvent(event) { this.listeners[event.type]?.(event); },
    replaceChildren() { this.children = []; },
  };
}

function load({secure = false, geolocation} = {}) {
  const inputs = [element(), element()];
  inputs[0].labels = [{textContent: 'Near address (optional)'}];
  inputs[1].labels = [{textContent: 'Business address'}];
  const locationButton = element(), status = element();
  const search = {elements: {address: inputs[0], lat: element(), lon: element(), radius: element()}};
  const timers = new Map(), requests = [];
  let timerId = 0;
  const context = vm.createContext({
    crypto: secure ? webcrypto : {getRandomValues: webcrypto.getRandomValues.bind(webcrypto)},
    Uint8Array, URLSearchParams, AbortController, Event,
    navigator: {geolocation},
    document: {
      querySelectorAll(selector) { return selector === '[data-address]' ? inputs : []; },
      querySelector(selector) {
        if (selector === '#discovery-search') return search;
        if (selector === '#location-status') return status;
        if (selector === '#use-location') return locationButton;
        return element();
      },
      createElement: element,
    },
    setTimeout(callback) { timers.set(++timerId, callback); return timerId; },
    clearTimeout(id) { timers.delete(id); },
    async fetch(url, options) {
      requests.push({url, body: options.body});
      return {ok: true, async json() { return {suggestions: ['123 Main Street, Kenosha, WI']}; }};
    },
  });
  vm.runInContext(source, context);
  return {inputs, locationButton, status, requests, context,
    async type(input, text) {
      input.value = text;
      input.listeners.input();
      for (const [id, callback] of [...timers]) { timers.delete(id); await callback(); }
    },
  };
}

for (const secure of [false, true]) {
  test(`autocomplete initializes, selects by keyboard and rotates tokens on ${secure ? 'HTTPS' : 'LAN HTTP'}`, async () => {
    const page = load({secure});
    const [input, secondInput] = page.inputs;
    await page.type(input, '12');
    assert.equal(page.requests.length, 0);
    await page.type(input, '123');
    assert.equal(page.requests[0].url, '/api/address-suggestions');
    assert.equal(page.requests[0].body.get('csrf'), 'csrf-test');
    const firstToken = page.requests[0].body.get('token');
    assert.match(firstToken, uuid);
    assert.equal(input.attributes['aria-expanded'], 'true');
    assert.equal(input.attributes['aria-label'], 'Near address (optional)');
    assert.equal(input.wrapper.children[1].textContent, '1 suggestions. Use arrow keys and Enter. Addresses by Google Maps.');
    const key = name => input.listeners.keydown({key: name, preventDefault() {}});
    key('ArrowDown');
    assert.equal(input.attributes['aria-activedescendant'], 'address-suggestions-0-0');
    key('Enter');
    assert.equal(input.value, '123 Main Street, Kenosha, WI');
    assert.equal(input.attributes['aria-expanded'], 'false');
    assert.equal(input.wrapper.children[1].textContent, 'Address selected.');
    await page.type(input, '456');
    const nextToken = page.requests[1].body.get('token');
    assert.match(nextToken, uuid);
    assert.notEqual(nextToken, firstToken);
    await page.type(secondInput, '789');
    assert.notEqual(page.requests[2].body.get('token'), nextToken);
  });
}

test('LAN HTTP still registers location fallback when randomUUID is unavailable', () => {
  const page = load();
  page.locationButton.listeners.click();
  assert.equal(page.status.textContent, 'Device location is unavailable. Enter an address instead.');
});

test('denied location clears coordinates and keeps address fallback usable', async () => {
  const page = load({geolocation: {getCurrentPosition(success, failure) { failure(); }}});
  page.locationButton.listeners.click();
  assert.match(page.status.textContent, /Enter an address/);
  await page.type(page.inputs[0], 'Kenosha');
  assert.equal(page.requests.length, 1);
});
