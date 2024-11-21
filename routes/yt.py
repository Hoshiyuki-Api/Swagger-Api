import requests
import time


class Ddownr:
    @staticmethod
    def download(url, format, max_retries=10):
        try:
            response = requests.get(
                f"https://p.oceansaver.in/ajax/download.php?copyright=0&format={format}&url={url}",
                headers={
                    'User-Agent': 'MyApp/1.0',
                    'Referer': 'https://ddownr.com/enW7/youtube-video-downloader'
                }
            )
            data = response.json()
            media = Ddownr.cek_progress(data['id'], max_retries)
            return {
                'success': True,
                'format': format,
                'title': data['title'],
                'thumbnail': data['info']['image'],
                'downloadUrl': media
            }
        except requests.RequestException as error:
            return {
                'success': False,
                'message': str(error)
            }

    @staticmethod
    def cek_progress(id, max_retries):
        retries = 0
        try:
            while retries < max_retries:
                progress_response = requests.get(
                    f"https://p.oceansaver.in/ajax/progress.php?id={id}",
                    headers={
                        'User-Agent': 'MyApp/1.0',
                        'Referer': 'https://ddownr.com/enW7/youtube-video-downloader'
                    }
                )
                data = progress_response.json()
                if data['progress'] == 1000:
                    return data['download_url']
                else:
                    time.sleep(1)
                    retries += 1
            return {
                'success': False,
                'message': 'Exceeded max retries without completion'
            }
        except requests.RequestException as error:
            return {
                'success': False,
                'message': str(error)
            }

ddownr = Ddownr()
print (ddownr.download("https://youtube.com/shorts/tH0ctzMelwk?si=gLhgOFxQ6qebzqDw", "mp3"))
