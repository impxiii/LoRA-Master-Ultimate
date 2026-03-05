from flask import Flask, render_template_string, send_from_directory, request, jsonify
import os
from collections import Counter

app = Flask(__name__)
DATA_FOLDER = '/data'

def get_dataset_info():
    cards, all_tags = [], []
    img_exts = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG')
    if not os.path.exists(DATA_FOLDER): return cards, Counter(), 0, 0
    files = os.listdir(DATA_FOLDER)
    img_files = [f for f in files if f.lower().endswith(img_exts)]
    for img_name in sorted(img_files):
        base = os.path.splitext(img_name)[0]
        txt_name = base + '.txt'
        tags = []
        txt_path = os.path.join(DATA_FOLDER, txt_name)
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                tags = [t.strip() for t in f.read().split(',') if t.strip()]
                all_tags.extend(tags)
        cards.append({'name': base, 'img': img_name, 'txt': txt_name, 'tags': tags, 'has_txt': os.path.exists(txt_path)})
    return cards, Counter(all_tags), len(img_files), len([f for f in files if f.endswith('.txt')])

@app.route('/')
def index():
    cards, stats, img_c, txt_c = get_dataset_info()
    return render_template_string(HTML_TEMPLATE, cards=cards, stats=dict(stats), img_c=img_c, txt_c=txt_c, utags=len(stats))

@app.route('/api/save', methods=['POST'])
def save_tags():
    data = request.json
    with open(os.path.join(DATA_FOLDER, data['file']), 'w', encoding='utf-8') as f:
        f.write(', '.join(data['tags']))
    return jsonify(success=True)

@app.route('/api/bulk', methods=['POST'])
def bulk_op():
    d = request.json
    tag, action, index = d['tag'].strip(), d['action'], int(d.get('index', 0))
    target_files = d.get('files') # Если есть список файлов (чекбоксы), работаем по ним
    
    files_to_process = []
    if target_files:
        files_to_process = target_files
    else:
        # Если файлы не переданы, берем вообще все .txt в папке
        files_to_process = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.txt')]

    for txt_name in files_to_process:
        txt_p = os.path.join(DATA_FOLDER, txt_name)
        tags = []
        if os.path.exists(txt_p):
            with open(txt_p, 'r', encoding='utf-8') as tf:
                tags = [t.strip() for t in tf.read().split(',') if t.strip()]
        
        if action == 'add' and tag not in tags:
            idx = max(0, min(index - 1, len(tags))) if index > 0 else len(tags)
            tags.insert(idx, tag)
        elif action == 'delete':
            tags = [t for t in tags if tag.lower() != t.lower()] # Строгое соответствие тегу
            
        with open(txt_p, 'w', encoding='utf-8') as tf:
            tf.write(', '.join(tags))
    return jsonify(success=True)

