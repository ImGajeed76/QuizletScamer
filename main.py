import time

import cv2
import keyboard
import numpy as np
import pyautogui
import pyperclip
import pyperclip as pc


class QuizletScammer:
    console_image = cv2.imread("images/quizlet-console.png")
    tile_image = cv2.imread("images/quizlet-tile-BGR.png")
    start_image = cv2.imread("images/quizlet-start.png")
    empty_image = cv2.imread("images/quizlet-empty.png")

    time_out = 0
    command = r"setTimeout(() => { " \
              r"let tiles = ''; " \
              r"let classes = document.getElementsByClassName('MatchModeQuestionGridTile-text'); " \
              r"for (const c of classes) { " \
              r"let tile = c.ariaLabel; " \
              r"tiles += tile + ';;';" \
              r"} " \
              r"navigator.clipboard.writeText(tiles);" \
              r"}, $timeout$)"

    words = {}
    tiles = []

    tile_coords = []
    console = ()
    empty = ()

    def __init__(self, words: dict, old_coords: list = None, time_out: float = 150):
        if old_coords is None:
            old_coords = []
        self.tile_coords = old_coords
        self.time_out = time_out
        self.command = self.command.replace("$timeout$", str(self.time_out))
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

    def press_start_btn(self, ss):
        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(self.start_image, ss, method)
        mn, _, mn_loc, _ = cv2.minMaxLoc(result)
        c_x, c_y = mn_loc
        c_x += self.start_image.shape[1] / 2
        c_y += self.start_image.shape[0] / 2
        pyautogui.click(c_x, c_y)
        self.empty = (c_x, c_y - 200)
        return c_x, c_y

    def start(self):
        ss = self.screen_shot()
        ss3 = np.copy(ss)

        self.find_console(ss3)
        p_x, p_y = self.press_start_btn(ss)

        self.get_words()
        pyautogui.position(p_x, p_y)
        self.find_tiles()

        if len(self.tile_coords) == 12:
            self.solve()

        print(len(self.tile_coords), " -> ", self.tile_coords)

    def find_tiles(self, screenshot=None):
        # get tiles
        if not self.tile_coords:
            if screenshot is None:
                screenshot = self.screen_shot()

            method = cv2.TM_CCOEFF_NORMED
            threshold = 0.01

            result = cv2.matchTemplate(self.tile_image, screenshot, method)
            (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
            (y_coords, x_coords) = np.where(result >= maxVal - threshold)
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

                cash.append(word)
                cash.append(other)

                pyautogui.click(self.tile_coords[i][0], self.tile_coords[i][1])
                pyautogui.click(self.tile_coords[other_pos][0], self.tile_coords[other_pos][1])

            if len(cash) == 12:
                break


class QuizletMatcher2:
    words = {}

    console_image_path = r"images/console.png"

    timeout = 500
    console_code = ""
    console_pos = ()
    empty_pos = ()

    new_words = []
    clipboard = ""

    tile_coords = []

    def __init__(self, words: dict, code_file: str, tile_coords: list[tuple[int, int]] = None, cps: float = 0.04):
        if cps < 0.04:
            print("Warning: The cps is probably to small. Quizlet only saves when the time is >= 0.5 seconds.")

        if not tile_coords:
            exit("Error: No tiles_coords found. You should calibrate first and copy the tile coords.")

        self.tile_coords = tile_coords
        pyautogui.PAUSE = cps

        for k, v in words.items():
            self.words.update({k: v, v: k})

        file = open(code_file, 'r')
        self.console_code = file.read()
        self.console_code = self.console_code.replace("$timeout$", str(self.timeout))
        file.close()

    def get_console_pos(self):
        pos = pyautogui.locateOnScreen(self.console_image_path)
        if pos is not None:
            self.console_pos = (pos.left + pos.width, pos.top + (pos.height / 2))
        else:
            print("Waring: Console pos not found")

    def calibrate(self):
        print("(Positions from top left to bottom right)")
        print("(press left shift to save position)")
        for i in range(12):
            print(f"Hover over tile {i + 1}")

            keyboard.wait('left shift')
            p = pyautogui.position()
            self.tile_coords.append((p[0], p[1]))

            while keyboard.press('left shift'):
                pass

        print(f"tile_coords = {self.tile_coords}")

    def run(self):
        print("Starting..")
        time.sleep(5)
        self.empty_pos = pyautogui.position()
        print("Started")

        # run code
        self.get_console_pos()
        pyautogui.click(self.console_pos[0], self.console_pos[1])
        pyperclip.copy(self.console_code)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        pyautogui.click(self.empty_pos[0], self.empty_pos[1])

        # ready
        time.sleep(self.timeout / 1000)
        print("you can start now")

        while pyperclip.paste() == self.console_code:
            pass

        print("got it")
        self.new_words = str(pyperclip.paste()).split(";;")
        self.solve()

    def solve(self):
        cash = ['']
        for i in range(len(self.new_words)):
            word = self.new_words[i]
            if word not in cash:
                other = self.words[word]

                cash.append(word)
                cash.append(other)

                i1 = i
                i2 = self.new_words.index(other)

                p1 = self.tile_coords[i1]
                p2 = self.tile_coords[i2]

                pyautogui.click(p1[0], p1[1])
                pyautogui.click(p2[0], p2[1])

            if len(cash) >= 13:
                exit()


if __name__ == '__main__':
    words = {
        "Auseinandersetzung, Streit": "argument",
        "Kreuzfahrt, Schiffsreise": "cruise",
        "stören": "disturb",
        "Taucher/Taucherin": "diver",
        "sich (zer)streiten": "fall out",
        "Erwärmung der Erdatmosphäre": "global warming",
        "jedoch": "however",
        "glücklicherweise": "luckily",
        "Verschmutzung": "pollution",
        "leider": "sadly",
        "leiden (unter)": "suffer (from)",
        "deshalb, darum": "that's why",
        "bedrohen, drohen": "threaten",
        "unglaublich": "unbelievable",
        "Menge": "amount",
        "meiden, vermeiden": "avoid",
        "konsumieren, zu sich nehmen": "consume",
        "zurzeit, momentan": "currently",
        "schaden, Schaden zufügen": "harm",
        "ignorieren, nicht beachten": "ignore",
        "Überfischen": "overfishing",
        "Politiker/Politikerin": "politician",
        "Meeresfrüchte": "seafood"
    }

    tile_coords = [(1106, 448), (1429, 454), (1712, 448), (1113, 730), (1429, 729), (1724, 730), (1118, 1011),
                   (1441, 1008), (1719, 1011), (1119, 1292), (1414, 1301), (1724, 1293)]

    matcher = QuizletMatcher2(words, "matcher_code.js", tile_coords, 0.04)
    matcher.run()
