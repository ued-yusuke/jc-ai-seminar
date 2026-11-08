from pathlib import Path
import re, base64, json

root = Path(__file__).resolve().parents[2]
target = root / 'index.html'
source = target.read_text(encoding='utf-8')
assert 'data-illustration=' not in source, 'Already applied'
mapping = {
    1: ('assistant', 'スマートフォンのAI助手と会話する人'),
    8: ('robot', '星を持つミニチュアロボット'),
    9: ('drafting', 'パソコンで文章の下書きを作る人'),
    10: ('summary', '散らばった資料を要点に整理'),
    11: ('ideas', '付箋でアイデアを広げる人'),
    12: ('image-making', 'タブレットで画像を作る人'),
    13: ('research', 'データを調べる人'),
    14: ('conversation', '対話しながら相談する人たち'),
    15: ('automation', '申請からタスク整理、期限設定、チャット通知へ進む自動化'),
    16: ('reports', '議事メモを整理された報告書に変える'),
    17: ('social', 'SNS投稿と反応、投稿予定の管理'),
    20: ('deep-research', '資料を虫眼鏡で詳しく調べる'),
    21: ('presentation', 'グラフを使ったスライド資料'),
    22: ('conversation', '対話しながら考える相談相手'),
    23: ('fact-check', '資料の内容を自分で確認する'),
    24: ('privacy', '鍵と盾で秘密の書類を守る'),
}
counter = 0
def replace_image(match):
    global counter
    tag = match.group()
    if 'src="data:image/' not in tag:
        return tag
    counter += 1
    if counter not in mapping:
        return tag
    name, alt = mapping[counter]
    raw = (root / 'november/assets/isometric' / (name + '.png')).read_bytes()
    data = 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')
    tag = re.sub(r'src="[^"]*"', lambda _: 'src="' + data + '"', tag)
    tag = re.sub(r'alt="[^"]*"', 'alt="' + alt + '（アイソメトリック）"', tag)
    return tag.replace('<img ', '<img data-illustration="' + name + '" ')

result = re.sub(r'<img\b[^>]*>', replace_image, source)
assert counter == 24
icon_count = 0
def replace_icon(match):
    global icon_count
    icon_count += 1
    opening, content = match.groups()
    # Keep the original native vector symbol on an extruded isometric tile.
    svg = '<svg viewBox="0 0 64 64" aria-hidden="true" class="iso-icon">'
    svg += '<ellipse cx="32" cy="53" rx="25" ry="6" fill="#25254b" opacity=".09" stroke="none"/>'
    svg += '<path d="M5 25L32 41V51L5 35Z" fill="#9B72CB" stroke="none"/>'
    svg += '<path d="M32 41L59 25V35L32 51Z" fill="#4285F4" stroke="none"/>'
    svg += '<path d="M5 25L32 9L59 25L32 41Z" fill="#eef0ff" stroke="#d4d8ed" stroke-width="1"/>'
    svg += '<g transform="matrix(1 .58 -1 .58 32 11)" fill="none" stroke="#5b5da7" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' + content + '</g></svg>'
    return opening + svg + '</div>'

result = re.sub(r'(<div class="ic(?: [^"]*)?">)<svg[^>]*>(.*?)</svg></div>', replace_icon, result, flags=re.S)
assert icon_count == 11, icon_count
css = '''
  /* Shared isometric illustration treatment: keep the complete miniature visible. */
  img[data-illustration]{object-fit:contain!important;background:#fff}
  .til.u.photo{background:#fff}
  .til.u.photo img[data-illustration]{width:100%;height:100%}
  .roi .illu:has(img[data-illustration]){background:#fff}
  .roi .illu img[data-illustration]{width:100%;height:100%}
  .tcard .til:has(img[data-illustration]){height:172px}
  .tcard .til img[data-illustration]{height:164px;width:100%}
  .ic:has(.iso-icon){background:transparent!important;overflow:visible}
  .ic svg.iso-icon{width:58px;height:58px}
  .ic.sm svg.iso-icon{width:48px;height:48px}
'''
result = result.replace('</style>', css + '</style>', 1)
# Existing single-file distribution remains usable offline, without an assets folder.
output = Path(__file__).resolve().parent / 'preview.html'
output.write_text(result, encoding='utf-8')
print(json.dumps({'images_replaced': len(mapping), 'vector_icons': icon_count, 'html_bytes': output.stat().st_size}))
