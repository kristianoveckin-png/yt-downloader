from flask import Flask, render_template, request, send_file, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

# Маршрут для иконки сайта
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(".", "favicon.png")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    
    # Настройки для yt-dlp (используем /tmp/ для Render)
    ydl_opts = {
        'format': 'best', 
        'outtmpl': '/tmp/%(title)s.%(ext)s', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка при скачивании: {e}"

if __name__ == '__main__':
    app.run(debug=True)
