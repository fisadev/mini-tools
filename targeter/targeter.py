#!/usr/bin/python
import Image, ImageDraw
import subprocess
import random
import wx
import cv


class Targeter(wx.Frame):
    def __init__(self):
        super(Targeter, self).__init__(None, -1, 'Winner targeter', size=(300, 100))
        # target button
        button = wx.Button(self, -1, 'Target!')
        button.Bind(wx.EVT_LEFT_UP, self.on_target)

        # we will be storing the picture, just in case
        self.image_path = 'picture.jpg'

        # initialize camera
        self.capture = cv.CaptureFromCAM(0)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 1024)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 1280)

    def on_target(self, event):
        # take picture and save it (5 times because, you know, 5 is more than 1)
        for _ in range(5):
            image = cv.QueryFrame(self.capture)
        cv.SaveImage(self.image_path, image)

        # open image and start drawing
        image = Image.open(self.image_path)
        draw = ImageDraw.Draw(image)

        # calculate needed drawing data
        width, height = image.size
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = width / 30
        line_width = size / 20
        line_color = '#00FF00'

        # draw reticle
        draw.ellipse((x - size / 2, y - size / 2, x + size / 2, y + size / 2))
        draw.line((x, y - size, x, y + size), fill=line_color, width=line_width)
        draw.line((x - size, y, x + size, y), fill=line_color, width=line_width)

        # save image with reticle
        image.save(self.image_path)

        # open eog to display the image
        subprocess.call(['eog', self.image_path])


if __name__ == '__main__':
    app = wx.App()
    targeter = Targeter()
    targeter.Show()
    app.MainLoop()
