import cv2
import numpy as np
import pyautogui
import pyperclip as pc


class QuizletScamer:
    console_image = cv2.imread("images/quizlet-console.png")
    tile_image = cv2.imread("images/quizlet-tile.png")

    command = r"test"

    words = []
    tiles = []

    tile_coords = []
    console = ()

    def __init__(self, words):
        self.words = words

    def screen_shot(self):
        img = pyautogui.screenshot()
        open_cv_image = np.array(img)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        return open_cv_image

    def find(self, screenshot):
        # get console
        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(self.console_image, screenshot, method)
        mn, _, mn_loc, _ = cv2.minMaxLoc(result)
        c_x, c_y = mn_loc
        c_x += self.console_image.shape[1]
        c_y += self.console_image.shape[0] / 2
        self.console = (c_x, c_y)

        # get tiles
        method = cv2.TM_CCOEFF_NORMED
        threshold = 0.923
        result = cv2.matchTemplate(self.tile_image, screenshot, method)
        (y_coords, x_coords) = np.where(result >= threshold)

        for i in range(len(y_coords)):
            self.tile_coords.append((x_coords[i], y_coords[i]))

    def run(self):
        # execute command
        pyautogui.click(self.console[0], self.console[1])
        pyautogui.write(self.command)
        pyautogui.press('enter')

        # get data
        self.tiles = list(pc.paste())

        # sort


if __name__ == '__main__':
    words = {

    }

    scammer = QuizletScamer(words)
    scammer.find(scammer.screen_shot())
    scammer.run()
    print(scammer.console)
    print(scammer.tile_coords)
    print(len(scammer.tile_coords))
