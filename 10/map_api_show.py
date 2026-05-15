import arcade
import requests
import sys
import os

API_KEY_STATIC = '8888936f-e50b-4137-87db-6b521c398173'

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'Карта: Аптеки'
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
            x = (self.width - self.background.width) // 2
            y = (self.height - self.background.height) // 2
            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(x, y, self.background.width, self.background.height)
            )

    def get_image(self):
        if self.ll_spn:
            map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&{self.ll_spn}"
        else:
            map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&"

        if self.add_params:
            map_request += '&' + self.add_params

        try:
            response = requests.get(map_request, timeout=15)
            if not response or response.status_code != 200:
                print('Ошибка выполнения запроса:')
                print(map_request)
                if response:
                    print(f'Статус: {response.status_code} ({response.reason})')
                    print(f'Ответ: {response.text[:300]}')
                sys.exit(1)

            with open(MAP_FILE, 'wb') as file:
                file.write(response.content)

            self.background = arcade.load_texture(MAP_FILE)

        except Exception as e:
            print(f'Ошибка загрузки карты: {e}')
            sys.exit(1)


def show_map(ll_spn=None, add_params=None):
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, ll_spn, add_params)
    gameview.setup()
    arcade.run()

    if os.path.exists(MAP_FILE):
        try:
            os.remove(MAP_FILE)
        except:
            pass


if __name__ == '__main__':
    show_map('ll=37.617635,55.755814&spn=0.01,0.01')
