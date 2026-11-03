from pathlib import Path
import sys, shutil, json, tempfile, argparse

source = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(source), str(source / 'tests')]
from app import create_app, db, one
from test_app import register, listing, rate, post, make_admin

parser = argparse.ArgumentParser(description='Prepare isolated static pages for browser layout checks.')
parser.add_argument('--output', required=True, type=Path, help='New directory for the layout harness')
out = parser.parse_args().output.resolve()
out.mkdir(parents=True, exist_ok=False)
fixture = tempfile.TemporaryDirectory(prefix='fry-layout-fixture-')
shutil.copytree(source / 'static', out / 'static', dirs_exist_ok=True)
application = create_app({'TESTING': True, 'SECRET_KEY': 'layout-fixture-only', 'DATABASE': str(Path(fixture.name) / 'fixture.sqlite3')})
client = application.test_client()
pages = {}

def capture(name, path, response=None):
    response = response or client.get(path)
    assert response.status_code in (200, 400), (name, response.status_code)
    html = response.data.decode().replace('/static/', 'static/')
    (out / (name + '.html')).write_text(html, encoding='utf8')
    pages[name] = path

for name, path in [('login','/login'), ('register','/register'), ('privacy','/privacy')]: capture(name,path)
register(client, 'layout_demo')
rid, fid = listing(client, name='Layout Demo Diner', address='123 Example Avenue, Kenosha, WI')
rate(client, fid, body='Demonstration review: crisp and well seasoned. ' + 'LongReviewWord' * 30,
     crispiness='4', seasoning='5', texture='4', freshness='4', portion='3', value='4', sauce='5', context='takeout')
for name, path in [('home','/'), ('search','/search'), ('restaurant',f'/restaurants/{rid}'),
                   ('fry',f'/fries/{fid}'), ('profile','/profile'), ('business','/business-requests/new'),
                   ('add-restaurant','/restaurants/new'), ('add-fries',f'/restaurants/{rid}/fries/new'),
                   ('admin-accounts','/admin/accounts'), ('delete-account','/account/delete')]: capture(name,path)
review_id = None
with application.app_context(): review_id = one('SELECT id FROM reviews')['id']
capture('delete-review',f'/reviews/{review_id}/delete')
post(client,'/business-requests/new',{'name':'Demonstration Business','address':'456 Example Road','description':'Test request for layout acceptance only.'})
capture('requests','/business-requests')
capture('admin-inbox','/admin/inbox')
capture('validation','/restaurants/new',post(client,'/restaurants/new',{'name':'','address':''}))
(out/'api').mkdir(exist_ok=True)
(out/'api/catalogue-choices').write_text(json.dumps({'choices':[{'name':'Waffle fries','kind':'Fries'}]}))

links=' '.join(f'<a href="?page={name}">{name}</a>' for name in pages)
script='''
const names = PAGES;
const chosen = new URLSearchParams(location.search).get('page') || 'search';
const results = [];
for (const name of names) for (const width of [390, 1280]) {
  const frame = document.createElement('iframe');
  frame.title = name + ' at ' + width + ' pixels';
  frame.width = width; frame.height = 844;
  if (name !== chosen) frame.style.cssText = 'position:absolute;left:-10000px;top:0';
  frame.onload = () => {
    const doc = frame.contentDocument, available = doc.documentElement.clientWidth;
    const overflowing = [...doc.querySelectorAll('main *, nav *, footer *')].filter(el => {
      const r = el.getBoundingClientRect();
      return r.width && (r.right > available + 1 || r.left < -1) && !el.matches('.skip,.sr-only,[type=hidden]');
    }).map(el => ({tag:el.tagName, text:el.textContent.trim().slice(0,50), class:el.className}));
    results.push({name,width,available,scrollWidth:doc.documentElement.scrollWidth,overflowing:overflowing.slice(0,12)});
    document.querySelector('#results').textContent = JSON.stringify(results,null,2);
    document.querySelector('#summary').textContent = results.length + '/' + names.length*2 + ' layouts checked; ' + results.filter(r => r.scrollWidth > r.available || r.overflowing.length).length + ' need inspection';
  };
  frame.src = name + '.html'; document.querySelector('#frames').append(frame);
}
'''.replace('PAGES',json.dumps(list(pages)))
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Fry UI acceptance at 390px and desktop</title><style>body{font:14px system-ui;background:#ddd}nav{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:16px}iframe{border:1px solid #555;background:white;margin-right:20px}#frames{display:flex;align-items:start}#results{white-space:pre-wrap}</style><h1>Fry UI acceptance — 390px and 1280px</h1><p>Isolated demonstration fixtures; no live accounts or reviews are modified.</p><nav>'+links+'</nav><p id="summary">Checking layouts…</p><div id="frames"></div><details><summary>Layout measurements</summary><pre id="results"></pre></details><script>'+script+'</script>',encoding='utf8')
fixture.cleanup()
print(f'Prepared {len(pages)} pages at two viewport widths in {out}')
