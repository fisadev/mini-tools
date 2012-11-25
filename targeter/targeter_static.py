#!/usr/bin/python
import Image
import ImageDraw
import subprocess
import random
import wx


class Targeter(wx.Frame):
    def __init__(self):
        super(Targeter, self).__init__(None, -1, 'Winner targeter', size=(250, 100))
        self.base_image_path = 'picture.jpg'
        self.image_path = 'picture_modified.jpg'

        button = wx.Button(self, -1, 'Target!')

        button.Bind(wx.EVT_LEFT_UP, self.on_target)

    def on_target(self, event):
        image = Image.open(self.base_image_path)
        draw = ImageDraw.Draw(image)

        width, height = image.size

        x = random.randint(0, width)
        y = random.randint(0, height)
        size = width / 30
        line_width = size / 20
        line_color = '#00FF00'

        draw.line((x, y - size, x, y + size), fill=line_color, width=line_width)
        draw.line((x - size, y, x + size, y), fill=line_color, width=line_width)
        image.save(self.image_path)

        subprocess.call(['eog', self.image_path])


def run():
    app = wx.App()

    targeter = Targeter()
    targeter.Show()

    app.MainLoop()


if __name__ == '__main__':
    run()
