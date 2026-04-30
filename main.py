import sys
from pharmacy_search import find_and_show_pharmacy


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    address = " ".join(sys.argv[1:])

    try:
        pharmacy = find_and_show_pharmacy(address)

        if pharmacy:
            print(f"От: {address}")
            print(f"До: {pharmacy['name']}")
            print(f"Расстояние: {pharmacy['distance']:.0f} м")
        else:
            print("\nАптеки не найдены")

    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
