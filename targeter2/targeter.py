"""
Randomly point a target in a picture.

Usage:
    targeter.py PICTURE_FILE


Press enter to add a new target, backspace to remove the last target from the picture, and escape
to quit. You can also press 'r' to do both, the removing of the last target and the adding of a
new one (typical use: "last target wasn't good, re-roll!")

Also, you can use the zoom controls of the picture to zoom in into the targets, and keys will keep
working as intended. Try it out! :)
"""
import random
import sys
from pathlib import Path

from docopt import docopt
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image


TARGET_FACTOR = 0.09


class Status:
    def __init__(self):
        self.targets = []
        self.keep_targetting = True


def targets_loop(picture):
    """
    Loop where the user interacts with the picture by adding and removing targets.
    """
    status = Status()

    max_width, max_height = picture.size
    target_size = min((max_width * TARGET_FACTOR, max_height * TARGET_FACTOR))

    def add_target():
        new_target = random.randint(0, max_width), random.randint(0, max_height)
        status.targets.append(new_target)
        print('New target:', new_target)

    def remove_target():
        if status.targets:
            print('Remove last target')
            status.targets.pop()
        else:
            print('No targets to remove')

    def draw_target(position, color):
        x, y = position
        vertical_line = Rectangle((x, y - target_size / 2), 0, target_size,
                                  linewidth=3, edgecolor=color, facecolor='none')
        horizontal_line = Rectangle((x - target_size / 2, y), target_size, 0,
                                    linewidth=3, edgecolor=color, facecolor='none')
        selection = fig.add_subplot(111)
        selection.add_patch(vertical_line)
        selection.add_patch(horizontal_line)

    def on_key(event):
        if event.key == 'escape':
            # stop targetting
            print('Have a nice day :)')
            status.keep_targetting = False
            plt.close('all')
        elif event.key == 'enter':
            add_target()
            plt.close('all')
        elif event.key == 'backspace':
            remove_target()
            plt.close('all')
        elif event.key == 'r':
            remove_target()
            add_target()
            plt.close('all')

    while status.keep_targetting:
        ax = plt.imshow(picture)

        fig = ax.get_figure()
        fig.canvas.set_window_title("Random targets!!")

        fig.canvas.mpl_connect('key_press_event', on_key)

        fig.tight_layout()

        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())

        plt.axis('off')

        last_target = len(status.targets) - 1
        for target_number, target in enumerate(status.targets):
            if target_number == last_target:
                color = (0.5, 1, 0, 0.7)
            else:
                color = 'r'
            draw_target(target, color)

        plt.show(block=True)


if __name__ == '__main__':
    opts = docopt(__doc__)
    picture_path = Path(opts['PICTURE_FILE'])

    if not picture_path.exists():
        print("No picture found in the specified path")
        sys.exit(1)

    picture = Image.open(picture_path)
    targets_loop(picture)
