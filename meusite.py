# Create a complete runnable MVP as a single-file Flask app + templates in ./app_mvp
# It reads a site definition JSON, provides a simple web editor UI, preview, and static export.

import os, json, textwrap

base_dir = './app_mvp'
templates_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

app_py = r'''
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os
import json
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, 'data')
EXPORTS_DIR = os.path.join(APP_DIR, 'exports')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

SITE_JSON_PATH = os.path.join(DATA_DIR, 'site.json')

DEFAULT_SITE = {
  "meta": {
    "site_id": "meu-site",
    "title": "Construindo Sonhos",
    "description": "Crie seu site profissional em minutos.",
    "primary_color": "#1f6feb",
    "secondary_color": "#0d1117",
    "font_family": "system-ui, -apple-system, Segoe UI, Roboto, Arial"
  },
  "sections": [
    {
      "type": "hero",
      "enabled": True,
      "data": {
        "headline": "Seu site profissional, sem complicação",
        "subheadline": "Escolha um template, personalize e publique em poucos passos.",
        "cta_text": "Falar no WhatsApp",
        "cta_url": "https://wa.me/5500000000000",
        "image_url": "https://images.unsplash.com/photo-1522542550221-31fd19575a2d?auto=format&fit=crop&w=1200&q=60"
      }
    },
    {
      "type": "about",
      "enabled": True,
      "data": {
        "title": "Sobre",
        "text": "Somos uma plataforma para criar sites bonitos e rápidos. Você não precisa saber código, hospedagem ou DNS."
      }
    },
    {
      "type": "services",
      "enabled": True,
      "data": {
        "title": "Serviços",
        "items": [
          {"title": "Templates prontos", "text": "Modelos profissionais para começar rápido."},
          {"title": "Edição por blocos", "text": "Troque textos, imagens e botões em segundos."},
          {"title": "Publicação", "text": "Exporte seu site estático e publique onde quiser."}
        ]
      }
    },
    {
      "type": "gallery",
      "enabled": True,
      "data": {
        "title": "Galeria",
        "images": [
          "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=60",
          "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=60",
          "https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=1200&q=60"
        ]
      }
    },
    {
      "type": "contact",
      "enabled": True,
      "data": {
        "title": "Contato",
        "phone": "+55 (00) 00000-0000",
        "email": "contato@exemplo.com",
        "address": "Rua Exemplo, 123 - Centro",
        "instagram": "https://instagram.com/seuperfil",
        "maps_embed": ""
      }
    },
    {
      "type": "footer",
      "enabled": True,
      "data": {
        "text": "© {year} Construindo Sonhos. Todos os direitos reservados."
      }
    }
  ]
}


def load_site():
    if not os.path.exists(SITE_JSON_PATH):
        save_site(DEFAULT_SITE)
    with open(SITE_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_site(site_obj):
    with open(SITE_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(site_obj, f, ensure_ascii=False, indent=2)


def normalize_site(site_obj):
    if 'meta' not in site_obj:
        site_obj['meta'] = {}
    if 'sections' not in site_obj:
        site_obj['sections'] = []
    if 'primary_color' not in site_obj['meta']:
        site_obj['meta']['primary_color'] = '#1f6feb'
    if 'font_family' not in site_obj['meta']:
        site_obj['meta']['font_family'] = 'system-ui, -apple-system, Segoe UI, Roboto, Arial'
    return site_obj


def export_static(site_obj):
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    export_dir = os.path.join(EXPORTS_DIR, 'export_' + ts)
    os.makedirs(export_dir, exist_ok=True)

    from flask import render_template
    html_str = render_template('site.html', site=site_obj, export_mode=True)

    index_path = os.path.join(export_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_str)

    return export_dir, index_path


app = Flask(__name__)


@app.get('/')
def home():
    return redirect(url_for('editor'))


@app.get('/editor')
def editor():
    site = normalize_site(load_site())
    return render_template('editor.html', site=site)


@app.post('/editor/save')
def editor_save():
    site = normalize_site(load_site())
    form = request.form

    site['meta']['title'] = form.get('meta_title', '').strip() or site['meta'].get('title', '')
    site['meta']['description'] = form.get('meta_description', '').strip() or site['meta'].get('description', '')
    site['meta']['primary_color'] = form.get('meta_primary_color', '').strip() or site['meta'].get('primary_color', '#1f6feb')
    site['meta']['secondary_color'] = form.get('meta_secondary_color', '').strip() or site['meta'].get('secondary_color', '#0d1117')
    site['meta']['font_family'] = form.get('meta_font_family', '').strip() or site['meta'].get('font_family', 'system-ui, -apple-system, Segoe UI, Roboto, Arial')

    for idx, sec in enumerate(site['sections']):
        prefix = 's' + str(idx) + '_'
        enabled_val = form.get(prefix + 'enabled', 'off')
        sec['enabled'] = True if enabled_val == 'on' else False

        stype = sec.get('type')
        data = sec.get('data', {})

        if stype == 'hero':
            data['headline'] = form.get(prefix + 'headline', data.get('headline', ''))
            data['subheadline'] = form.get(prefix + 'subheadline', data.get('subheadline', ''))
            data['cta_text'] = form.get(prefix + 'cta_text', data.get('cta_text', ''))
            data['cta_url'] = form.get(prefix + 'cta_url', data.get('cta_url', ''))
            data['image_url'] = form.get(prefix + 'image_url', data.get('image_url', ''))
        elif stype == 'about':
            data['title'] = form.get(prefix + 'title', data.get('title', ''))
            data['text'] = form.get(prefix + 'text', data.get('text', ''))
        elif stype == 'services':
            data['title'] = form.get(prefix + 'title', data.get('title', ''))
            items_raw = form.get(prefix + 'items_json', '')
            try:
                items = json.loads(items_raw) if items_raw.strip() else data.get('items', [])
                if isinstance(items, list):
                    data['items'] = items
            except Exception:
                pass
        elif stype == 'gallery':
            data['title'] = form.get(prefix + 'title', data.get('title', ''))
            images_raw = form.get(prefix + 'images_json', '')
            try:
                images = json.loads(images_raw) if images_raw.strip() else data.get('images', [])
                if isinstance(images, list):
                    data['images'] = images
            except Exception:
                pass
        elif stype == 'contact':
            data['title'] = form.get(prefix + 'title', data.get('title', ''))
            data['phone'] = form.get(prefix + 'phone', data.get('phone', ''))
            data['email'] = form.get(prefix + 'email', data.get('email', ''))
            data['address'] = form.get(prefix + 'address', data.get('address', ''))
            data['instagram'] = form.get(prefix + 'instagram', data.get('instagram', ''))
            data['maps_embed'] = form.get(prefix + 'maps_embed', data.get('maps_embed', ''))
        elif stype == 'footer':
            data['text'] = form.get(prefix + 'text', data.get('text', ''))

        sec['data'] = data

    save_site(site)
    return redirect(url_for('editor'))


@app.get('/preview')
def preview():
    site = normalize_site(load_site())
    return render_template('site.html', site=site, export_mode=False)


@app.post('/export')
def export():
    site = normalize_site(load_site())
    export_dir, index_path = export_static(site)

    zip_base = export_dir
    zip_path = zip_base + '.zip'

    import shutil
    if os.path.exists(zip_path):
        os.remove(zip_path)
    shutil.make_archive(zip_base, 'zip', export_dir)

    return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))


@app.get('/api/site')
def api_site_get():
    return jsonify(normalize_site(load_site()))


@app.post('/api/site')
def api_site_post():
    site_obj = request.get_json(force=True, silent=False)
    site_obj = normalize_site(site_obj)
    save_site(site_obj)
    return jsonify({"ok": True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
'''

