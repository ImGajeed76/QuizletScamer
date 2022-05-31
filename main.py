import time

import cv2
import numpy as np
import pyautogui
import pyperclip as pc


class QuizletScamer:
    console_image = cv2.imread("images/quizlet-console.png")
    tile_image = cv2.imread("images/quizlet-tile.png")
    start_image = cv2.imread("images/quizlet-start.png")

    timeOut = 2000

    command = r"setTimeout(() => { let tiles = ''; let classes = document.getElementsByClassName('MatchModeQuestionGridTile-text'); for (const c of classes) { let tile = c.ariaLabel; tiles += tile + ';;';} navigator.clipboard.writeText(tiles);}, 120)"

    words = {}
    tiles = []

    tile_coords = []
    console = ()
    empty = ()

    def __init__(self, words: dict):
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

        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(self.start_image, ss, method)
        mn, _, mn_loc, _ = cv2.minMaxLoc(result)
        c_x, c_y = mn_loc
        c_x += self.console_image.shape[1]
        c_y += self.console_image.shape[0] / 2
        pyautogui.click(c_x, c_y)

        result = cv2.matchTemplate(self.start_image, ss, method)
        mn, _, mn_loc, _ = cv2.minMaxLoc(result)
        c_x, c_y = mn_loc
        c_x += self.console_image.shape[1]
        c_y += self.console_image.shape[0] / 2
        self.empty = (c_x, c_y)

        self.find(ss)
        self.get()
        time.sleep(1)
        self.find_tiles(ss)
        self.solve()

    def find_tiles(self, screenshot):
        # get tiles
        method = cv2.TM_CCOEFF_NORMED
        threshold = 0.923
        result = cv2.matchTemplate(self.tile_image, screenshot, method)
        (y_coords, x_coords) = np.where(result >= threshold)
        trows, tcols = self.tile_image.shape[:2]

        for i in range(len(y_coords)):
            self.tile_coords.append((x_coords[i] + tcols, y_coords[i] + trows))

    def find(self, screenshot):
        # get console
        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(self.console_image, screenshot, method)
        mn, _, mn_loc, _ = cv2.minMaxLoc(result)
        c_x, c_y = mn_loc
        c_x += self.console_image.shape[1]
        c_y += self.console_image.shape[0] / 2
        self.console = (c_x, c_y)

    def get(self):
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
        for i in range(len(self.words)):
            k = list(self.words.keys())[i]
            v = list(self.words.values())[i]

            if k in self.tiles:
                pos = self.tiles.index(v)
                pyautogui.click(self.tile_coords[pos][0], self.tile_coords[pos][1])
                pyautogui.click(self.tile_coords[i][0], self.tile_coords[i][1])


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

    scammer = QuizletScamer(words)
    scammer.start()
