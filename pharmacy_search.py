import sys
from geocode_function import (
    coordinates,
    get_ll_span,
    search_pharmacy_nearby,
    calculate_distance
)
from map_api_show import show_map


def format_distance(distance_meters):
    if distance_meters < 1000:
        return f"{distance_meters:.0f} м"
    else:
        return f"{distance_meters / 1000:.2f} км"


def create_pharmacy_snippet(pharmacy, start_address):
    snippet = """
                    БЛИЖАЙШАЯ АПТЕКА                       
 Название:   {name:<50} 
 Адрес:      {address:<50}
 Часы работы: {hours:<50} 
 Телефон:    {phone:<50}
 Расстояние: {distance:<50}
""".format(
        name=pharmacy['name'][:50] if pharmacy['name'] else 'Аптека',
        address=pharmacy['address'][:50] if pharmacy['address'] else 'Не указан',
        hours=pharmacy['hours'][:50] if pharmacy['hours'] else 'Не указано',
        phone=pharmacy['phone'][:50] if pharmacy['phone'] else 'Не указан',
        distance=format_distance(pharmacy['distance'])
    )

    return snippet


def calculate_map_bounds(point1_lon, point1_lat, point2_lon, point2_lat):
    min_lon = min(point1_lon, point2_lon)
    max_lon = max(point1_lon, point2_lon)
    min_lat = min(point1_lat, point2_lat)
    max_lat = max(point1_lat, point2_lat)

    lon_diff = max_lon - min_lon
    lat_diff = max_lat - min_lat

    lon_diff = max(lon_diff, 0.005)
    lat_diff = max(lat_diff, 0.005)

    margin_lon = lon_diff * 0.2
    margin_lat = lat_diff * 0.2

    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    span_lon = lon_diff + 2 * margin_lon
    span_lat = lat_diff + 2 * margin_lat

    ll = f"{center_lon},{center_lat}"
    spn = f"{span_lon},{span_lat}"

    return ll, spn


def find_and_show_pharmacy(address):
    start_lon, start_lat = coordinates(address)

    if start_lon is None or start_lat is None:
        print(f"Не удалось найти координаты для адреса: {address}")
        return

    print(f"Координаты адреса: {start_lon:.6f}, {start_lat:.6f}")

    pharmacy = search_pharmacy_nearby(start_lon, start_lat)

    if not pharmacy:
        print("Аптеки не найдены в радиусе 5 км")
        ll, spn = get_ll_span(address)
        if ll:
            point_param = f'pt={ll},pm2rdm'
            ll_spn = f'll={ll}&spn={spn}'
            show_map(ll_spn, add_params=point_param)
        return

    pharmacy_lon, pharmacy_lat = pharmacy['coordinates']
    print(f"   Найдена аптека: {pharmacy['name']}")
    print(f"   Координаты: {pharmacy_lon:.6f}, {pharmacy_lat:.6f}")
    print(f"   Расстояние: {format_distance(pharmacy['distance'])}")

    snippet = create_pharmacy_snippet(pharmacy, address)
    print(snippet)

    ll, spn = calculate_map_bounds(start_lon, start_lat, pharmacy_lon, pharmacy_lat)

    points_param = f'pt={start_lon},{start_lat},pm2rdm,{pharmacy_lon},{pharmacy_lat},pm2blm'

    ll_spn = f'll={ll}&spn={spn}'

    show_map(ll_spn, add_params=points_param)

    return pharmacy


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    address = " ".join(sys.argv[1:])
    find_and_show_pharmacy(address)


if __name__ == '__main__':
    main()
