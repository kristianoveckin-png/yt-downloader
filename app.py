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
    ydl_opts = {
        'format': 'best', # Скачивать лучшее доступное качество
        'outtmpl': '/tmp/%(title)s.%(ext)s', # Папка для временного хранения
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем информацию о видео
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Отправляем файл пользователю
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка при скачивании: {e}"

if __name__ == '__main__':
    # Создаем папку downloads, если её нет
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
