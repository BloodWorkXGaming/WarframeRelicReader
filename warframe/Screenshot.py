from PIL import ImageGrab
from PIL import Image
import pytesseract
from PIL import ImageEnhance
import requests
from warframe.marketReq import get_price_from_id
import re
from warframe.image_cleanser import cleanse_numpy
import threading
import _thread
import multiprocessing as mp

import time
import numpy as np

box_width = 480
top_pos = (825, 875)
bottom_pos = (870, 920)


class ReadingThread(threading.Thread):
    def __init__(self, threadID: int, img: Image, left: int):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.img = img
        self.left = left

    def run(self):
        read_from_left_pos(self.img, self.left)


def strip_name(name: str) -> str:
    cleaned = " "
    last_char_space = True
    name = name.replace("ı", "i").replace(" : ", ":")
    has_colon = False

    for c in name:
        if not (c.isalpha() or c == ":" or c == " "):
            continue
        if c == ":" and has_colon:
            continue
        if c.isupper() and not last_char_space:
            cleaned += " "

        if c == ":":
            has_colon = True
        cleaned += c
        last_char_space = c == " "

    cleaned = cleaned.strip().replace("   ", " ").replace("  ", " ").strip()

    return cleaned


mapping = {
    "Prime:? Chassis Blaupause": "prime_chassis",
    "Prime:? Neuroptik Blaupause": "prime_neuroptics",
    "Prime:? Systeme Blaupause": "prime_systems",
    "Prime:? Gehause": "prime_receiver",
    "Prime:? Gehäuse": "prime_receiver",
    "Prime:? Lauf": "prime_barrel",
    "Prime:? Verbindung": "prime_link",
    "Prime:? Ornament": "prime_ornament",
    "Prime:? Schaft": "prime_stock",
    "Prime:? Griff": "prime_handle",
    "Prime:? Klinge": "prime_blade",
    "Prime:? Cerebrum": "prime_cerebrum",
    "Prime:? Panzer": "prime_carapace",
    "Prime:? Sterne": "prime_stars",
    "Prime:? Tasche": "prime_pouch",
    "Prime:? Unterteil": "prime_lower_limb",
    "Prime:? Oberteil": "prime_upper_limb",
    "Prime:? Sehne": "prime_string",
    "Prime Blaupause": "prime_blueprint",
}


def to_url_id(name: str) -> str:
    for k, v in mapping.items():
        name = re.sub(k, v, name)
        # name = name.replace(k, v)

    name = name.replace(" ", "_").lower().strip()
    return name


def check_valid_name(name: str) -> bool:
    last_space = 0
    for c in strip_name(name.strip()):
        if c == " ":
            if last_space < 2:
                return False
            last_space = 0
        else:
            last_space += 1

    return True


def get_names_from_file(img: Image, player_count: int):
    print()
    print()
    print()
    print()
    print()
    print("Loading for " + str(player_count) + " Players")
    left_pos = []

    if player_count == 3:
        left_pos.append(1200)
        left_pos.append(1680)
        left_pos.append(2165)

    if player_count == 4:
        left_pos.append(960)
        left_pos.append(1440)
        left_pos.append(1925)
        left_pos.append(2410)

    threads = []
    for left in left_pos:
        # t = ReadingThread(len(threads), img, player_count)
        p = mp.Process(target=read_from_left_pos, args=(img, left))
        threads.append(p)
        p.start()

    for t in threads:
        t.join()


def read_from_left_pos(img: Image, left: int):
    cropped_top = img.crop((left, top_pos[0], left + box_width, top_pos[1]))
    cropped_bottom = img.crop((left, bottom_pos[0], left + box_width, bottom_pos[1]))

    ctop = ImageEnhance.Sharpness(cropped_top).enhance(1)
    cbot = ImageEnhance.Sharpness(cropped_bottom).enhance(1)

    cropped_top = cleanse_img(ctop)
    cropped_bottom = cleanse_img(cbot)
    #
    # ctop = ImageEnhance.Contrast(cropped_top).enhance(1)
    # cbot = ImageEnhance.Contrast(cropped_bottom).enhance(1)
    #
    # cropped_top = ctop
    # cropped_bottom = cbot
    #
    read_top = pytesseract.image_to_string(cropped_top, config="--oem 3 --psm 13", lang="deu")
    read_bottom = pytesseract.image_to_string(cropped_bottom, config="--oem 3 --psm 13", lang="deu")

    # print(read_top)
    # print(read_bottom)

    if 4 < len(read_bottom) < 10 and read_bottom.startswith("B") and read_bottom.endswith("e"):
        read_bottom = "Blaupause"

    lines = read_top.splitlines() + read_bottom.splitlines()
    name_total = " ".join(filter(lambda l: len(l) > 8 and check_valid_name(l), lines))
    fullname = strip_name(name_total)

    if fullname == "Forma Blaupause":
        print("#############################"
              "\nForma Blueprint"
              "\nWoooooooooooooo kann man das kaufen?"
              "\n#############################")
        return

    url_id = to_url_id(fullname)
    # print(fullname)
    # print("url id: " + url_id)

    prices_str = get_price_from_id(url_id)
    print("#############################\n"
          + fullname + "\n"
          + prices_str + "\n"
          + "#############################")

    # cropped_top.show()
    # cropped_bottom.show()


def cleanse_img(im: Image) -> Image:
    im.getdata()
    out = Image.new('RGB', im.size, 0xffffff)

    r_text = 189
    g_text = 169
    b_text = 102

    width, height = im.size
    for x in range(width):
        for y in range(height):
            r, g, b = im.getpixel((x, y))
            if abs(r_text - r) < 70 and abs(g_text - g) < 70 and abs(b_text - b) < 70:
                out.putpixel((x, y), 0)

    return out


def get_names_from_screenshot(player_count: int):
    img = ImageGrab.grab()
    # img: Image = Image.open("./warframerelics" + str(player_count) + ".png")
    img.save("C:/Users/jonas/Documents/Github/Warframe/src/warframesc" + str(time.time_ns()) + ".png")
    get_names_from_file(img, player_count)


if __name__ == "__main__":
    # get_names_from_screenshot(4)

    # img = Image.open("C:/Users/jonas/Documents/Github/Warframe/src/warframerelics3.png")
    im = Image.open("C:/Users/jonas/Documents/Github/Warframe/src/warframesc1587921614099171500.png")
    get_names_from_file(im, 4)
