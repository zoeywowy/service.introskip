# -*- coding: utf-8 -*-
"""Small standard-library HTTP helpers.

Avoids installing a separate requests add-on dependency in Kodi. Downloads are
streamed to disk so large IntroDB exports never need to live in memory.
"""
import hashlib
import json
import os
from urllib.error import HTTPError as _URLHTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class HTTPError(Exception):
    """Base error for failed HTTP operations."""


class HTTPStatusError(HTTPError):
    def __init__(self, status_code, reason=""):
        self.status_code = int(status_code)
        self.reason = str(reason or "")
        super().__init__("HTTP {} {}".format(self.status_code, self.reason).strip())


class HTTPTransportError(HTTPError):
    pass


class DownloadCancelled(Exception):
    """Raised when Kodi is shutting down during a streamed download."""


def _url_with_params(url, params):
    if not params:
        return url
    query = urlencode(params, doseq=True)
    return "{}{}{}".format(url, "&" if "?" in url else "?", query)


def _open(url, params=None, timeout=3, headers=None):
    url = _url_with_params(url, params)
    request_headers = {"User-Agent": "IntroSkip Kodi add-on"}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers, method="GET")
    try:
        return urlopen(request, timeout=timeout)
    except _URLHTTPError as exc:
        raise HTTPStatusError(exc.code, exc.reason) from exc
    except (URLError, OSError, TimeoutError) as exc:
        reason = getattr(exc, "reason", exc)
        raise HTTPTransportError(str(reason)) from exc


def get_bytes(url, params=None, timeout=3, headers=None):
    """Fetch a small response body, such as a manifest or compressed API JSON."""
    with _open(url, params=params, timeout=timeout, headers=headers) as response:
        return response.read()


def get_json(url, params=None, timeout=3, headers=None):
    """Fetch and decode a UTF-8 JSON response."""
    payload = get_bytes(url, params=params, timeout=timeout, headers=headers)
    return json.loads(payload.decode("utf-8-sig"))


def download_to_file(url, destination, timeout=3, cancel_event=None, chunk_size=65536):
    """Stream a response to disk and return (bytes_written, sha256_hex)."""
    digest = hashlib.sha256()
    total = 0
    try:
        with _open(url, timeout=timeout) as response:
            with open(destination, "wb") as output:
                while True:
                    if cancel_event is not None and cancel_event.is_set():
                        raise DownloadCancelled("Download cancelled during Kodi shutdown")
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    output.write(chunk)
                    digest.update(chunk)
                    total += len(chunk)
        return total, digest.hexdigest()
    except Exception:
        try:
            os.remove(destination)
        except OSError:
            pass
        raise
