import arcade
import requests
import sys
import os

API_KEY_STATIC = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'Карта: Поиск аптеки'
MAP_FILE = 'map.png'


class GameView(arcade.Window):
    def __init__(self, width, height, title, ll_spn=None, add_params=None):
        super().__init__(width, height, title)
        self.ll_spn = ll_spn
        self.add_params = add_params
        self.background = None

    def setup(self):
        self.get_image()

    def on_draw(self):
        self.clear()

        if self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(
                    (self.width - self.background.width) // 2,
                    (self.height - self.background.height) // 2,
                    self.background.width,
                    self.background.height),
            )

    def get_image(self):
        if self.ll_spn:
            map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&{self.ll_spn}"
        else:
            map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&"

        if self.add_params:
            map_request += '&' + self.add_params

        print(f"Запрос карты: {map_request}")

        response = requests.get(map_request)

        if not response:
            print('Ошибка выполнения запроса:')
            print(map_request)
            print('Http статус:', response.status_code, '(', response.reason, ')')
            sys.exit(1)

        try:
            with open(MAP_FILE, 'wb') as file:
                file.write(response.content)
        except IOError as ex:
            print('Ошибка записи временного файла:', ex)
            sys.exit(1)

        self.background = arcade.load_texture(MAP_FILE)


def show_map(ll_spn=None, add_params=None):
    main(ll_spn, add_params)


def main(ll_spn=None, add_params=None):
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, ll_spn, add_params)
    gameview.setup()
    arcade.run()
    if os.path.exists(MAP_FILE):
        os.remove(MAP_FILE)


if __name__ == '__main__':
    # Пример использования
    show_map('ll=37.617635,55.755814&spn=0.01,0.01')
