import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
import math
from ctypes import *

if not os.path.exists('tmp'):
    os.makedirs('tmp')


def set_plot_title(title, fs=16):
    plt.title(title, fontsize=fs)


class NotchFilter:
    def __init__(self):
        pass

    def filter(self, fshift, points, d0, path):
        m = fshift.shape[0]
        n = fshift.shape[1]
        for u in range(m):
            for v in range(n):
                for d in range(len(points)):
                    u0 = points[d][0]
                    v0 = points[d][1]
                    u0, v0 = v0, u0
                    d1 = pow(pow(u - u0, 2) + pow(v - v0, 2), 0.5)
                    d2 = pow(pow(u + u0, 2) + pow(v + v0, 2), 0.5)
                    fshift[u][v] *= (1 - math.exp(-0.5 * (d1 * d2 / pow(d0, 2))))

        f_ishift = np.fft.ifftshift(fshift)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        matplotlib.image.imsave(path, img_back, cmap="gray")
        return


class Main:
    def __init__(self):
        windll.shcore.SetProcessDpiAwareness(1)
        self.root = tk.Tk()
        self.root.tk.call('tk', 'scaling', 1.5)
        self.root.resizable(0, 0)
        self.root.title("Notch")
        self.orig_frame = tk.LabelFrame(text="Оригинал")
        self.orig_frame.columnconfigure(0)
        self.orig_frame.columnconfigure(1)
        self.orig_frame.rowconfigure(0)
        self.orig_frame.rowconfigure(1)
        self.orig_frame.rowconfigure(2)
        self.orig_frame.rowconfigure(3)
        self.orig_frame.rowconfigure(4)
        self.orig_frame.rowconfigure(5)
        self.original_img = tk.Label(self.orig_frame, image="", padx=150,
                                     pady=150)
        self.btn_take_img = tk.Button(self.orig_frame, text="Выбрать изображение", bg="lightgray",
                                        command=self.take_img)
        self.btn_filter = tk.Button(self.orig_frame, text="Начать обработку", bg="lightgray",
                                    command=self.filter)
        self.select_filter_var = tk.StringVar(self.root)
        self.NumberOfPoints = tk.Entry(self.orig_frame)
        self.original_img.grid(row=0, column=0, columnspan=2)
        self.btn_take_img.grid(row=1, column=0, sticky='nsew')
        self.btn_filter.grid(row=1, column=1, sticky='nsew')
        tk.Label(self.orig_frame,  text="Кол-во точек: ").grid(row=3, column=0, sticky='nsew')
        self.NumberOfPoints.grid(row=3, column=1, sticky='nsew')
        self.NumberOfPoints.insert(tk.END, '4')
        self.orig_frame.pack(side="left", fill=tk.Y)
        self.right_frame = tk.LabelFrame(text="Результат")
        self.filter_img = tk.Label(self.right_frame, image="",
                                   padx=150, pady=150)
        self.filter_img.pack()
        self.right_frame.pack(side="right", fill=tk.Y)

    def take_img(self):
        file = filedialog.askopenfilename(title="Load Image", filetypes=[('Images', ['*jpeg', '*png', '*jpg'])])
        file = ImageOps.grayscale((Image.open(file)))
        file.save(pathlib.Path("tmp/original_img.png"))
        file = file.resize((800, 600))
        file = ImageTk.PhotoImage(file)
        self.original_img.configure(text="", image=file)
        self.original_img.text = ""
        self.original_img.image = file

    def GetFshiftDFT(self):
        img = Image.open(pathlib.Path("tmp/original_img.png"))
        img = np.asarray(img)
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        dft = 20 * np.log(np.abs(fshift))
        matplotlib.image.imsave(pathlib.Path("tmp/dft.png"), dft, cmap="gray")
        return fshift, dft

    def filter(self):
        fshift, dft = self.GetFshiftDFT()
        plt.clf()
        plt.imshow(Image.open(pathlib.Path("tmp/dft.png")), cmap="gray")
        set_plot_title("Поставьте точки")
        plt.waitforbuttonpress()
        points = np.asarray(plt.ginput(int(self.NumberOfPoints.get()), timeout=-1))
        plt.close()
        NotchFilter().filter(fshift, points, 120,
                                     pathlib.Path("tmp/FiltImg.png"))
        filter_img = ImageTk.PhotoImage(
            ImageOps.grayscale((Image.open(pathlib.Path("tmp/FiltImg.png")).resize((800, 600)))))
        self.filter_img.configure(image=filter_img)
        self.filter_img.image = filter_img

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Main().run()
