import sys
from geocode_function import (
    coordinates,
    get_ll_span,
    search_pharmacies_with_expanding_radius
)
from map_api_show import show_map


def format_distance(distance_meters):
    if distance_meters < 1000:
        return f"{distance_meters:.0f} м"
    return f"{distance_meters / 1000:.2f} км"


def print_pharmacy_table(pharmacies, start_address):
    print(f" ")
    print(f"{'№'} {'Название'} {'Расстояние'} {'Режим работы'}")

    for i, p in enumerate(pharmacies, 1):
        if p['color'] == 'gn':
            status_text = "КРУГЛОСУТОЧНО"
        elif p['color'] == 'bl':
            status_text = "ДНЕВНАЯ"
        else:
            status_text = "НЕТ ДАННЫХ"

        name = p['name']
        if len(name) > 28:
            name = name[:25] + "..."

        dist_str = format_distance(p['distance'])

        hours = p['hours'][:25] + "..." if len(p['hours']) > 28 else p['hours']
        hours_display = hours if hours and p['color'] != 'gr' else ""

        print(f"{i} {name} {dist_str} {hours_display}")

    stats = {'gn': 0, 'bl': 0, 'gr': 0}
    for p in pharmacies:
        stats[p['color']] += 1

    print(f"Круглосуточных: {stats['gn']}")
    print(f"Дневных: {stats['bl']}")
    print(f"Без данных: {stats['gr']}")


def calculate_map_bounds_with_points(points):
    if not points:
        return None, None

    lons = [p[0] for p in points]
    lats = [p[1] for p in points]

    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    lon_diff = max(max_lon - min_lon, 0.01)
    lat_diff = max(max_lat - min_lat, 0.01)

    margin_lon = lon_diff * 0.3
    margin_lat = lat_diff * 0.3

    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    span_lon = lon_diff + 2 * margin_lon
    span_lat = lat_diff + 2 * margin_lat

    span_lon = min(max(span_lon, 0.02), 0.5)
    span_lat = min(max(span_lat, 0.02), 0.5)

    return f"{center_lon},{center_lat}", f"{span_lon},{span_lat}"


def create_colored_points_param(start_lon, start_lat, pharmacies):
    color_map = {
        'gn': 'pm2gnm',  # зелёный
        'bl': 'pm2blm',  # синий
        'gr': 'pm2grm'  # серый
    }
    # Красная точка - мое местоположение
    points = [f'{start_lon},{start_lat},pm2rdm']

    for p in pharmacies[:15]:
        lon, lat = p['coordinates']
        color_code = color_map.get(p['color'], 'pm2blm')
        points.append(f'{lon},{lat},{color_code}')

    return '~'.join(points)


def find_and_show_pharmacy(address, limit=10):
    print(f"\nАдрес: {address}")

    start_lon, start_lat = coordinates(address)
    print(f"Ваши координаты: {start_lon:.5f}, {start_lat:.5f}")

    pharmacies = search_pharmacies_with_expanding_radius(
        start_lon, start_lat,
        start_radius=500,
        max_radius=10000,  # 10 км
        limit=limit
    )

    if not pharmacies:
        print("\nАптеки не найдены в радиусе 10 км")
        print("Попробуйте другой адрес")

        ll, spn = get_ll_span(address)
        if ll:
            show_map(f'll={ll}&spn={spn}', add_params=f'pt={start_lon},{start_lat},pm2rdm')
        return None

    print_pharmacy_table(pharmacies, address)

    all_points = [(start_lon, start_lat)] + [tuple(p['coordinates']) for p in pharmacies]
    ll, spn = calculate_map_bounds_with_points(all_points)
    points_param = create_colored_points_param(start_lon, start_lat, pharmacies)

    map_params = f'size=650,450&pt={points_param}&l=map'
    show_map(f'll={ll}&spn={spn}', add_params=map_params)

    return pharmacies


def main():
    address = " ".join(sys.argv[1:])
    find_and_show_pharmacy(address, limit=10)


if __name__ == '__main__':
    main()
