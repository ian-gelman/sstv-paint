from __future__ import division
from tkinter import *
from pysstv.sstv import SSTV
from time import sleep
from itertools import islice
from PIL import Image
from pysstv.color import Robot36
import datetime
import tkinter.font as font
import pyscreenshot as ImageGrab
import struct, pyaudio
from tkinter.colorchooser import *

class PyAudioSSTV(object):
    def __init__(self, sstv):
        self.pa = pyaudio.PyAudio()
        self.sstv = sstv
        self.fmt = '<' + SSTV.BITS_TO_STRUCT[sstv.bits]

    def __del__(self):
        self.pa.terminate()

    def execute(self):
        self.sampler = self.sstv.gen_samples()
        stream = self.pa.open(
                format=self.pa.get_format_from_width(self.sstv.bits // 8),
                channels=1, rate=self.sstv.samples_per_sec, output=True,
                stream_callback=self.callback)
        stream.start_stream()
        while stream.is_active():
            sleep(0.5)
        stream.stop_stream()
        stream.close()

    def callback(self, in_data, frame_count, time_info, status):
        frames = b''.join(struct.pack(self.fmt, b)
                for b in islice(self.sampler, frame_count))
        return frames, pyaudio.paContinue

class PaintApp:

    # Stores current drawing tool used
    drawing_tool = "pencil"

    color = "red"

    size = 8

    # Tracks whether left mouse is down
    left_but = "up"

    # x and y positions for drawing with pencil
    x_pos, y_pos = None, None

    # Tracks x & y when the mouse is clicked and released
    x1_line_pt, y1_line_pt, x2_line_pt, y2_line_pt = None, None, None, None

    # ---------- CATCH MOUSE UP ----------

    def left_but_down(self, event=None):
        self.left_but = "down"

        # Set x & y when mouse is clicked
        self.x1_line_pt = event.x
        self.y1_line_pt = event.y

    # ---------- CATCH MOUSE UP ----------

    def left_but_up(self, event=None):
        self.left_but = "up"

        # Reset the line
        self.x_pos = None
        self.y_pos = None

        # Set x & y when mouse is released
        self.x2_line_pt = event.x
        self.y2_line_pt = event.y

        # If mouse is released and line tool is selected
        # draw the line
        if self.drawing_tool == "line":
            self.line_draw(event)
        elif self.drawing_tool == "arc":
            self.arc_draw(event)
        elif self.drawing_tool == "oval":
            self.oval_draw(event)
        elif self.drawing_tool == "rectangle":
            self.rectangle_draw(event)
        elif self.drawing_tool == "text":
            self.text_draw(event)

    # ---------- CATCH MOUSE MOVEMENT ----------

    def motion(self, event=None):

        if self.drawing_tool == "pencil":
            self.pencil_draw(event)

    # ---------- DRAW PENCIL ----------

    def pencil_draw(self, event=None):
        if self.left_but == "down":

            # Make sure x and y have a value
            if self.x_pos is not None and self.y_pos is not None:
                radius = self.size/2
                event.widget.create_line(self.x_pos, self.y_pos, event.x, event.y, smooth=TRUE, width=self.size, fill=self.color)
                event.widget.create_oval(event.x-radius, event.y+radius, event.x+radius, event.y-radius, fill=self.color, width=0)

            self.x_pos = event.x
            self.y_pos = event.y

    # ---------- DRAW LINE ----------

    def line_draw(self, event=None):

        # Shortcut way to check if none of these values contain None
        if None not in (self.x1_line_pt, self.y1_line_pt, self.x2_line_pt, self.y2_line_pt):
            event.widget.create_line(self.x1_line_pt, self.y1_line_pt, self.x2_line_pt, self.y2_line_pt, smooth=TRUE, fill="green")

    # ---------- DRAW ARC ----------

    def arc_draw(self, event=None):

        # Shortcut way to check if none of these values contain None
        if None not in (self.x1_line_pt, self.y1_line_pt, self.x2_line_pt, self.y2_line_pt):

            coords = self.x1_line_pt, self.y1_line_pt, self.x2_line_pt, self.y2_line_pt

            # start : starting angle for the slice in degrees
            # extent : width of the slice in degrees
            # fill : fill color if needed
            # style : can be ARC, PIESLICE, or CHORD
            event.widget.create_arc(coords, start=0, extent=150, style=ARC)

    # ---------- DRAW OVAL ----------

    def oval_draw(self, event=None):
        if None not in (self.x1_line_pt, self.y1_line_pt, self.x2_line_pt,self.y2_line_pt):

            # fill : Color option names are here http://wiki.tcl.tk/37701
            # outline : border color
            # width : width of border in pixels

            event.widget.create_oval(self.x1_line_pt, self.y1_line_pt,
					self.x2_line_pt, self.y2_line_pt,
                                        fill="midnight blue",
                                        outline="yellow",
                                        width=2)

    # ---------- DRAW RECTANGLE ----------

    def rectangle_draw(self, event=None):
        if None not in (self.x1_line_pt, self.y1_line_pt, self.x2_line_pt, self.y2_line_pt):

            # fill : Color option names are here http://wiki.tcl.tk/37701
            # outline : border color
            # width : width of border in pixels

            event.widget.create_rectangle(self.x1_line_pt, self.y1_line_pt, self.x2_line_pt, self.y2_line_pt,
                fill="midnight blue",
                outline="yellow",
                width=2)

    # ---------- DRAW TEXT ----------

    def text_draw(self, event=None):
        if None not in (self.x1_line_pt, self.y1_line_pt):
            # Show all fonts available
            print(tkinter.font.families())

            text_font = tkinter.font.Font(family='Helvetica',
            size=20, weight='bold', slant='italic')

            event.widget.create_text(self.x1_line_pt, self.y1_line_pt,
                                      fill="green",
                                      font=text_font,
                                      text="WOW")

    def grab_n_send(self, event=None):
        x0 = int(self.drawing_area.winfo_rootx())
        y0 = int(self.drawing_area.winfo_rooty())
        x1 = int(x0 + self.width)
        y1 = int(y0 + self.height)
        crop_region = (x0,y0,x1,y1)
        print(crop_region)
        im = ImageGrab.grab(backend='scrot', bbox=crop_region)
        #im.save("capture "+str(datetime.datetime.now())+".png")
        #im.save("capture.png")
        #im.show()
        im = im.resize((320,240), Image.ANTIALIAS)
        sstv = Robot36(im, 44100, 16)
        sstv.vox_enabled = True
        PyAudioSSTV(sstv).execute()

    def to_white(self, event=None):
        self.color = "white"

    def to_red(self, event=None):
        self.color = "red"

    def to_orange(self, event=None):
        self.color = "orange"
    
    def to_yellow(self, event=None):
        self.color = "yellow"

    def to_green(self, event=None):
        self.color = "green"

    def to_blue(self, event=None):
        self.color = "blue"

    def to_indigo(self, event=None):
        self.color = "indigo"

    def to_violet(self, event=None):
        self.color = "violet"

    def getColor(self, event=None):
        color = askcolor()
        self.color = color[-1]

    def to_small(self, event=None):
        self.size = 4

    def to_med(self, event=None):
        self.size = 8

    def to_big(self, event=None):
        self.size = 12

    def to_huge(self, event=None):
        self.size = 16

    def to_chonk(self, event=None):
        self.size = 20

    def to_heck(self, event=None):
        self.size = 30

    def to_bigchung(self, event=None):
        self.size = 40

    def to_ohlawd(self, event=None):
        self.size = 50

    def __init__(self, root):
        self.width = 1280
        self.height = 960
        self.drawing_area = Canvas(root, width=self.width, height=self.height, background='white')
        self.drawing_area.grid(row = 0, column = 0, rowspan=13)
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_but_down)
        self.drawing_area.bind("<ButtonRelease-1>", self.left_but_up)

