import requests


class HttpHeadGetter:
    @staticmethod
    def get_content_len(url):
        r = requests.head(url, allow_redirects=True)
        if r.status_code == 200:
            return r.headers.get("content-length", -1)
        else:
            return -1

    @staticmethod
    def get_content_type(url) -> str:
        r = requests.head(url, allow_redirects=True)
        if r.status_code == 200:
            return r.headers.get("content-type", "unknown")
        else:
            return "unknown"
