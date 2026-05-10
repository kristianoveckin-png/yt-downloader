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

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    # Проверяем: ссылка пришла из формы (POST) или из ссылки-параметра (GET)
    if request.method == 'POST':
        url = request.form.get('url')
    else:
        url = request.args.get('url')
        
    if not url:
        return redirect(url_for('index'))

    ydl_opts = {
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'extract_flat': 'in_playlist',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Проверка на плейлист
            if 'entries' in info:
                playlist_videos = []
                for entry in info['entries']:
                    playlist_videos.append({
                        'title': entry.get('title'),
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    })
                return render_template('playlist.html', title=info.get('title'), videos=playlist_videos)
            
            # Обычное видео
            else:
                formats = []
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                        formats.append({
                            'format_id': f.get('format_id'),
                            'resolution': f.get('format_note') or f.get('resolution'),
                            'ext': f.get('ext')
                        })
                
                if not formats:
                    for f in info.get('formats', []):
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            formats.append({
                                'format_id': f.get('format_id'),
                                'resolution': f.get('//format_note') or f.get('resolution') or "Стандарт",
                                'ext': f.get('ext')
                            })

                # ПЕРЕВОРОТ СПИСКА: Теперь самое лучшее качество будет сверху
                formats = formats[::-1]

                return render_template('options.html', url=url, formats=formats, title=info.get('title'))
    except Exception as e:
        return f"Ошибка при анализе: {e}"

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_id = request.form.get('format_id')
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
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
