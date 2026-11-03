// Catalogue suggestions are separate from Google's address autocomplete.
// Fetch the current public names once per page, then filter locally.
(() => {
  let catalogue;
  const normalize = value => value.normalize('NFKC').toLowerCase().trim().replace(/\s+/g, ' ');
  const load = () => {
    if (!catalogue) {
      catalogue = fetch('/api/catalogue-choices', {cache: 'no-store'})
        .then(response => {
          if (!response.ok) throw new Error('Suggestions are unavailable. Enter a complete listed name.');
          return response.json();
        })
        .then(data => data.choices)
        .catch(error => { catalogue = undefined; throw error; });
    }
    return catalogue;
  };

  document.querySelectorAll('[data-catalogue-search]').forEach((input, number) => {
    const list = document.createElement('ul');
    list.className = 'catalogue-options';
    list.id = `catalogue-options-${number}`;
    list.setAttribute('role', 'listbox');
    list.setAttribute('aria-label', 'Listed restaurants, fries and styles');
    list.hidden = true;
    const status = document.createElement('p');
    status.className = 'catalogue-status';
    status.id = `catalogue-status-${number}`;
    status.setAttribute('role', 'status');
    input.after(list, status);
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-controls', list.id);
    input.setAttribute('aria-describedby', status.id);
    input.setAttribute('aria-expanded', 'false');
    let active = -1, version = 0;
    const close = () => {
      list.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
      active = -1;
    };
    const choose = choice => {
      ++version;
      input.value = choice.name;
      input.dispatchEvent(new Event('change', {bubbles: true}));
      close();
      status.textContent = '';
      input.focus();
    };
    input.addEventListener('input', async () => {
      const current = ++version;
      close();
      status.textContent = '';
      const query = normalize(input.value);
      if (!query) return;
      try {
        const choices = await load();
        if (current !== version) return;
        const matches = choices.filter(choice => normalize(choice.name).includes(query))
          .sort((a, b) => Number(!normalize(a.name).startsWith(query)) - Number(!normalize(b.name).startsWith(query)))
          .slice(0, 8);
        list.replaceChildren();
        matches.forEach((choice, index) => {
          const option = document.createElement('li');
          option.id = `${list.id}-${index}`;
          option.setAttribute('role', 'option');
          option.setAttribute('aria-selected', 'false');
          const name = document.createElement('span');
          name.textContent = choice.name;
          const kind = document.createElement('small');
          kind.textContent = choice.kind;
          option.append(name, kind);
          option.addEventListener('mousedown', event => event.preventDefault());
          option.addEventListener('click', () => choose(choice));
          list.append(option);
        });
        list.hidden = !matches.length;
        input.setAttribute('aria-expanded', String(!list.hidden));
        status.textContent = matches.length ? '' : 'No matching names. Choose something listed on the site.';
      } catch (error) {
        if (current === version) status.textContent = 'Suggestions are unavailable. Enter a complete listed name.';
      }
    });
    input.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        ++version;
        close();
        status.textContent = '';
      }
      if (list.hidden) return;
      const options = [...list.children];
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        active = active < 0 ? (event.key === 'ArrowDown' ? 0 : options.length - 1)
          : (active + (event.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
        options.forEach((option, index) => option.setAttribute('aria-selected', String(index === active)));
        input.setAttribute('aria-activedescendant', options[active].id);
        options[active].scrollIntoView({block: 'nearest'});
      }
      if (event.key === 'Enter' && active >= 0) {
        event.preventDefault();
        // Names are plain text, separate from the type label in the option.
        choose({name: options[active].firstChild.textContent});
      }
    });
    input.addEventListener('blur', () => { ++version; close(); });
  });
})();
