"""Check both PyPI-safe README documents offline, without calling the API."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from readme_renderer.markdown import render

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []
        self.logos = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {"a", "img"}:
            url = attributes.get("href" if tag == "a" else "src")
            if url:
                self.urls.append(url)
        if tag == "img":
            assert attributes.get("alt"), "Image needs descriptive alt text"
            if attributes.get("src") == "https://ionoflux.runvia.app/brand/icon-512.png":
                self.logos += 1


def main() -> None:
    for name in ("README.md", "README.ko.md"):
        body = (ROOT / name).read_text(encoding="utf-8")
        rendered = render(body)
        assert rendered is not None, f"Cannot render {name}"
        links = Links()
        links.feed(rendered)
        assert links.logos == 1, "Official logo must survive PyPI sanitization"
        assert "pip install ionoflux" in body[:1000], "Installation must be prominent"
        for url in links.urls:
            parsed = urlsplit(url)
            assert parsed.scheme == "https" and parsed.netloc, f"Non-absolute HTTPS URL: {url}"
        print(f"{name}: rendered, official logo retained, {len(links.urls)} HTTPS links")


if __name__ == "__main__":
    main()
