const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/catalogue-search.js'), 'utf8');

function element() {
  return {
    value: '', children: [], listeners: {}, attributes: {},
    append(...items) { this.children.push(...items); },
    after(list, status) { this.list = list; this.status = status; },
    get firstChild() { return this.children[0]; },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    addEventListener(name, handler) { this.listeners[name] = handler; },
    dispatchEvent(event) { return this.listeners[event.type]?.(event); },
    replaceChildren() { this.children = []; },
    focus() {}, scrollIntoView() {},
  };
}

function page(fetcher) {
  const input = element(), calls = [];
  const context = vm.createContext({Event,
    document: {querySelectorAll: () => [input], createElement: element},
    fetch(url, options) {
      calls.push({url, options});
      return fetcher ? fetcher() : Promise.resolve({ok: true, json: async () => ({choices: [
        {name: 'Wingstop', kind: 'Restaurant'}, {name: 'Cheese Fries', kind: 'Fries'},
      ]})});
    },
  });
  vm.runInContext(source, context);
  return {input, calls,
    type(value) { input.value = value; return input.listeners.input(); },
    key(key) { input.listeners.keydown({key, preventDefault() {}}); },
  };
}

test('keyboard and pointer choices fill the name; typo/clear never retain an old selection', async () => {
  const p = page();
  await p.type('Wing');
  assert.equal(p.input.attributes['aria-expanded'], 'true');
  p.key('ArrowDown');
  assert.equal(p.input.attributes['aria-activedescendant'], 'catalogue-options-0-0');
  p.key('Enter');
  assert.equal(p.input.value, 'Wingstop');
  assert.equal(p.input.attributes['aria-expanded'], 'false');
  await p.type('wngstop');
  assert.equal(p.input.list.children.length, 0);
  assert.match(p.input.status.textContent, /No matching names/);
  await p.type('Cheese');
  p.input.list.children[0].listeners.click();
  assert.equal(p.input.value, 'Cheese Fries');
  await p.type('');
  assert.equal(p.input.attributes['aria-expanded'], 'false');
  assert.equal(p.input.status.textContent, '');
  assert.equal(p.calls.length, 1);
  assert.equal(p.calls[0].url, '/api/catalogue-choices');
  assert.equal(p.calls[0].options.cache, 'no-store');
});

test('Escape/blur ignore late catalogue responses and ArrowUp selects the last choice', async () => {
  let resolve;
  const p = page(() => new Promise(r => { resolve = r; }));
  const typing = p.type('Wing');
  p.key('Escape');
  resolve({ok: true, json: async () => ({choices: [{name: 'Wingstop', kind: 'Restaurant'}]})});
  await typing;
  assert.equal(p.input.attributes['aria-expanded'], 'false');
  await p.type('Wing');
  p.key('ArrowUp');
  p.key('Enter');
  assert.equal(p.input.value, 'Wingstop');
  p.input.listeners.blur();
  assert.equal(p.input.attributes['aria-expanded'], 'false');
});

test('unavailable suggestions can retry and names are inserted as text', async () => {
  let count = 0;
  const name = '<img src=x onerror=alert(1)>';
  const p = page(async () => ++count === 1 ? {ok: false} : {
    ok: true, json: async () => ({choices: [{name, kind: 'Fries'}]}),
  });
  await p.type('img');
  assert.match(p.input.status.textContent, /unavailable/);
  await p.type('img');
  assert.equal(p.input.list.children[0].firstChild.textContent, name);
  assert.equal(p.input.list.children[0].firstChild.innerHTML, undefined);
});
