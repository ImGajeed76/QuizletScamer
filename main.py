import cv2
import numpy as np
import pyautogui
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


if __name__ == '__main__':
    words = {
        "la tête": "der Kopf",
        "le cou": "der Hals",
        "le bras": "der Arm",
        "l'épaule (f)": "die Schulter",
        "le coude": "der Ellbogen",
        "la main": "die Hand",
        "le doigt": "der Finger",
        "le dos": "der Rücken",
        "la jambe": "das Bein",
        "le genou": "das Knie",
        "le pied": "der Fuss",
        "croiser": "kreuzen",
        "écarter": "spreizen, ausbreiten",
        "plier": "beugen, falten",
        "tendre": "strecken",
        "baisser": "senken",
        "lâcher": "loslassen",
        "arrêter": "aufhören",
        "recommencer": "wieder beginnen",
        "avancer": "nach vorne strecken",
        "reculer": "zurückziehen, zurückgehen",
        "danser": "tanzen",
        "se lever": "sich setzen",
        "Lève-toi.": "Steh auf.",
        "Levez-vous.": "Steht auf.",
        "sich setzen": "s'asseoir",
        "Assieds-toi.": "Setz dich.",
        "Asseyez-vous.": "Setzt euch.",
        "tenir": "halten",
        "Tiens...": "Halte...",
        "Tenez...": "Haltet...",
        "la plage": "der Strand",
        "la pluie": "der Regen",
        "le vent": "der Wind",
        "la neige": "der Schnee",
        "Tu t'en souviens?": "Erinnerst du dich daran?",
        "J'y pense souvent.": "Ich denke oft daran.",
        "J'en suis fier/fière.": "Ich bin stolz darauf.",
        "On en parle.": "Man spricht darüber.",
        "J'en ai besoin.": "Ich brauche es.",
        "Elle en profite.": "Sie profitiert davon.",
        "Je m'en fous.": "Das ist mir egal.",
        "Je n'en sais rien.": "Ich weiss nichts davon.",
        "Je n'y peux rien.": "Ich kann nichts dafür.",
        "On y va?": "Auf geht's!",
        "J'y vais.": "Ich mache mich auf den Weg.",
        "Vas-y!": "Los! / Mach schon!",
        "Allons-y!": "Auf geht's!",
        "On y est.": "Es ist so weit.",
        "Nous y sommes.": "Da wären wir.",
        "Ca y est.": "Es ist so weit.",
        "Va-t'en!": "Geh weg!",
        "On s'en va.": "Wir gehen jetzt.",
        "Le/La ... qui me plaît est...": "..., der mir gefällt, ist...",
        "Un/Une... qui me fascine est...": "..., der/die mich fasziniert, ist...",
        "Le/La... que je préfère est...": "..., den/die ich bevorzuge, ist...",
        "Le/La... que je trouve bien est...": "..., das ich gut finde, ist...",
    }

    old_coords = [(281, 218), (597, 218), (913, 218), (281, 415), (597, 415), (913, 415), (281, 613), (597, 613),
                  (913, 613), (281, 810), (597, 810), (913, 810)]

    scammer = QuizletScammer(words, old_coords, 115)
    scammer.start()
