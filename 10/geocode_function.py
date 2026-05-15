import requests
import math

API_KEY = 'd504c2d0-69ab-4f12-a7e9-4158d5f66edc'
API_KEY_STATIC = '8888936f-e50b-4137-87db-6b521c398173'

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",  # 🇷🇺
]


def geocode(address):
    url = f'http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            features = data['response']['GeoObjectCollection']['featureMember']
            return features[0]['GeoObject'] if features else None
    except:
        pass
    return None


def coordinates(address):
    obj = geocode(address)
    if not obj:
        return None, None
    lon, lat = obj['Point']['pos'].split()
    return float(lon), float(lat)


def get_ll_span(address):
    obj = geocode(address)
    if not obj:
        return None, None
    lon, lat = obj['Point']['pos'].split()
    ll = f"{lon},{lat}"
    env = obj['boundedBy']['Envelope']
    l, b = env['lowerCorner'].split()
    r, t = env['upperCorner'].split()
    dx = (abs(float(r) - float(l)) or 0.01) * 1.5
    dy = (abs(float(t) - float(b)) or 0.01) * 1.5
    return ll, f"{dx},{dy}"


def calculate_distance(lon1, lat1, lon2, lat2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_pharmacy_color(hours):
    if not hours:
        return 'gr'
    h = str(hours).lower()
    if any(kw in h for kw in ['круглосуточно', '24/7', '24 ч', '24ч', '00:00-23:59', 'нон-стоп']):
        return 'gn'
    if any(c.isdigit() for c in h) or ':' in h:
        return 'bl'
    return 'gr'


def search_pharmacies_overpass(lon, lat, radius_meters=10000, limit=10):
    """Поиск аптек через Overpass API, тк у меня не получилось создать с Яндекс API"""
    pharmacies = []

    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"="pharmacy"](around:{radius_meters},{lat},{lon});
      way["amenity"="pharmacy"](around:{radius_meters},{lat},{lon});
    );
    out center;
    """

    headers = {
        'User-Agent': 'PharmacySearchApp/1.0',
        'Accept': 'application/json'
    }

    for mirror in OVERPASS_MIRRORS:
        try:
            response = requests.post(mirror, data={'data': query}, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
            data = response.json()
            for elem in data.get('elements', []):
                try:
                    coords = elem.get('center') or elem
                    p_lat, p_lon = coords['lat'], coords['lon']
                    dist = calculate_distance(lon, lat, p_lon, p_lat)
                    if dist > radius_meters:
                        continue
                    tags = elem.get('tags', {})
                    pharmacies.append({
                        'name': tags.get('name', tags.get('name:ru', 'Аптека')),
                        'address': tags.get('addr:street', ''),
                        'coordinates': [p_lon, p_lat],
                        'distance': dist,
                        'hours': tags.get('opening_hours', ''),
                        'phone': tags.get('phone', ''),
                        'color': get_pharmacy_color(tags.get('opening_hours', '')),
                        'is_24h': False
                    })
                except:
                    continue
            if pharmacies:
                break
        except:
            continue

    pharmacies.sort(key=lambda x: x['distance'])
    return pharmacies[:limit]


def search_pharmacies_with_expanding_radius(lon, lat, start_radius=500, max_radius=10000, limit=10):
    radius = start_radius
    while radius <= max_radius:
        pharmacies = search_pharmacies_overpass(lon, lat, radius, limit)
        if len(pharmacies) >= limit:
            return pharmacies
        radius += 1000
    return search_pharmacies_overpass(lon, lat, max_radius, limit)
