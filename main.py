import cv2
import numpy as np
import pyautogui
import pyperclip as pc


class QuizletScammer:
    console_image = cv2.imread("images/quizlet-console.png")
    tile_image = cv2.imread("images/quizlet-tile.png")
    start_image = cv2.imread("images/quizlet-start.png")
    empty_image = cv2.imread("images/quizlet-empty.png")

    command = r"setTimeout(() => { let tiles = ''; let classes = document.getElementsByClassName('MatchModeQuestionGridTile-text'); for (const c of classes) { let tile = c.ariaLabel; tiles += tile + ';;';} navigator.clipboard.writeText(tiles);}, 150)"

    words = {}
    tiles = []

    tile_coords = []
    console = ()
    empty = ()

    def __init__(self, words: dict, old_coords: list = []):
        self.tile_coords = old_coords
        ks = list(words.keys())

        for i in range(len(words)):
            k = ks[i]
            v = words[k]

            self.words.update({k: v})
            self.words.update({v: k})

    def screen_shot(self):
        img = pyautogui.screenshot()
        open_cv_image = np.array(img)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        return open_cv_image

    def start(self):
        ss = self.screen_shot()
        ss3 = np.copy(ss)

        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(self.start_image, ss, method)
        mn, _, mn_loc, _ = cv2.minMaxLoc(result)
        c_x, c_y = mn_loc
        c_x += self.start_image.shape[1] / 2
        c_y += self.start_image.shape[0] / 2
        pyautogui.click(c_x, c_y)
        self.empty = (c_x, c_y - 200)

        self.find_console(ss3)
        self.get_words()
        pyautogui.position(c_x, c_y)
        self.find_tiles()
        if len(self.tile_coords) == 12:
            self.solve()
        print(len(self.tile_coords), self.tile_coords)

    def find_tiles(self, screenshot = None):
        # get tiles
        if self.tile_coords == []:
            if screenshot is None:
                screenshot = self.screen_shot()
            method = cv2.TM_CCOEFF_NORMED
            threshold = 0.932
            result = cv2.matchTemplate(self.tile_image, screenshot, method)
            (y_coords, x_coords) = np.where(result >= threshold)
            print(len(y_coords))
            print(y_coords, x_coords)
            trows, tcols = self.tile_image.shape[:2]

            for i in range(len(y_coords)):
                self.tile_coords.append((x_coords[i] + tcols, y_coords[i] + trows))

    def find_console(self, screenshot):
        # get console
        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(self.console_image, screenshot, method)
        mn, _, mn_loc, _ = cv2.minMaxLoc(result)
        c_x, c_y = mn_loc
        c_x += self.console_image.shape[1]
        c_y += self.console_image.shape[0] / 2
        self.console = (c_x, c_y)

    def get_words(self):
        # execute command
        pyautogui.click(self.console[0], self.console[1])
        pc.copy(self.command)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press('enter')
        pyautogui.click(self.empty[0], self.empty[1])

        # get data
        self.tiles = str(pc.paste()).split(";;")

    def solve(self):
        # solve
        cash = []
        for i in range(len(self.tiles)):
            word = self.tiles[i]
            if word not in cash:
                other = self.words[word]
                other_pos = self.tiles.index(other)

                print(word, other, other_pos)

                cash.append(word)
                cash.append(other)

                pyautogui.click(self.tile_coords[i][0], self.tile_coords[i][1])
                pyautogui.click(self.tile_coords[other_pos][0], self.tile_coords[other_pos][1])


if __name__ == '__main__':
    words = {
        "remporter": "gewinnen, davontragen",
        "recevoir": "erhalten, bekommen",
        "se partager": "unter sich aufteilen",
        "l'argent (m)": "das Geld/das Silber",
        "l'argent de poche (m)": "das Taschengeld",
        "la monnaie": "das Kleingeld",
        "la pièce (de monnaie)": "die Münze",
        "le billet (de banque)": "die Banknote, der Geldschein",
        "en or": "aus Gold",
        "en argent": "aus Silber",
        "Si j'étais..., je pourrais...": "Wenn ich... wäre, könnte ich...",
        "Si j'avais..., je ferais...": "Wenn ich... hätte, würde ich... machen.",
        "Si je pouvais, j'irais...": "Wenn ich könnte, würde ich... gehen.",
        "dire": "sagen",
        "ajouter": "anfügen",
        "raconter": "erzählen",
        "s'exclamer": "ausrufen",
        "murmurer": "murmeln",
        "chuchoter": "flüstern",
        "Il dit que...": "Er sagt, dass...",
        "Elle raconte que...": "Sie erzählt, dass...",
        "Il demande si...": "Er fragt, ob...",
        "faire tomber": "fallen lassen",
        "faire faire": "machen lassen",
        "faire réparer": "reparieren lassen",
    }

    old_coords = []

    scammer = QuizletScammer(words, old_coords)
    scammer.start()
