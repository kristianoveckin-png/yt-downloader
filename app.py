from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    
    # Настройки для yt-dlp
    # ВАЖНО: Используем /tmp/, так как Render позволяет писать только туда
    ydl_opts = {
        'format': 'best', 
        'outtmpl': '/tmp/%(title)s.%(ext)s', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем информацию и скачиваем файл во временную папку /tmp/
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Отправляем файл пользователю
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка при скачивании: {e}"

if __name__ == '__main__':
    # На локальном компьютере запустится на 5000 порту
    app.run(debug=True)
