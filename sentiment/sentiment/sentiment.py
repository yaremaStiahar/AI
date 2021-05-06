from textblob import TextBlob
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import tkinter as tk
from PIL import ImageTk, Image
from os import system


class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self, master=master, **kw)
        self.default_background = self["background"]
        self.default_foreground = self["foreground"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self["background"] = self["activebackground"]
        self["foreground"] = self["activeforeground"]

    def on_leave(self, e):
        self["background"] = self.default_background
        self["foreground"] = self.default_foreground


def find_text(page_html):
    text = ""
    soup = BeautifulSoup(page_html, 'html.parser')
    for i in range(1, 7):
        tags = soup.find_all(f"h{i}")
        for tag in tags:
            text += " " + tag.getText()
    tags = soup.find_all('p')
    for tag in tags:
        text += " " + tag.getText()
    return text


def search(data):
    webdriver_path = "chromedriver.exe"
    driver = webdriver.Chrome(webdriver_path)

    try:
        driver.get("https://www.google.co.uk")
        search_field = driver.find_element_by_xpath("/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input")
        search_field.send_keys(data)
        search_field.send_keys(Keys.RETURN)
    except:
        print("No internet connection")
        exit()

    s = []

    for j in range(1, 10):
        for i in range(1, 2):
            try:
                driver.get("https://www.google.co.uk")
                search_field = driver.find_element_by_xpath("/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input")
                search_field.send_keys(data)
                search_field.send_keys(Keys.RETURN)
                s1 = driver.find_element_by_xpath(f"//*[@id=\"rso\"]/div[{j}]/div/div/div[1]/a/h3")
                #//*[@id="rso"]/div[1]/div/div/div/div[1]/a/h3
                #//*[@id="rso"]/div[3]/div/div/div[1]/a/h3
                #//*[@id=\"rso\"]/div[{j}]/div/div[{i}]/div/div/div[1]/a[1]/h3
                #s1 = driver.find_element_by_xpath(f"//*[@id=\"rso\"]/div[{j}]/div/div[{i}]/div/div/div[1]/a[1]/h3")
                s1.click()
                page_html = driver.page_source
                s.append(find_text(page_html))
                if len(s) == 100:
                    break
            except:
                continue

    file = open("analysed_text.txt", "w+", encoding="utf-8")
    file.write(str(0))
    file.write(s[0])
    file.close()
    file = open("analysed_text.txt", "a+", encoding="utf-8")
    for i in range(1, len(s)):
        file.write(str(i))
        file.write(s[i])
    file.close()

    return [[TextBlob(s[i]).sentiment for i in range(len(s))], s]


def start_search():
    global result
    global data_str
    data_str = data.get()
    result = search(data.get())
    root.destroy()


def configure():
    configure_root = tk.Toplevel(root)
    tk.Label(configure_root, text="Enter attempts number", font=("Cambria", 14)).pack()
    url_count_entry = tk.Entry(configure_root, font=("Cambria", 12))
    url_count_entry.pack()

    def edit_url_count():
        global url_count
        url_count = int(url_count_entry.get()) - 1
        configure_root.destroy()

    HoverButton(configure_root, text="Apply", command=edit_url_count, activebackground="grey",
                bg="#D3D3D3", fg="black", activeforeground="white").pack()


def openfile():
    system('notepad analysed_text.txt')


smiles = {
    1: "very_sad.png",
    2: "sad.png",
    3: "neutral.png",
    4: "happy.png",
    5: "very_happy.png",
}

url_count = 5
data_str = ""
result = [[(0, 0)] * url_count, 0]

while True:

    root = tk.Tk()
    root.title("Advanced search")
    root.protocol("WM_DELETE_WINDOW", exit)
    data = tk.StringVar()
    data.set(data_str)
    menu = tk.Menu(root)
    menu.add_command(label="Exit", command=exit)
    menu.add_command(label="Config", command=configure)
    root.config(menu=menu)

    show_text_button_frame = tk.Frame(root)
    HoverButton(show_text_button_frame, text="Show text", activebackground="grey",
                bg="#D3D3D3", fg="black", activeforeground="white", command=openfile, width=15).pack()
    show_text_button_frame.pack(side=tk.BOTTOM)
    result_frame = [None] * len(result[0])
    polarity_canvas = [None] * len(result[0])
    polarity_label = [None] * len(result[0])
    smile = [None] * len(result[0])
    for i in range(len(result[0])):
        result_frame[i] = tk.Frame(root)
        polarity_canvas[i] = tk.Canvas(result_frame[i], width=30, height=30)
        polarity_label[i] = tk.Label(result_frame[i], text="Result #" + str(i + 1) + " ", font=("Cambria", 12))
        if result[0][i][0] < -0.5:
            smile[i] = ImageTk.PhotoImage(Image.open(smiles[1]))
        elif result[0][i][0] < 0:
            smile[i] = ImageTk.PhotoImage(Image.open(smiles[2]))
        elif result[0][i][0] == 0:
            smile[i] = ImageTk.PhotoImage(Image.open(smiles[3]))
        elif result[0][i][0] < 0.5:
            smile[i] = ImageTk.PhotoImage(Image.open(smiles[4]))
        elif result[0][i][0] <= 1:
            smile[i] = ImageTk.PhotoImage(Image.open(smiles[5]))
        polarity_canvas[i].create_image(17, 17, image=smile[i])

    for i in reversed(range(len(result[0]))):
        result_frame[i].pack(side=tk.BOTTOM)
        polarity_canvas[i].pack(side=tk.RIGHT)
        polarity_label[i].pack(side=tk.RIGHT)

    data_frame = tk.Frame(root)
    data_label = tk.Label(data_frame, text="Insert keywords", font=("Cambria", 14))
    data_entry = tk.Entry(data_frame, font=("Cambria", 12), textvariable=data)
    data_frame.pack(side=tk.LEFT, expand=1, fill=tk.X)
    data_label.pack()
    data_entry.pack(fill=tk.X)

    actions_frame = tk.Frame(root)
    start_button = HoverButton(actions_frame, text="Search", width=15, activebackground="grey",
                               bg="#D3D3D3", fg="black", activeforeground="white", command=start_search)
    actions_frame.pack(side=tk.RIGHT, fill=tk.Y)
    start_button.pack(side=tk.RIGHT, fill=tk.Y)

    root.mainloop()
