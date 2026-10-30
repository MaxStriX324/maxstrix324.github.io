#!/usr/bin/env python3
"""One-time, reproducible import of original PAZ-3206 photos from the user's DRIVE2 PDF.

The source URLs were read from clickable image annotations in 18.pdf
("Перенос аварийной двери ... Часть 1"), pages 2, 9, 13, 14, 21, 28.
Images are re-encoded to WebP and stored in the GitHub Pages repository.
"""
import io
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "projects" / "paz-3206"
SOURCE = "https://www.drive2.ru/l/746631068496444355/"
PHOTOS = [
    ("emergency-door-before", 2, "Аварийная дверь до демонтажа", "_ZJei37iTK02Leg3DsY0xog4h_M"),
    ("door-opening", 9, "Проём после демонтажа аварийной двери", "xjiKaQDu_JPHlMrrXH3FDTYFKVs"),
    ("removed-door", 9, "Снятая аварийная дверь рядом с автобусом", "ZgVVNwtRkHDzJnMJmlvpFfNPZFE"),
    ("door-fitted", 13, "Примерка листа при закрытии проёма", "SQPKdlbQafmoYE2AcDXu_aDJJmc"),
    ("closed-opening", 14, "Закрываем старый проём аварийной двери", "hTMfZVxYD67g7w7S9fMzt8aEVKw"),
    ("saloon-disassembly", 21, "Разобранный салон автобуса", "kGe1-Sog3YpS9sxzSg091vYWkeY"),
    ("paz-exterior", 21, "Внешний вид ПАЗ-3206 во время переделки", "bdKpD7BtLLqiMtnY8NEz1gyMPDQ"),
    ("body-restoration", 22, "Промежуточные результаты работ по кузову", "JzKVf5Be5Jut4jTd3BYV3PA0dEs"),
    ("additional-parts", 28, "Дополнительные детали для переделки автобуса", "R-WT2y0mNg7SqjYH9uc-VemnhZw"),
]

def fetch_image(url: str) -> bytes:
    for attempt in range(3):
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MaxStriX324Site/1.0)",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": "https://www.drive2.ru/",
            })
            with urlopen(req, timeout=25) as response:
                data = response.read(12 * 1024 * 1024 + 1)
                ctype = response.headers.get("Content-Type", "")
                if len(data) > 12 * 1024 * 1024:
                    raise ValueError("Image too large")
                if not ctype.startswith("image/"):
                    raise ValueError(f"Not an image: {ctype!r}")
                return data
        except Exception as exc:
            if attempt == 2:
                raise RuntimeError(f"Could not fetch {url}: {exc}") from exc
            time.sleep(2 + attempt * 2)
    raise AssertionError("unreachable")

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    metadata = []
    for name, page, caption, code in PHOTOS:
        url = f"https://a1.drive-data.ru/{code}-1920.jpg"
        raw = fetch_image(url)
        try:
            im = Image.open(io.BytesIO(raw))
            im.load()
            im = ImageOps.exif_transpose(im).convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise RuntimeError(f"Invalid image: {url}") from exc
        im.thumbnail((1400, 1200), Image.Resampling.LANCZOS)
        path = DEST / f"{name}.webp"
        im.save(path, "WEBP", quality=80, method=6)
        metadata.append({
            "name": name,
            "caption": caption,
            "source_article": SOURCE,
            "source_pdf": "18.pdf",
            "source_pdf_page": page,
            "original_url": url,
            "path": f"/assets/projects/paz-3206/{name}.webp",
            "width": im.width,
            "height": im.height,
        })
        print(f"{name}: {im.width}x{im.height}, {path.stat().st_size} bytes")
    (DEST / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Imported {len(metadata)} image(s)")

if __name__ == "__main__":
    main()
