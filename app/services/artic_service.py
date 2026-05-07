import httpx
from typing import Optional

ARTIC_BASE_URL = "https://api.artic.edu/api/v1"

_cache: dict[str, dict] = {}


async def get_artwork(external_id: str) -> Optional[dict]:
    if external_id in _cache:
        return _cache[external_id]

    url = f"{ARTIC_BASE_URL}/artworks/{external_id}"
    params = {"fields": "id,title,image_id,thumbnail"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    data = response.json().get("data")
    if not data:
        return None

    artwork = {
        "external_id": str(data["id"]),
        "title": data.get("title"),
        "image_url": _build_image_url(data.get("image_id")),
    }
    _cache[external_id] = artwork
    return artwork


async def validate_artwork(external_id: str) -> bool:
    result = await get_artwork(external_id)
    return result is not None


def _build_image_url(image_id: Optional[str]) -> Optional[str]:
    if not image_id:
        return None
    return f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
