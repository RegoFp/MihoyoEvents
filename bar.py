import tkinter as tk
import pystray
from pystray import MenuItem as Item
from PIL import Image

from ctypes import windll


def get_pos(event):  # this is executed when the title bar is clicked to move the window
    if window.maximized == False:
        xwin = window.winfo_x()
        ywin = window.winfo_y()
        startx = event.x_root
        starty = event.y_root

        ywin = ywin - starty
        xwin = xwin - startx

        def move_window(event):  # runs when window is dragged
            window.geometry(f'+{event.x_root + xwin}+{event.y_root + ywin}')

        def release_window(event):  # runs when window is released
            window.config(cursor="arrow")

        topbar.bind('<B1-Motion>', move_window)
        topbar.bind('<ButtonRelease-1>', release_window)

        topbarTitle.bind('<B1-Motion>', move_window)
        topbarTitle.bind('<ButtonRelease-1>', release_window)


# Shows the app on the windows bar
def set_appwindow():  # to display the window icon on the taskbar,
    # even when using root.overrideredirect(True
    # Some WindowsOS styles, required for task bar integration
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    # Magic
    hwnd = windll.user32.GetParent(window.winfo_id())
    stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    stylew = stylew & ~WS_EX_TOOLWINDOW
    stylew = stylew | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)

    window.wm_withdraw()
    window.after(10, lambda: window.wm_deiconify())


# Change x button color on hover
def changex_on_hovering(event):
    close_button['bg'] = 'red'


def returnx_to_normalstate(event):
    close_button['bg'] = RGRAY


def changer_on_hovering(event):
    config_button['bg'] = '#3e4344'


def returnr_to_normalstate(event):
    config_button['bg'] = RGRAY


# Windows tray stuff
def hide_window():
    window.withdraw()
    print("yyp")
    image = Image.open(r"img\icon.ico")
    menu = (Item('Show', show_window, default=True),
            Item('Quit', quit_window))  # ,item('Timeline', show_timeline),item("Primo tracker", show_tracker))
    icon = pystray.Icon("name", image, "Proto calculator", menu)
    icon.run()


def show_window(icon):
    icon.stop()
    window.after(0, window.deiconify)


def quit_window(icon):
    icon.stop()
    window.destroy()


def get_returnButton():
    return config_button


def stop():
    window.grab_release()
    window.destroy()


# The bar widget
class Bar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        global window
        global RGRAY

        window = parent

        parent.minimized = False  # only to know if root is minimized
        parent.maximized = False  # only to know if root is maximized

        LGRAY = '#3e4042'  # button color effects in the title bar (Hex color)
        DGRAY = '#25292e'  # window background color               (Hex color)
        RGRAY = '#1d1f21'  # title bar color                       (Hex color)

        self.config(bg=RGRAY)
        self.config(relief='raised', bd=0, highlightthickness=0)

        global close_button

        global topbar
        global topbarTitle

        global config_button

        topbar = self

        close_button = tk.Button(self, text='  ×  ', command=hide_window, bg=RGRAY, padx=2, pady=2,
                                 font=("calibri", 13), bd=0, fg='white', highlightthickness=0)
        topbarTitle = tk.Label(self, text="Genshin companion", bg=RGRAY, bd=0, fg='white', font=("helvetica", 10),
                               highlightthickness=0)
        config_button = tk.Button(self, text="↻", bg=RGRAY, bd=0, fg='white', font=("Cambria", 13),
                                  highlightthickness=0, padx=2, pady=2, width=5)

        close_button.pack(side="right", ipadx=7, ipady=1)
        config_button.pack(side="right", fill='y')
        topbarTitle.pack(side="left", padx=10)

        # button effects in the title bar when hovering over buttons
        close_button.bind('<Enter>', changex_on_hovering)
        close_button.bind('<Leave>', returnx_to_normalstate)

        config_button.bind('<Enter>', changer_on_hovering)
        config_button.bind('<Leave>', returnr_to_normalstate)

        # Shows the app on the windows bar
        parent.after(10, lambda: set_appwindow())

        self.bind('<Button-1>', get_pos)  # so you can drag the window from the title bar
        topbarTitle.bind('<Button-1>', get_pos)


class ProtoBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        global window
        global RGRAY

        window = parent

        parent.minimized = False  # only to know if root is minimized
        parent.maximized = False  # only to know if root is maximized

        LGRAY = '#3e4042'  # button color effects in the title bar (Hex color)
        DGRAY = '#25292e'  # window background color               (Hex color)
        RGRAY = '#1d1f21'  # title bar color                       (Hex color)

        self.config(bg=RGRAY)
        self.config(relief='raised', bd=0, highlightthickness=0)

        global close_button

        global topbar
        global topbarTitle

        global config_button

        topbar = self

        close_button = tk.Button(self, text='  ×  ', command=stop, bg=RGRAY, padx=2, pady=2, font=("calibri", 13), bd=0,
                                 fg='white', highlightthickness=0)
        topbarTitle = tk.Label(self, text="Genshin companion", bg=RGRAY, bd=0, fg='white', font=("helvetica", 10),
                               highlightthickness=0)

        close_button.pack(side="right", ipadx=7, ipady=1)
        topbarTitle.pack(side="left", padx=10)

        # button effects in the title bar when hovering over buttons
        close_button.bind('<Enter>', changex_on_hovering)
        close_button.bind('<Leave>', returnx_to_normalstate)

        self.bind('<Button-1>', get_pos)  # so you can drag the window from the title bar
        topbarTitle.bind('<Button-1>', get_pos)


####Only for testing --------------------------
class MyApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Hello Tkinter")
        self.geometry("800x600")
        self.resizable(width=False, height=False)
        self.overrideredirect(True)

        Bar(self).pack(fill='x')


if __name__ == '__main__':
    app = MyApplication()
    app.mainloop()
