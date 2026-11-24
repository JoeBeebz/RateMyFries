/* Google receives a request only after the visitor chooses to load the map. */
(() => {
  'use strict';
  const root = document.getElementById('restaurant-explorer');
  if (!root) return;
  const items = JSON.parse(document.getElementById('restaurant-map-data').textContent);
  const status = document.getElementById('map-status');
  const select = document.getElementById('map-selection');
  const details = document.getElementById('map-details');
  const load = document.getElementById('load-restaurant-map');
  const canvas = document.getElementById('restaurant-map');
  const located = items.filter(r => Number.isFinite(r.latitude) && Number.isFinite(r.longitude));
  const markers = new Map();
  let map, info, timer, loaded = false;
  const stars = (average, count) => average == null ? 'Not rated yet' : `${average.toFixed(1)} / 5 · ${count} rating${count === 1 ? '' : 's'}`;
  function element(tag, text, parent) {
    const el = document.createElement(tag);
    if (text != null) el.textContent = text;
    if (parent) parent.append(el);
    return el;
  }
  function show(id, fromMarker = false) {
    const r = items.find(item => String(item.id) === String(id));
    details.replaceChildren();
    if (!r) { element('p', 'Select a marker or choose a restaurant to explore its fries.', details); return; }
    select.value = String(r.id);
    element('h3', r.name, details);
    element('p', r.address || 'Address unavailable', details);
    element('p', stars(r.average, r.count), details);
    const link = element('a', 'View restaurant →', details); link.href = r.url;
    element('h4', 'Matching fry options', details);
    const list = element('ul', null, details);
    for (const fry of r.fries) {
      const li = element('li', null, list);
      const a = element('a', fry.name, li); a.href = fry.url;
      element('small', `${fry.price_cents == null ? 'Price unavailable' : '$' + (fry.price_cents / 100).toFixed(2)} · ${stars(fry.average, fry.count)}`, li);
    }
    if (!r.fries.length) element('p', 'No matching fry options yet. Visit the restaurant for more details.', details);
    if (r.latitude == null) element('p', 'Location unavailable — this restaurant has no map marker.', details);
    const marker = markers.get(r.id);
    if (marker && map) {
      map.panTo(marker.position);
      if (!fromMarker) map.setZoom(Math.max(map.getZoom(), 14));
      const content = element('div');
      element('strong', r.name, content);
      const a = element('a', 'View restaurant & fries', content); a.href = r.url;
      info.setContent(content); info.open({map, anchor: marker});
    }
  }
  function failed() {
    clearTimeout(timer);
    status.textContent = 'The map could not load. You can still choose a restaurant and browse all details below.';
    load.disabled = false; load.textContent = 'Retry map'; loaded = false;
  }
  function initialize() {
    try {
      clearTimeout(timer);
      canvas.replaceChildren();
      map = new google.maps.Map(canvas, {center: {lat: located[0].latitude, lng: located[0].longitude}, zoom: 12,
        mapId: 'DEMO_MAP_ID', mapTypeControl: false, streetViewControl: false, gestureHandling: 'cooperative'});
      info = new google.maps.InfoWindow({minWidth: 200, maxWidth: 280});
      const bounds = new google.maps.LatLngBounds();
      markers.clear();
      for (const r of located) {
        const position = {lat: r.latitude, lng: r.longitude};
        const marker = new google.maps.marker.AdvancedMarkerElement({map, position, title: r.name, gmpClickable: true});
        marker.addEventListener('gmp-click', () => show(r.id, true));
        markers.set(r.id, marker); bounds.extend(position);
      }
      if (located.length > 1) map.fitBounds(bounds, 48);
      google.maps.event.addListenerOnce(map, 'idle', () => { if (map.getZoom() > 16) map.setZoom(16); });
      status.textContent = `${located.length} restaurant location${located.length === 1 ? '' : 's'} on the map. ${items.length - located.length} without coordinates remain in the list.`;
      load.textContent = 'Map loaded'; load.disabled = true; loaded = true;
      if (select.value) show(select.value);
    } catch (_) { failed(); }
  }
  select.addEventListener('change', () => show(select.value));
  window.gm_authFailure = failed;
  window.initRestaurantMap = initialize;
  load.addEventListener('click', () => {
    if (loaded) return;
    if (!located.length) { status.textContent = 'No locations are available for these results. Choose a restaurant to see its details, or clear your filters.'; return; }
    if (!root.dataset.mapKey) { status.textContent = 'The interactive map is temporarily unavailable. Choose a restaurant to explore its fries below.'; return; }
    load.disabled = true; status.textContent = 'Loading the neighborhood…';
    if (window.google?.maps?.marker) { initialize(); return; }
    document.getElementById('google-restaurant-map-loader')?.remove();
    const script = document.createElement('script');
    script.id = 'google-restaurant-map-loader'; script.async = true;
    script.nonce = document.querySelector('script[nonce]').nonce;
    const params = new URLSearchParams({key: root.dataset.mapKey, callback: 'initRestaurantMap', loading: 'async', libraries: 'marker', v: 'quarterly', auth_referrer_policy: 'origin'});
    script.src = 'https://maps.googleapis.com/maps/api/js?' + params;
    script.onerror = failed; timer = setTimeout(failed, 15000);
    document.head.append(script);
  });
})();
