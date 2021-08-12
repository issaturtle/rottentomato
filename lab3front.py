"""
                                                                                      Hung Nguyen
Description: sets up a GUI for users to select which they want to see
"""

import tkinter as tk
import numpy as np
import sqlite3
import webbrowser
import tkinter.messagebox as tkmb
class mainWin(tk.Tk):
    #The main window for users to interact with
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('movies.db')
        self.cur = self.conn.cursor()
        
        self.protocol("WM_DELETE_WINDOW", self.closeGUI)

        self.title("Movies")
        self.frame1 = tk.Frame(self)
        self.frame2 = tk.Frame(self)
        self.frame3 = tk.Frame(self)
        
        tk.Label(self.frame1, text = "2021 Most Anticipated Movies", font = ("b")).pack(pady = (5,10))
        self.frame1.grid()

        tk.Label(self.frame3, text = "Search:").grid(row = 1, column = 0, sticky = 'w', padx = (10,20))
        self.frame2.grid()

        tk.Button(self.frame3, text = "Webpage", fg = "blue", command = self.web).grid(row = 1, column = 1, padx = (3,3) , pady = (10,10))
        tk.Button(self.frame3, text = "Main Actor", fg = "blue", command = self.mainAct).grid(row = 1, column = 2, padx = (3,3), pady = (10,10))
        tk.Button(self.frame3, text = "Month", fg = "blue", command = self.month).grid(row = 1, column= 3, padx = (3,10), pady = (10,10))
        self.frame3.grid()

    def closeGUI(self):
        if tkmb.askokcancel("Close", "Do you want to exit?"):
            self.destroy()
            self.quit()

    def web(self):
        #opens url website
        web = webp(self, "movie")
        self.wait_window(web)
        if web.getter() != 0:
            self.cur.execute("""SELECT url FROM MoviesDB WHERE title = ?""", (web.getter(),))
            url = self.cur.fetchone()[0]
            webbrowser.open(url)
        
    def mainAct(self):
        #allows user to click on main actors and display the movies 
        web = webp(self,"main actor")
        self.wait_window(web)
        result = ''.join(dict.fromkeys(web.getter()))
        if web.getter() != 0:
            self.cur.execute("""SELECT * FROM MoviesDB WHERE actors0 = ? """, (*result,))
            display = displayWin(self, self.cur.fetchall(),1)

    def month(self):
        #display all the movies on that month
        web = webp(self,"month")
        self.wait_window(web)
        if web.getter() != 0:
            self.cur.execute('''SELECT title FROM MoviesDB JOIN MonthDB 
                ON MoviesDB.monthKey = MonthDB.monthKey AND MonthDB.month = ? ''', (web.getter(),))
        
            display = displayWin(self, self.cur.fetchall(),2)

class webp(tk.Toplevel):
    def __init__(self, master, choice):
        #a Top level window to display user's choices
        super().__init__(master)
        self.protocol("WM_DELETE_WINDOW", self.closeGUI)

        self.conn = sqlite3.connect('movies.db')
        self.cur = self.conn.cursor()
        self.grab_set()     
        self.frame1 = tk.Frame(self)
        self.frame2= tk.Frame(self)
        self.title("Movie")
        
        self.i = 0
        self.getLb = 0
        tk.Label(self.frame1, text = f"Click on a {choice} to select ", bg = 'light grey').grid()

        S = tk.Scrollbar(self.frame2)
        self.LB = tk.Listbox(self.frame2, height = 12, width = 20, yscrollcommand=S.set)
        self.sqlData = self.setListBox(choice)
        for data in self.sqlData:
            self.LB.insert(tk.END,*data)

        self.LB.grid(row= 1, column = 0)
        S.config(command=self.LB.yview)
        S.grid(sticky = 'ns', row = 1, column = 1)
        
        self.frame1.grid()
        self.frame2.grid()
        
        self.LB.bind('<<ListboxSelect>>', self.closeWin)
    
    def setListBox(self, choice):
        #gets the sql data based on user choice
        if choice == "movie":
            i = [ movie for movie in self.cur.execute('''SELECT title FROM MoviesDB ORDER BY title ASC ''')]
            return i
        elif choice == "main actor":
            i = [actor for actor in self.cur.execute('''SELECT actors0 FROM MoviesDB ORDER BY actors0 ASC ''')]
            return i
        elif choice == "month":
            i = [month for month in self.cur.execute('''SELECT month FROM MonthDB''')]
            i.pop()
            return i
    def closeWin(self,value):
        self.i = self.LB.curselection() 
        self.getLb = str(self.LB.get(self.i))
        self.destroy()
    def getter(self):
        return self.getLb
    def closeGUI(self):
        self.getLb = 0
        self.destroy()

class displayWin(tk.Toplevel):
    def __init__(self, master, movieTup, types):
        #display one movie datas or print all the titles of one month
        super().__init__(master)
        self.title("Movies")
        self.geometry("300x300")
        self.protocol("WM_DELETE_WINDOW", self.closeGUI)

        frame1 = tk.Frame(self)
        S = tk.Scrollbar(frame1)
        self.LB = tk.Listbox(frame1, height = 30, width = 50, yscrollcommand=S.set)
        self.grab_set()
       
        if types == 1:
            for a in movieTup:
                for ind in range(len(a)):
                    
                    if ind == 0:
                    
                        self.LB.insert(tk.END, f"Movie: {a[ind]}")
                    elif ind == 3 or ind == 1:
                        pass
                    elif ind == 2:
                    
                        self.LB.insert(tk.END, f"Directors: {a[ind]}")
                    elif ind == 4: 
                        self.LB.insert(tk.END, "Starring:")
                        self.LB.insert(tk.END, a[ind])
                    else:
                        try:
                            self.LB.insert(tk.END, a[ind].strip())
                        except:
                            break
                self.LB.insert(tk.END, "\n")
        if types == 2:
            for data in movieTup:
                self.LB.insert(tk.END, *data)
                        
        self.LB.grid(row= 1, column = 0)
        S.config(command=self.LB.yview)
        S.grid(sticky = 'ns', row = 1, column = 1)
        frame1.grid()

    def closeGUI(self):
        self.destroy()
r = mainWin()
r.mainloop()
