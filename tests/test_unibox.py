import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image

import unibox as ub


def test_to_df_dict():
    df = ub.to_df({"a": 1, "b": {"c": 2}})

    assert isinstance(df, pd.DataFrame)
    assert df.columns[0] == "DICT_KEY"
    assert set(df["DICT_KEY"]) == {"a", "b"}
    assert df.loc[df["DICT_KEY"] == "a", "VALUE"].iloc[0] == 1
    assert df.loc[df["DICT_KEY"] == "b", "c"].iloc[0] == 2


def test_to_df_list_of_scalars():
    df = ub.to_df(["x", "y"])

    assert list(df.columns) == ["VALUE"]
    assert df["VALUE"].tolist() == ["x", "y"]


@pytest.fixture
def http_file_server(tmp_path: Path):
    (tmp_path / "alpha.txt").write_text("alpha\n", encoding="utf-8")
    (tmp_path / "beta.txt").write_text("beta\n", encoding="utf-8")
    (tmp_path / "spaced.txt").write_text("alpha\n  beta  \n\n", encoding="utf-8")
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()
    (tmp_path / "dir1" / "shared.txt").write_text("dir1\n", encoding="utf-8")
    (tmp_path / "dir2" / "shared.txt").write_text("dir2\n", encoding="utf-8")

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):  # noqa: A003
            return

    handler = partial(QuietHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.fixture
def extensionless_image_server():
    image_buffer = BytesIO()
    Image.new("RGB", (2, 1), color=(255, 0, 0)).save(image_buffer, format="PNG")
    image_payload = image_buffer.getvalue()

    class ImageHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/typed-image":
                content_type = "image/png"
            elif self.path == "/generic-image":
                content_type = "application/octet-stream"
            else:
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(image_payload)))
            self.end_headers()
            self.wfile.write(image_payload)

        def log_message(self, format, *args):  # noqa: A003
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), ImageHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_loads_http_file_mode(http_file_server: str):
    local_path = ub.loads(f"{http_file_server}/alpha.txt", file=True, debug_print=False)

    assert local_path.is_file()
    assert local_path.read_text(encoding="utf-8") == "alpha\n"


def test_loads_http_preserves_loader_kwargs(http_file_server: str):
    data = ub.loads(f"{http_file_server}/spaced.txt", strip=False, skip_empty=True, debug_print=False)

    assert data == ["alpha", "  beta  "]


def test_loads_http_extensionless_image_uses_content_type(
    extensionless_image_server: str, tmp_path: Path
):
    url = f"{extensionless_image_server}/typed-image"

    image = ub.loads(url, target_dir=str(tmp_path), debug_print=False)
    local_path = ub.loads(url, file=True, target_dir=str(tmp_path), debug_print=False)

    assert image.size == (2, 1)
    assert local_path.suffix == ".png"


def test_loads_http_extensionless_image_falls_back_to_pil(
    extensionless_image_server: str, tmp_path: Path
):
    image = ub.loads(
        f"{extensionless_image_server}/generic-image",
        target_dir=str(tmp_path),
        debug_print=False,
    )

    assert image.size == (2, 1)


def test_concurrent_loads_http_extensionless_images(
    extensionless_image_server: str, tmp_path: Path
):
    urls = [
        f"{extensionless_image_server}/typed-image",
        f"{extensionless_image_server}/generic-image",
    ]

    images = ub.concurrent_loads(
        urls,
        num_workers=2,
        target_dir=str(tmp_path),
        debug_print=False,
    )

    assert [image.size for image in images] == [(2, 1), (2, 1)]


def test_concurrent_loads_http_file_mode(http_file_server: str):
    urls = [
        f"{http_file_server}/alpha.txt",
        f"{http_file_server}/beta.txt",
        f"{http_file_server}/alpha.txt",
    ]

    downloaded = ub.concurrent_loads(urls, num_workers=3, file=True, debug_print=False)

    assert [path.read_text(encoding="utf-8") for path in downloaded] == ["alpha\n", "beta\n", "alpha\n"]
    assert downloaded[0] == downloaded[2]


def test_concurrent_loads_http_parses_content(http_file_server: str):
    urls = [
        f"{http_file_server}/alpha.txt",
        f"{http_file_server}/beta.txt",
    ]

    loaded = ub.concurrent_loads(urls, num_workers=2, debug_print=False)

    assert loaded == [["alpha"], ["beta"]]


def test_concurrent_loads_http_keeps_same_basename_urls_distinct(http_file_server: str):
    urls = [
        f"{http_file_server}/dir1/shared.txt",
        f"{http_file_server}/dir2/shared.txt",
    ]

    downloaded = ub.concurrent_loads(urls, num_workers=2, file=True, debug_print=False)

    assert [path.read_text(encoding="utf-8") for path in downloaded] == ["dir1\n", "dir2\n"]
    assert downloaded[0] != downloaded[1]


def test_concurrent_loads_rejects_http_only_kwargs_for_local_file_mode(tmp_path: Path):
    local_path = tmp_path / "local.txt"
    local_path.write_text("local\n", encoding="utf-8")

    with pytest.raises(ValueError, match="only supported for HTTP/HTTPS URIs"):
        ub.concurrent_loads([local_path], file=True, timeout=1, debug_print=False)