base_html = r'''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ site.meta.title }}</title>
  <meta name="description" content="{{ site.meta.description }}">
  <style>
    :root {
      --primary: {{ site.meta.primary_color }};
      --secondary: {{ site.meta.secondary_color }};
      --font: {{ site.meta.font_family }};
      --bg: #0b1220;
      --card: rgba(255,255,255,0.06);
      --text: rgba(255,255,255,0.92);
      --muted: rgba(255,255,255,0.70);
      --border: rgba(255,255,255,0.12);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: var(--font); background: radial-gradient(1200px 600px at 20% -10%, rgba(31,111,235,0.35), transparent 55%), radial-gradient(900px 500px at 95% 10%, rgba(120,60,255,0.22), transparent 60%), var(--bg); color: var(--text); }
    a { color: inherit; }
    .container { width: min(1080px, 92vw); margin: 0 auto; }
    .topbar { position: sticky; top: 0; backdrop-filter: blur(10px); background: rgba(10,16,30,0.55); border-bottom: 1px solid var(--border); z-index: 10; }
    .topbar-inner { display: flex; gap: 12px; align-items: center; padding: 12px 0; }
    .brand { font-weight: 800; letter-spacing: 0.2px; }
    .pill { display: inline-flex; gap: 8px; align-items: center; padding: 8px 10px; border: 1px solid var(--border); border-radius: 999px; background: rgba(255,255,255,0.04); color: var(--muted); text-decoration: none; font-size: 14px; }
    .pill strong { color: var(--text); }
    .pill.primary { border-color: rgba(31,111,235,0.45); background: rgba(31,111,235,0.16); }

    .section { padding: 64px 0; }
    .card { border: 1px solid var(--border); border-radius: 18px; background: var(--card); padding: 18px; }
    .grid { display: grid; gap: 16px; }
    .grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    @media (max-width: 860px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }

    h1 { font-size: clamp(30px, 4vw, 54px); margin: 0 0 12px; }
    h2 { font-size: clamp(22px, 2.5vw, 32px); margin: 0 0 10px; }
    p { color: var(--muted); line-height: 1.55; margin: 0; }
    .btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 12px 14px; border-radius: 12px; text-decoration: none; border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.06); }
    .btn.primary { border-color: rgba(31,111,235,0.55); background: rgba(31,111,235,0.22); }

    .hero { display: grid; gap: 18px; grid-template-columns: 1.2fr 0.8fr; align-items: center; }
    @media (max-width: 860px) { .hero { grid-template-columns: 1fr; } }
    .hero-img { width: 100%; aspect-ratio: 4/3; border-radius: 18px; border: 1px solid var(--border); object-fit: cover; }
    .kpis { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
    .kpi { padding: 8px 10px; border-radius: 999px; border: 1px solid var(--border); color: var(--muted); font-size: 13px; }

    .gallery { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
    @media (max-width: 860px) { .gallery { grid-template-columns: 1fr; } }
    .gallery img { width: 100%; aspect-ratio: 4/3; border-radius: 16px; object-fit: cover; border: 1px solid var(--border); }

    .footer { padding: 32px 0; border-top: 1px solid var(--border); color: var(--muted); font-size: 14px; }
    .muted { color: var(--muted); }
    .split { display: flex; gap: 12px; flex-wrap: wrap; }
    .split > * { flex: 1 1 auto; }

    .editor-wrap { padding: 22px 0 60px; }
    .editor-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 980px) { .editor-grid { grid-template-columns: 1fr; } }
    .field { display: grid; gap: 6px; margin: 10px 0; }
    input, textarea { width: 100%; padding: 10px 12px; border-radius: 12px; border: 1px solid var(--border); background: rgba(255,255,255,0.04); color: var(--text); }
    textarea { min-height: 110px; }
    label { color: var(--muted); font-size: 13px; }
    .sec-title { display: flex; gap: 10px; align-items: center; justify-content: space-between; }
    .sec-title h3 { margin: 0; font-size: 16px; }
    .toggle { display: inline-flex; gap: 8px; align-items: center; font-size: 13px; color: var(--muted); }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .hint { font-size: 12px; color: rgba(255,255,255,0.60); }
  </style>
</head>
<body>
  <div class="topbar">
    <div class="container topbar-inner">
      <div class="brand">{{ site.meta.title }}</div>
      <div style="flex:1"></div>
      {% if export_mode %}
        <span class="pill"><strong>Export</strong><span class="muted">static</span></span>
      {% else %}
        <a class="pill" href="{{ url_for('editor') }}"><strong>Editor</strong></a>
        <a class="pill" href="{{ url_for('preview') }}"><strong>Preview</strong></a>
      {% endif %}
    </div>
  </div>

  {% block content %}{% endblock %}
</body>
</html>
'''

