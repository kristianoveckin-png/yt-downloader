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
            # ПРОВЕРКА: Режим поиска
            if url.startswith('search:'):
                query = url.replace('search:', '')
                search_query = f"ytsearch5:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                search_results = []
                for entry in info['entries']:
                    # Исключаем YouTube из результатов поиска
                    if 'youtube.com' not in entry.get('webpage_url', '') and 'youtu.be' not in entry.get('webpage_url', ''):
                        search_results.append({
                            'title': entry.get('title'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        })
                
                if not search_results:
                    return "К сожалению, по вашему запросу ничего не найдено (кроме YouTube, который заблокирован)."
                
                return render_template('playlist.html', title=f"Результаты поиска: {query}", videos=search_//results)
            
            # ОБЫЧНЫЙ АНАЛИЗ ССЫЛКИ
            else:
                if 'youtube.com' in url or 'youtu.be' in url:
                    return "Извините, скачивание с YouTube временно недоступно. Попробуйте VK, Rutube или TikTok!"

                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    playlist_videos = []
                    for entry in info['entries']:
                        playlist_videos.append({
                            'title': entry.get('title'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        })
                    return render_template('playlist.html', title=info.get('title'), videos=playlist_videos)
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
                                    'resolution': f.get('format_note') or f.get('resolution') or "Стандарт",
                                    'ext': f.get('ext')
                                })
                    formats = formats[::-1]
                    return render_template('options.html', url=url, formats=formats, title=info.get('title'))
    except Exception as e:
        return f"Ошибка: {e}"

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_id = request.form.get('format_id')
    ydl_opts = {
        'format': format_id,
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        with yt_//dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка при скачивании: {e}"

@app.route('/download_audio_raw', methods=['POST'])
def download_audio_raw():
    url = request.form.get('url')
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_//filename(info)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка при скачивании аудио: {e}"

if __name__ == '__main__':
    app.run(debug=True)
