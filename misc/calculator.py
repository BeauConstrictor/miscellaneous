from __future__ import annotations
import tkinter as tk

FONT = ("Arial", 20)

class Keypad(tk.Frame):
    def __init__(self, root: App):
        super().__init__()

        self.buttons = []

        self.root = root

        for row in range(4):
            for column in range(3):
                if row == 3 and column != 1: continue
                label = "0" if row == 3 else str((row+1) * (column+1))
                button = tk.Button(self, text=label, command=lambda l=label: self.root.enter_key(l), font=FONT)
                self.buttons.append(button)
                button.grid(row=row, column=column)

        for i in range(3):
            tk.Label(self, text="        ").grid(row=0, column=4)

        self.operation_buttons = [
            [ "+", "-", "×" ],
            [ "÷", "C", "=" ],
            [ ".", "(", ")" ],
        ]
        for y, lbls in enumerate(self.operation_buttons):
            for x, lbl in enumerate(lbls):
                btn = tk.Button(self, text=lbl, command=lambda l=lbl: self.root.enter_key(l), font=FONT)
                btn.grid(row=y, column=5+x)

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Calculator")
        self.resizable(False, False)

        self.expression = ""

        self.display = tk.Label(font=FONT)
        self.display.pack()

        self.keypad = Keypad(self)
        self.keypad.pack()

    def enter_key(self, key: str) -> None:
        if key == "=":
            if self.expression == "": return
            try:
                self.expression = self.expression.replace("÷", "/").replace("×", "*")
                self.expression = str(eval(self.expression))
            except Exception as e:
                self.expression = type(e).__name__
        elif key == "C":
            self.expression = ""
        else:
            self.expression += key
       
        self.display.config(text=self.expression)

if __name__ == "__main__":
    app = App()
    app.mainloop()