site_html = r'''
{% extends "base.html" %}
{% block content %}
  <div class="container">

    {% for sec in site.sections %}
      {% if sec.enabled %}
        {% if sec.type == 'hero' %}
          <section class="section">
            <div class="hero">
              <div>
                <h1>{{ sec.data.headline }}</h1>
                <p>{{ sec.data.subheadline }}</p>
                <div style="height: 16px"></div>
                <div class="split">
                  {% if sec.data.cta_url and sec.data.cta_text %}
                    <a class="btn primary" href="{{ sec.data.cta_url }}" target="_blank" rel="noopener">{{ sec.data.cta_text }}</a>
                  {% endif %}
                  <a class="btn" href="#contato">Ver contato</a>
                </div>
                <div class="kpis">
                  <div class="kpi">Sem código</div>
                  <div class="kpi">Templates</div>
                  <div class="kpi">Rápido</div>
                </div>
              </div>
              <div>
                {% if sec.data.image_url %}
                  <img class="hero-img" src="{{ sec.data.image_url }}" alt="Imagem" />
                {% else %}
                  <div class="card">Adicione uma imagem no editor.</div>
                {% endif %}
              </div>
            </div>
          </section>

        {% elif sec.type == 'about' %}
          <section class="section">
            <div class="grid grid-2">
              <div>
                <h2>{{ sec.data.title }}</h2>
                <p>{{ sec.data.text }}</p>
              </div>
              <div class="card">
                <div class="muted" style="font-size: 14px;">Dica</div>
                <div style="height: 8px"></div>
                <div>Use este bloco para contar *o que você faz* e *por que confiar em você*.</div>
              </div>
            </div>
          </section>

        {% elif sec.type == 'services' %}
          <section class="section">
            <h2>{{ sec.data.title }}</h2>
            <div style="height: 14px"></div>
            <div class="grid grid-3">
              {% for item in sec.data.items %}
                <div class="card">
                  <div style="font-weight: 700; margin-bottom: 6px;">{{ item.title }}</div>
                  <div class="muted">{{ item.text }}</div>
                </div>
              {% endfor %}
            </div>
          </section>

        {% elif sec.type == 'gallery' %}
          <section class="section">
            <h2>{{ sec.data.title }}</h2>
            <div style="height: 14px"></div>
            <div class="gallery">
              {% for img in sec.data.images %}
                <img src="{{ img }}" alt="Imagem" />
              {% endfor %}
            </div>
          </section>

        {% elif sec.type == 'contact' %}
          <section class="section" id="contato">
            <div class="grid grid-2">
              <div>
                <h2>{{ sec.data.title }}</h2>
                <div style="height: 10px"></div>
                <div class="card">
                  <div class="muted">Telefone</div>
                  <div style="height: 6px"></div>
                  <div>{{ sec.data.phone }}</div>
                  <div style="height: 12px"></div>
                  <div class="muted">Email</div>
                  <div style="height: 6px"></div>
                  <div>{{ sec.data.email }}</div>
                  <div style="height: 12px"></div>
                  <div class="muted">Endereço</div>
                  <div style="height: 6px"></div>
                  <div>{{ sec.data.address }}</div>
                  <div style="height: 12px"></div>
                  {% if sec.data.instagram %}
                    <a class="btn" href="{{ sec.data.instagram }}" target="_blank" rel="noopener">Instagram</a>
                  {% endif %}
                </div>
              </div>
              <div class="card">
                {% if sec.data.maps_embed %}
                  {{ sec.data.maps_embed | safe }}
                {% else %}
                  <div class="muted">Mapa</div>
                  <div style="height: 10px"></div>
                  <div class="muted">Cole aqui o iframe do Google Maps no editor se quiser.</div>
                {% endif %}
              </div>
            </div>
          </section>

        {% elif sec.type == 'footer' %}
          <div class="footer">
            <div class="container">
              {{ sec.data.text.replace('{year}', (cycler(1)|string) ) }}
            </div>
          </div>
        {% endif %}
      {% endif %}
    {% endfor %}

    <div style="height: 24px"></div>

  </div>
{% endblock %}
'''