root = Tk()

paint_app = PaintApp(root)

root.title("SSTV Paint")

#ttk.Button(root, text="hello").pack()

MyFont = font.Font(family="Helvetica", size=24)
smallFont = font.Font(family="Helvetica", size=14)

lineSmall = font.Font(family="Helvetica", size=10)
lineMed = font.Font(family="Helvetica", size=12)
lineBig = font.Font(family="Helvetica", size=14)
lineHuge = font.Font(family="Helvetica", size=16)
lineChonk = font.Font(family="Helvetica", size=18)
lineHeckinChonk = font.Font(family="Helvetica", size=20)
lineBigChungus = font.Font(family="Helvetica", size=22)
lineOHLAWDHECOMIN = font.Font(family="Helvetica", size=24)

wheel = PhotoImage(file="./img/colorwheel.png")

Button(root, text="Send", font=MyFont, width=6, height=2, command=paint_app.grab_n_send).grid(sticky = S)
Button(root, bg="white", width=6, height=3, command=paint_app.to_white).grid(row=0, column=1)
Button(root, bg="red", width=6, height=3, command=paint_app.to_red).grid(row=1, column=1)
Button(root, bg="orange", width=6, height=3, command=paint_app.to_orange).grid(row=2, column=1)
Button(root, bg="yellow", width=6, height=3, command=paint_app.to_yellow).grid(row=3, column=1)
Button(root, bg="green", width=6, height=3, command=paint_app.to_green).grid(row=0, column=2)
Button(root, bg="blue", width=6, height=3, command=paint_app.to_blue).grid(row=1, column=2)
Button(root, bg="indigo", width=6, height=3, command=paint_app.to_indigo).grid(row=2, column=2)
Button(root, bg="violet", width=6, height=3, command=paint_app.to_violet).grid(row=3, column=2)
Button(root, text="—", font=lineSmall, width=1, height=1, command=paint_app.to_small).grid(row=4, column=1)
Button(root, text="—", font=lineMed, width=1, height=1, command=paint_app.to_med).grid(row=5, column=1)
Button(root, text="—", font=lineBig, width=1, height=1, command=paint_app.to_big).grid(row=6, column=1)
Button(root, text="—", font=lineHuge, width=1, height=1, command=paint_app.to_huge).grid(row=7, column=1)
Button(root, text="—", font=lineChonk, width=1, height=1, command=paint_app.to_chonk).grid(row=4, column=2)
Button(root, text="—", font=lineHeckinChonk, width=1, height=1, command=paint_app.to_heck).grid(row=5, column=2)
Button(root, text="—", font=lineBigChungus, width=1, height=1, command=paint_app.to_bigchung).grid(row=6, column=2)
Button(root, text="—", font=lineOHLAWDHECOMIN, width=1, height=1, command=paint_app.to_ohlawd).grid(row=7, column=2)
Button(root, image=wheel, text='Custom\nColor', font=smallFont, command=paint_app.getColor).grid(row=8,column=1,columnspan=2)

root.mainloop()
