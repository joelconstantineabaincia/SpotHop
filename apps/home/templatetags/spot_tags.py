from django import template

register = template.Library()

VENUE_COVERS = {
    'CAFE': [
        'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1559925393-8be0ec4767c8?auto=format&fit=crop&w=800&q=80',
    ],
    'LIBRARY': [
        'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1568667256549-094345857637?auto=format&fit=crop&w=800&q=80',
    ],
    'COWORKING': [
        'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1527192491265-7e15c55b1ed2?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80',
    ],
    'LOUNGE': [
        'https://images.unsplash.com/photo-1517502884422-41eaead166d4?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80',
    ],
}

DEFAULT_FALLBACK_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='450' viewBox='0 0 800 450' fill='%23F5F5F4'><rect width='800' height='450' fill='%23F5F5F4'/><path d='M400 190l-60 60h120z' fill='%23D6D3D1'/><text x='400' y='285' font-family='sans-serif' font-size='16' fill='%2378716C' text-anchor='middle'>SpotHop Study Space</text></svg>"

@register.filter
def spot_cover_url(spot):
    """Return a curated architectural cover photo URL for a given StudySpot."""
    if not spot:
        return DEFAULT_FALLBACK_SVG
    cat = (getattr(spot, 'category', '') or 'CAFE').upper()
    pool = VENUE_COVERS.get(cat, VENUE_COVERS['CAFE'])
    spot_id = getattr(spot, 'id', 0) or 0
    return pool[spot_id % len(pool)]

@register.simple_tag
def spot_fallback_svg():
    return DEFAULT_FALLBACK_SVG