editor_html = r'''
{% extends "base.html" %}
{% block content %}
  <div class="container editor-wrap">

    <div class="card">
      <div class="sec-title">
        <h3>Editor do site (MVP)</h3>
        <div class="split" style="justify-content: flex-end;">
          <a class="btn" href="{{ url_for('preview') }}" target="_blank" rel="noopener">Abrir preview</a>
          <form action="{{ url_for('export') }}" method="post" style="margin:0">
            <button class="btn primary" type="submit">Exportar ZIP</button>
          </form>
        </div>
      </div>
      <div class="hint" style="margin-top:8px">Edite, salve e abra o preview. Para listas (serviços/galeria), edite o JSON.</div>
    </div>

    <div style="height: 14px"></div>

    <form action="{{ url_for('editor_save') }}" method="post">
      <div class="editor-grid">

        <div class="card">
          <div class="sec-title"><h3>Configurações</h3></div>
          <div class="field">
            <label>Título do site</label>
            <input name="meta_title" value="{{ site.meta.title }}" />
          </div>
          <div class="field">
            <label>Descrição</label>
            <textarea name="meta_description">{{ site.meta.description }}</textarea>
          </div>
          <div class="field">
            <label>Cor primária</label>
            <input class="mono" name="meta_primary_color" value="{{ site.meta.primary_color }}" />
          </div>
          <div class="field">
            <label>Cor secundária</label>
            <input class="mono" name="meta_secondary_color" value="{{ site.meta.secondary_color }}" />
          </div>
          <div class="field">
            <label>Fonte (CSS font-family)</label>
            <input class="mono" name="meta_font_family" value="{{ site.meta.font_family }}" />
          </div>
        </div>

        <div class="card">
          <div class="sec-title"><h3>Seções</h3></div>
          <div class="hint">Cada seção tem um toggle. O preview usa só as seções habilitadas.</div>

          {% for sec in site.sections %}
            <div style="height: 12px"></div>
            <div class="card">
              <div class="sec-title">
                <h3>{{ loop.index }}. {{ sec.type }}</h3>
                <label class="toggle">
                  <input type="checkbox" name="s{{ loop.index0 }}_enabled" {% if sec.enabled %}checked{% endif %} />
                  habilitado
                </label>
              </div>

              {% if sec.type == 'hero' %}
                <div class="field"><label>Headline</label><input name="s{{ loop.index0 }}_headline" value="{{ sec.data.headline }}" /></div>
                <div class="field"><label>Subheadline</label><textarea name="s{{ loop.index0 }}_subheadline">{{ sec.data.subheadline }}</textarea></div>
                <div class="field"><label>CTA texto</label><input name="s{{ loop.index0 }}_cta_text" value="{{ sec.data.cta_text }}" /></div>
                <div class="field"><label>CTA url</label><input class="mono" name="s{{ loop.index0 }}_cta_url" value="{{ sec.data.cta_url }}" /></div>
                <div class="field"><label>Imagem url</label><input class="mono" name="s{{ loop.index0 }}_image_url" value="{{ sec.data.image_url }}" /></div>
              {% elif sec.type == 'about' %}
                <div class="field"><label>Título</label><input name="s{{ loop.index0 }}_title" value="{{ sec.data.title }}" /></div>
                <div class="field"><label>Texto</label><textarea name="s{{ loop.index0 }}_text">{{ sec.data.text }}</textarea></div>
              {% elif sec.type == 'services' %}
                <div class="field"><label>Título</label><input name="s{{ loop.index0 }}_title" value="{{ sec.data.title }}" /></div>
                <div class="field">
                  <label>Itens (JSON)</label>
                  <textarea class="mono" name="s{{ loop.index0 }}_items_json">{{ sec.data.items | tojson(indent=2) }}</textarea>
                  <div class="hint">Formato: [{"title":"...","text":"..."}, ...]</div>
                </div>
              {% elif sec.type == 'gallery' %}
                <div class="field"><label>Título</label><input name="s{{ loop.index0 }}_title" value="{{ sec.data.title }}" /></div>
                <div class="field">
                  <label>Imagens (JSON)</label>
                  <textarea class="mono" name="s{{ loop.index0 }}_images_json">{{ sec.data.images | tojson(indent=2) }}</textarea>
                  <div class="hint">Formato: ["url1", "url2", ...]</div>
                </div>
              {% elif sec.type == 'contact' %}
                <div class="field"><label>Título</label><input name="s{{ loop.index0 }}_title" value="{{ sec.data.title }}" /></div>
                <div class="field"><label>Telefone</label><input name="s{{ loop.index0 }}_phone" value="{{ sec.data.phone }}" /></div>
                <div class="field"><label>Email</label><input name="s{{ loop.index0 }}_email" value="{{ sec.data.email }}" /></div>
                <div class="field"><label>Endereço</label><input name="s{{ loop.index0 }}_address" value="{{ sec.data.address }}" /></div>
                <div class="field"><label>Instagram</label><input class="mono" name="s{{ loop.index0 }}_instagram" value="{{ sec.data.instagram }}" /></div>
                <div class="field"><label>Google Maps iframe (opcional)</label><textarea class="mono" name="s{{ loop.index0 }}_maps_embed">{{ sec.data.maps_embed }}</textarea></div>
              {% elif sec.type == 'footer' %}
                <div class="field"><label>Texto</label><input name="s{{ loop.index0 }}_text" value="{{ sec.data.text }}" /></div>
                <div class="hint">Use {year} para ano automático (na exportação você pode ajustar se quiser).</div>
              {% endif %}

            </div>
          {% endfor %}

        </div>

      </div>

      <div style="height: 14px"></div>
      <button class="btn primary" type="submit">Salvar</button>
      <a class="btn" href="{{ url_for('preview') }}" target="_blank" rel="noopener">Preview</a>
    </form>

  </div>
{% endblock %}
'''

