from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for
import yt_dlp
import os

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(".", "favicon.png")

@app.route('/')
def index():
    return render_template('index.html')

# Эта страница анализирует ссылку и показывает доступные форматы
@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    if not url:
        return redirect(url_for('index'))

    ydl_opts = {'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            # Собираем только те форматы, где есть и видео, и аудио вместе (для простоты)
            # или лучшие доступные варианты
            for f in info.get('formats', []):
                # Фильтруем: нам нужны форматы с видео, аудио и расширением mp4
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    formats.append({
                        'format_id': f.get('format_id'),
                        'resolution': f.get('format_note') or f.get('resolution'),
                        'ext': f.get('ext')
                    })
            
            # Если ничего не нашли в mp4, берем вообще всё, что есть
            if not formats:
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        formats.append({
                            'format_id': f.get('format_id'),
                            'resolution': f.get('format_note') or f.get('resolution') or "Стандарт",
                            'ext': f.get('ext')
                        })

            return render_template('options.html', url=url, formats=formats, title=info.get('title'))
    except Exception as e:
        return f"Ошибка при анализе видео: {e}"

# Эта функция скачивает выбранное качество
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_id = request.form.get('format_id')
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': '/tmp/%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка при скачивании: {e}"

if __name__ == '__main__':
    app.run(debug=True)
