import requests
import math

API_KEY = '8013b162-6b42-4997-9691-77b7074026e0'
API_KEY_SEARCH = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'


def geocode(address):
    geocoder_request = f'http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json'
    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
    else:
        raise RuntimeError(
            f"Ошибка выполнения запроса: {geocoder_request}")

    features = json_response['response']['GeoObjectCollection']['featureMember']
    return features[0]['GeoObject'] if features else None


def coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    toponym_coordinates = toponym['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split()
    return float(toponym_longitude), float(toponym_lattitude)


def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return (None, None)

    toponym_coordinates = toponym['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split()

    ll = ','.join([toponym_longitude, toponym_lattitude])
    envelope = toponym['boundedBy']['Envelope']

    l, b = envelope['lowerCorner'].split(" ")
    r, t = envelope['upperCorner'].split(" ")

    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    span = f'{dx},{dy}'

    return ll, span


def calculate_distance(lon1, lat1, lon2, lat2):
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def search_pharmacy_nearby(lon, lat, radius=5000):
    search_request = f'https://search-maps.yandex.ru/v1/'
    params = {
        'apikey': API_KEY_SEARCH,
        'text': 'аптека',
        'll': f'{lon},{lat}',
        'spn': f'{radius / 111000:.4f},{radius / 111000:.4f}',
        'type': 'biz',
        'lang': 'ru_RU',
        'results': '10'
    }

    response = requests.get(search_request, params=params)

    if not response:
        print(f'Ошибка выполнения запроса поиска аптек:')
        return None

    try:
        json_response = response.json()
        features = json_response.get('features', [])

        if not features:
            return None

        nearest_pharmacy = None
        min_distance = float('inf')

        for feature in features:
            pharmacy_coords = feature['geometry']['coordinates']
            pharmacy_lon, pharmacy_lat = pharmacy_coords

            distance = calculate_distance(lon, lat, pharmacy_lon, pharmacy_lat)

            if distance < min_distance:
                min_distance = distance
                nearest_pharmacy = {
                    'name': feature['properties'].get('name', 'Аптека'),
                    'address': feature['properties'].get('address', ''),
                    'coordinates': pharmacy_coords,
                    'distance': distance,
                    'hours': feature['properties'].get('openingHours', {}).get('text', 'Не указано'),
                    'phone': feature['properties'].get('phone', ''),
                    'companyMetaData': feature.get('properties', {}).get('CompanyMetaData', {})
                }

        return nearest_pharmacy

    except Exception as e:
        print(f'Ошибка обработки ответа: {e}')
        return None


def get_pharmacy_details(pharmacy_id):
    pass