readme_txt = r'''
Construindo Sonhos Web - MVP (Flask)

Como rodar:
1) Entre na pasta app_mvp
2) (Opcional) crie venv
3) Instale dependencias: pip install flask
4) Rode: python app.py
5) Abra: http://localhost:8000/editor

O que tem:
- Editor simples por seções (hero/sobre/servicos/galeria/contato/footer)
- Preview do site
- Exportar um ZIP com index.html estatico
- API JSON do site: GET/POST /api/site

Arquivo de dados:
- data/site.json
'''

site_json = json.dumps({
  "meta": {
    "site_id": "meu-site",
    "title": "Construindo Sonhos",
    "description": "Crie seu site profissional em minutos.",
    "primary_color": "#1f6feb",
    "secondary_color": "#0d1117",
    "font_family": "system-ui, -apple-system, Segoe UI, Roboto, Arial"
  },
  "sections": [
    {
      "type": "hero",
      "enabled": True,
      "data": {
        "headline": "Seu site profissional, sem complicação",
        "subheadline": "Escolha um template, personalize e publique em poucos passos.",
        "cta_text": "Falar no WhatsApp",
        "cta_url": "https://wa.me/5500000000000",
        "image_url": "https://images.unsplash.com/photo-1522542550221-31fd19575a2d?auto=format&fit=crop&w=1200&q=60"
      }
    },
    {
      "type": "about",
      "enabled": True,
      "data": {
        "title": "Sobre",
        "text": "Somos uma plataforma para criar sites bonitos e rápidos. Você não precisa saber código, hospedagem ou DNS."
      }
    },
    {
      "type": "services",
      "enabled": True,
      "data": {
        "title": "Serviços",
        "items": [
          {"title": "Templates prontos", "text": "Modelos profissionais para começar rápido."},
          {"title": "Edição por blocos", "text": "Troque textos, imagens e botões em segundos."},
          {"title": "Publicação", "text": "Exporte seu site estático e publique onde quiser."}
        ]
      }
    },
    {
      "type": "gallery",
      "enabled": True,
      "data": {
        "title": "Galeria",
        "images": [
          "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=60",
          "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=60",
          "https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=1200&q=60"
        ]
      }
    },
    {
      "type": "contact",
      "enabled": True,
      "data": {
        "title": "Contato",
        "phone": "+55 (00) 00000-0000",
        "email": "contato@exemplo.com",
        "address": "Rua Exemplo, 123 - Centro",
        "instagram": "https://instagram.com/seuperfil",
        "maps_embed": ""
      }
    },
    {
      "type": "footer",
      "enabled": True,
      "data": {
        "text": "© {year} Construindo Sonhos. Todos os direitos reservados."
      }
    }
  ]
}, ensure_ascii=False, indent=2)

# Write files
with open(os.path.join(base_dir, 'app.py'), 'w', encoding='utf-8') as f:
    f.write(app_py)
with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
    f.write(base_html)
with open(os.path.join(templates_dir, 'site.html'), 'w', encoding='utf-8') as f:
    f.write(site_html)
with open(os.path.join(templates_dir, 'editor.html'), 'w', encoding='utf-8') as f:
    f.write(editor_html)
with open(os.path.join(base_dir, 'README.txt'), 'w', encoding='utf-8') as f:
    f.write(readme_txt)

os.makedirs(os.path.join(base_dir, 'data'), exist_ok=True)
with open(os.path.join(base_dir, 'data', 'site.json'), 'w', encoding='utf-8') as f:
    f.write(site_json)

print('Created project at: ' + base_dir)
print('Files:')
for root_dir, dirs, file_names in os.walk(base_dir):
    for fn in sorted(file_names):
        rel = os.path.relpath(os.path.join(root_dir, fn), base_dir)
        print('- ' + rel)
