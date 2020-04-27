import numpy as np
from PIL import Image

r_text = 189
g_text = 169
b_text = 102

black = np.array([0, 0, 0], dtype=np.uint8)
white = np.array([255, 255, 255], dtype=np.uint8)


def cleanse_numpy(img: Image) -> Image:
    def test(v):
        # print(v)
        if abs(r_text - v[0]) < 70 and abs(g_text - v[1]) < 70 and abs(b_text - v[2]) < 70:
            return black
        return white

    arr = np.asarray(im)
    l = np.apply_along_axis(test, 2, arr)

    # arr = list(im.getdata())
    # l = list(map(test, arr))

    out = Image.fromarray(l)
    return out
    # out.show()

# change all pixels that don't match color to black
##data[np.logical_not(mask)] = black
im: Image = Image.open("C:/Users/jonas/Documents/Github/Warframe/src/warframesc1587918403370823000.png")