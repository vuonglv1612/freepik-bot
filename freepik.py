import requests
import os
import urllib.parse
from dataclasses import dataclass
from redis import Redis
import json


@dataclass
class Freepik:
    success: bool
    filename: str
    filesize: int
    linkvip: str


def get_credentials():
    return os.getenv("EMAIL"), os.getenv("PASSWORD")


def get_cached_cookie():
    redis_url = os.getenv("REDIS_URI")
    if not redis_url:
        return None, None
    client = Redis.from_url(redis_url, decode_responses=True)
    value = client.get("cookie")
    if not value:
        return None, None
    dict_value = json.loads(value)
    return dict_value["cookie"], dict_value["expires"]


def cache_cookie(cookie, expires_at=None):
    redis_url = os.getenv("REDIS_URI")
    if not redis_url:
        return
    client = Redis.from_url(redis_url, decode_responses=True)
    value = json.dumps({"cookie": cookie, "expires": expires_at})
    if expires_at:
        client.set("cookie", value, exat=int(expires_at))
    else:
        client.set("cookie", value, ex=3600 * 24)
    print("Cached cookie")
    client.close()


def get_user_info():
    session = login()
    result = session.get("https://vngraphic.com/infoUser")
    try:
        result = result.json()
    except Exception:
        raise Exception("Session expired")
    session.close()
    return result


def login():
    session = requests.Session()
    cached_cookie, expires = get_cached_cookie()
    if cached_cookie:
        session.cookies.set("connect.sid", cached_cookie, domain="vngraphic.com", expires=expires)
        try:
            result = session.get("https://vngraphic.com/infoUser")
            try:
                result = result.json()
            except Exception:
                raise Exception("Session expired")
            return session
        except Exception:
            pass

    username, password = get_credentials()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"
    }
    url = "https://vngraphic.com/login"
    form_data = "email={}&password={}".format(urllib.parse.quote(username), urllib.parse.quote(password))
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = session.post(url, headers=headers, data=form_data, allow_redirects=False)
    if not response.ok:
        raise Exception("Login failed")

    result = session.get("https://vngraphic.com/infoUser")
    try:
        result = result.json()
    except Exception:
        raise Exception("Session expired")
    for cookie in session.cookies:
        if cookie.name == "connect.sid":
            cache_cookie(cookie.value, cookie.expires)
            break

    return session


def get_freepik(url):
    session = login()

    payload = {
        "link": url,
        "typeDownload": "image",
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = session.post("https://vngraphic.com/freepik", headers=headers, json=payload)
    if not response.ok:
        raise Exception("Get link failed")
    freepik = Freepik(**response.json())

    session.close()
    return freepik
