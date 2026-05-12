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
            if url.startswith('search:'):
                query = url.replace('search:', '')
                search_query = f"ytsearch10:{query}"
                info = ydl.extract_info(search_query, download=False)
                results = []
                for entry in info['entries']:
                    webpage = entry.get('webpage_url', '').lower()
                    if 'youtube.com' not in webpage and 'youtu.be' not in webpage:
                        results.append({
                            'title': entry.get('title'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        })
                if not results:
                    return "Ничего не найдено."
                return render_template('playlist.html', title=f"Результаты поиска: {query}", videos=results)
            
            else:
                if 'youtube.com' in url.lower() or 'youtu.be' in url.lower():
                    return "Извините, YouTube временно недоступен."

                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    playlist_videos = []
                    for entry in info['entries']:
                        webpage = entry.get('webpage_url', '').lower()
                        if 'youtube.com' not in webpage and 'youtu.be' not in webpage:
                            playlist_videos.append({
                                'title': entry.get('title'),
                                'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            })
                    return render_//template('playlist.html', title=info.get('title'), videos=playlist_videos)
                else:
                    # НОВАЯ ЛОГИКА ПОДБОРА КАЧЕСТВА
                    formats = []
                    # 1. Сначала ищем форматы с видео и звуком (mp4)
                    for f in info.get('formats', []):
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            # Добавляем любой формат, где есть и звук, и видео
                            formats.append({
                                'format_id': f.get('format_id'),
                                'resolution': f.get('format_note') or f.get('resolution') or "Стандарт",
                                'ext': f.get('ext')
                            })
                    
                    # 2. Если список пуст, берем вообще любые доступные форматы
                    if not formats:
                        for f in info.get('formats', []):
                            formats.append({
                                'format_id': f.get('format_id'),
                                'resolution': f.get('format_note') or f.get('resolution') or "Стандарт",
                                'ext': f.get('ext')
                            })

                    # Сортируем так, чтобы самые высокие разрешения были сверху
                    # Мы просто переворачиваем список, так как yt-dlp обычно выдает от низкого к высокому
                    formats = formats[::-1]
                    
                    # Оставляем только уникальные разрешения, чтобы не было 10 одинаковых 360p
                    seen_res = set()
                    unique_formats = []
                    for f in formats:
                        if f['resolution'] not in seen_res:
                            unique_formats.append(f)
                            seen_res.add(f['resolution'])
                    
                    return render_template('options.html', url=url, formats=unique_formats, title=info.get('title'))
    except Exception as e:
        return f"Ошибка: {e}"