@app.route('/images/<path:filename>')
def static_proxy(filename):
    return send_from_directory(DATA_FOLDER, filename)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LoRA Master Ultimate</title>
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
    <style>
        :root { --accent: #00d4ff; --bg: #090909; --card-bg: #141414; --danger: #ff4b4b; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: #e0e0e0; margin: 0; padding: 15px; }
        .mini-dash { display: flex; gap: 20px; background: #111; padding: 10px; border-radius: 8px; border: 1px solid #333; margin-bottom: 10px; font-size: 13px; align-items: center; }
        .mini-dash b { color: var(--accent); }
        
        .stats-bar { background: #111; padding: 12px; border-radius: 10px; border: 1px solid #333; margin-bottom: 15px; }
        .stats-ctrl { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 12px; color: #666; }
        .tags-wrap { max-height: 180px; overflow-y: auto; display: flex; flex-wrap: wrap; gap: 8px; }
        .stat-tag { color: #888; cursor: pointer; font-size: 11px; padding: 3px 6px; border: 1px solid #222; border-radius: 4px; background: #181818; }
        .stat-tag:hover { border-color: var(--accent); color: #fff; }

        .toolbar { position: sticky; top: 0px; background: rgba(20,20,20,0.98); backdrop-filter: blur(10px); padding: 15px; border-radius: 10px; z-index: 100; margin-bottom: 20px; display: flex; gap: 10px; border: 1px solid #444; align-items: center; flex-wrap: wrap; }
        input, .num-input { background: #1a1a1a; border: 1px solid #444; color: white; padding: 8px; border-radius: 6px; }
        .num-input { width: 45px; text-align: center; }
        button { background: var(--accent); border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px; color: #000; }
        
        /* Новый стиль для маленьких кнопок-стрелок */
        .icon-btn { background: #333; color: var(--accent); padding: 8px 12px; font-size: 16px; line-height: 1; border: 1px solid #444; border-radius: 6px; cursor: pointer; }
        .icon-btn:hover { background: #444; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .card { background: var(--card-bg); border-radius: 12px; border: 1px solid #333; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .card.selected { border-color: var(--accent); box-shadow: 0 0 10px rgba(0,212,255,0.2); }
        .select-box { position: absolute; top: 12px; left: 12px; z-index: 10; width: 20px; height: 20px; cursor: pointer; }
        
        .img-box { width: 100%; height: 220px; background: #000; overflow: hidden; position: relative; }
        .img-box img { width: 100%; height: 100%; object-fit: contain; cursor: zoom-in; }
        .badge { position: absolute; top: 10px; right: 10px; background: var(--danger); font-size: 10px; padding: 3px 7px; border-radius: 4px; }

        .info { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }
        .tag-list { display: flex; flex-wrap: wrap; gap: 6px; min-height: 100px; max-height: 250px; padding: 10px; background: #0c0c0c; border-radius: 8px; border: 1px solid #222; overflow-y: auto; resize: vertical; }
        .tag { background: #222; border: 1px solid #3d3d3d; padding: 4px 8px; border-radius: 5px; font-size: 12px; color: #ccc; cursor: grab; }
        .tag.highlight { background: var(--danger) !important; color: #fff !important; }

        .add-row { margin-top: auto; display: flex; gap: 5px; padding-top: 10px; border-top: 1px solid #333; align-items: center; }
        .btn-s { padding: 11px 18px; font-size: 12px; background: #333; color: var(--accent); border: 1px solid #444; border-radius: 6px; cursor: pointer; }
        .hint { font-size: 9px; color: #555; margin-top: 5px; text-align: center; }

        #modal { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.95); z-index: 2000; justify-content: center; align-items: center; }
        #modal img { max-width: 95%; max-height: 95%; object-fit: contain; }

        /* Контейнер для подсказки */
        .tooltip-container {
            position: relative;
            display: inline-block;
            margin-left: 5px; /* небольшой отступ от кнопки */
            cursor: help;
        }

        /* Иконка информации */
        .info-icon {
            display: inline-block;
            width: 20px;
            height: 20px;
            background: #333;
            color: var(--accent);
            border-radius: 50%;
            text-align: center;
            line-height: 20px;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #444;
        }

        /* Текст подсказки (скрыт по умолчанию) */
        .tooltip-text {
            visibility: hidden;
            width: 260px;
            background-color: #222;
            color: #fff;
            text-align: center;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #444;
            font-size: 12px;
            line-height: 1.4;
            
            /* Позиционирование */
            position: absolute;
            z-index: 1;
            bottom: 150%; /* появляется сверху */
            left: 50%;
            transform: translateX(-50%);
            
            /* Анимация появления */
            opacity: 0;
            transition: opacity 0.2s;
            
            /* Стрелочка снизу подсказки */
            &::after {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #222 transparent transparent transparent;
            }
        }

        /* Показываем подсказку при наведении на контейнер */
        .tooltip-container:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }

    </style>
</head>
<body>
    <div class="mini-dash">
        <span>Images: <b>{{ img_c }}</b> | Txt: <b>{{ txt_c }}</b> | Unique Tags: <b>{{ utags }}</b></span>
        <button class="btn-s" style="margin-left:auto" onclick="selectAllVisible()">Select All Visible</button>
        <button class="btn-s" style="background:#442222; color:#ff8888" onclick="deselectAll()">Clear Selection</button>
        <span id="selectedCount" style="margin-left: 15px; color: var(--accent);">Selected: <b>0</b></span>
    </div>

    <div class="stats-bar">
        <div class="stats-ctrl">
            <span>Global Stats:</span>
            <div>
                <button class="btn-s" onclick="sortStats('alpha')">Name A-Z</button>
                <button class="btn-s" onclick="sortStats('freq')">Popularity</button>
            </div>
        </div>
        <div class="tags-wrap" id="statsWrap">
            {% for tag, count in stats.items() %}
            <span class="stat-tag" data-count="{{ count }}" onclick="setSearch('{{ tag }}')">{{ tag }}: <b>{{ count }}</b></span>
            {% endfor %}
        </div>
    </div>

    <div class="toolbar">
        <input type="text" id="searchInput" placeholder="Filter images/tags..." onkeyup="filter()">
        <button style="background:#333; color:#ccc" onclick="clearSearch()">Reset Filter</button>

        <!-- Две новые кнопки для переноса тега -->
        <button class="icon-btn" id="copySearchToBulk" title="Копировать поиск в поле тега">⥂</button>
        <button class="icon-btn" id="copyBulkToSearch" title="Копировать тег в поле поиска">⥃</button>

        <div style="width: 1px; height: 30px; background: #444; margin: 0 10px;"></div>

        <input type="text" id="bulkInput" placeholder="Tag name...">
        <input type="number" id="bulkIdx" class="num-input" value="0" title="Position (1=first, 0=end)">
        <button onclick="bulkAction('add')">Add Tag</button>
        <button style="background:var(--danger)" onclick="bulkAction('delete')">Delete Tag</button>
        <span class="tooltip-container">
            <span class="info-icon">ⓘ</span>
            <span class="tooltip-text">If no checkboxes are selected, the operation applies to ALL files.</span>
</span>
    </div>

    <div class="grid">
        {% for card in cards %}
        <div class="card {{ 'missing' if not card.has_txt else '' }}" data-txt="{{ card.txt }}">
            <input type="checkbox" class="select-box" onchange="updateSelected()">
            <div class="img-box">
                {% if not card.has_txt %}<div class="badge">MISSING TXT</div>{% endif %}
                <img src="/images/{{ card.img }}" onclick="openModal(this.src)">
            </div>
            <div class="info">
                <div style="font-size: 10px; color:#444; margin-bottom: 5px;">{{ card.name }}</div>
                <div class="tag-list">
                    {% for tag in card.tags %}
                    <span class="tag" data-tag="{{ tag.lower() }}" onclick="if(event.ctrlKey) deleteTag('{{ card.txt }}', '{{ tag }}', this)">{{ tag }}</span>
                    {% endfor %}
                </div>
                <div class="add-row">
                    <input type="text" placeholder="Add..." style="height: 20px;" onkeydown="if(event.key==='Enter') addOne('{{ card.txt }}', this)">
                    <input type="number" class="num-input" value="1" style="height: 20px;">
                    <div class="btn-s" onclick="addOne('{{ card.txt }}', this.previousElementSibling.previousElementSibling, this.previousElementSibling.value)">Add</div>
                </div>
                <div class="hint">Tip: Ctrl + Click to delete tag</div>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="modal" onclick="this.style.display='none'"><img src="" id="modalImg"></div>

    <script>
        // Sortable JS
        document.querySelectorAll('.tag-list').forEach(el => {
            new Sortable(el, { animation: 150, onEnd: function (evt) {
                let file = evt.item.closest('.card').dataset.txt;
                let tags = Array.from(evt.to.querySelectorAll('.tag')).map(t => t.innerText);
                fetch('/api/save', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({file: file, tags: tags})});
            }});
        });

        function sortStats(type) {
            let container = document.getElementById('statsWrap');
            let items = Array.from(container.children);
            items.sort((a, b) => {
                if(type === 'alpha') return a.innerText.localeCompare(b.innerText);
                return parseInt(b.dataset.count) - parseInt(a.dataset.count);
            });
            items.forEach(i => container.appendChild(i));
        }

        function filter() {
            let q = document.getElementById('searchInput').value.toLowerCase().trim();
            document.querySelectorAll('.tag').forEach(t => t.classList.toggle('highlight', q && t.dataset.tag.includes(q)));
            document.querySelectorAll('.card').forEach(c => {
                let match = q === '' || c.innerText.toLowerCase().includes(q);
                c.style.display = match ? '' : 'none';
            });
        }

        function selectAllVisible() {
            document.querySelectorAll('.card').forEach(c => {
                if(c.style.display !== 'none') c.querySelector('.select-box').checked = true;
            });
            updateSelected();
        }

        function deselectAll() {
            document.querySelectorAll('.select-box').forEach(cb => cb.checked = false);
            updateSelected();
        }

        function updateSelected() {
            let sel = document.querySelectorAll('.select-box:checked');
            document.getElementById('selectedCount').innerHTML = "Selected: <b>" + sel.length + "</b>";
            document.querySelectorAll('.card').forEach(c => c.classList.toggle('selected', c.querySelector('.select-box').checked));
        }

        function clearSearch() { document.getElementById('searchInput').value = ''; filter(); }
        function setSearch(v) { document.getElementById('searchInput').value = v; filter(); }
        function openModal(s) { document.getElementById('modalImg').src = s; document.getElementById('modal').style.display = 'flex'; }

        function addOne(file, input, idx=0) {
            let val = input.value.trim(); if(!val) return;
            let tags = Array.from(input.closest('.info').querySelectorAll('.tag')).map(t => t.innerText);
            if(!tags.includes(val)) {
                let p = parseInt(idx);
                if(p <= 0) tags.push(val); else tags.splice(p-1, 0, val);
                fetch('/api/save', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({file: file, tags: tags})}).then(() => location.reload());
            }
        }

        function deleteTag(file, tag, el) {
            let tags = Array.from(el.parentElement.querySelectorAll('.tag')).map(t => t.innerText).filter(t => t !== tag);
            fetch('/api/save', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({file: file, tags: tags})}).then(() => el.remove());
        }

        function bulkAction(action) {
            let tag = document.getElementById('bulkInput').value.trim();
            let index = document.getElementById('bulkIdx').value;
            let selected = Array.from(document.querySelectorAll('.select-box:checked')).map(cb => cb.closest('.card').dataset.txt);
            
            // Если ничего не выбрано чекбоксами, передаем null (сервер обработает как "все файлы")
            let filesToSend = selected.length > 0 ? selected : null;

            if(!tag) { alert("Enter tag name!"); return; }
            if(!filesToSend && action === 'delete' && !confirm("Delete this tag from ALL files in folder?")) return;

            fetch('/api/bulk', {
                method: 'POST', headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify({action: action, tag: tag, index: index, files: filesToSend}) 
            }).then(() => location.reload());
        }

        // --- Новые функции для кнопок переноса ---
        document.getElementById('copySearchToBulk').addEventListener('click', function() {
            let searchVal = document.getElementById('searchInput').value.trim();
            if (searchVal) {
                document.getElementById('bulkInput').value = searchVal;
            }
        });

        document.getElementById('copyBulkToSearch').addEventListener('click', function() {
            let bulkVal = document.getElementById('bulkInput').value.trim();
            if (bulkVal) {
                document.getElementById('searchInput').value = bulkVal;
                filter(); // сразу применяем фильтр по этому тегу
            }
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)