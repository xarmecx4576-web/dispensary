import sys
from pharmacy_search import find_and_show_pharmacy


def main():
    address = " ".join(sys.argv[1:])

    try:
        pharmacies = find_and_show_pharmacy(address, limit=10)

        if pharmacies:
            print(f"\nНайдено {len(pharmacies)} аптек")
        else:
            print("\nАптеки не найдены")

    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
