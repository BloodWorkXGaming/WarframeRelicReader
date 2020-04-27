import keyboard
from warframe.Screenshot import get_names_from_screenshot


# Press PAGE UP then PAGE DOWN to type "foobar".
keyboard.add_hotkey('ctrl+shift+o', lambda: get_names_from_screenshot(3))
keyboard.add_hotkey('ctrl+shift+p', lambda: get_names_from_screenshot(4))

# Block forever, like `while True`.
keyboard.wait()
