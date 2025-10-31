import tkinter as tk
from tkinter import ttk
import math
import re

# --- Safe eval helpers ---
# Restricting the functions available in 'eval' is a crucial security measure.
SAFE_FUNCTIONS = {
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'pi': math.pi,
    'e': math.e,
    'pow': pow,
    'abs': abs,
}

def safe_eval(expr: str):
    """
    Evaluate a math expression safely by limiting globals.
    Allows numbers, basic arithmetic operators, and functions from SAFE_FUNCTIONS.
    """
    # Simple check for allowed characters (slightly relaxed, relying heavily on restricted eval scope)
    allowed_chars = "0123456789+-*/(). %e"
    for ch in expr:
        if ch.isalpha() and ch not in 'sincotapewabsr': # Check against letters in allowed functions
            raise ValueError("Invalid character found in expression")
        if ch.isalpha() or ch.isspace():
            continue
        if ch not in allowed_chars:
            raise ValueError(f"Invalid character: {ch}")

    # Evaluate with SAFE_FUNCTIONS as allowed globals and an empty dictionary for locals
    return eval(expr, {**SAFE_FUNCTIONS}, {})

class ModernCalculator(tk.Tk):
    # Fix 1: Corrected constructor name from 'init' to '__init__'
    def __init__(self):
        super().__init__()
        self.title("Modern Python Calculator")
        self.geometry("360x540")
        self.resizable(False, False)
        self.configure(bg="#2b2b2b")

        # style
        style = ttk.Style(self)
        style.theme_use('clam')

        # fonts & colors
        self.bg = "#2b2b2b"
        self.panel_bg = "#1f1f1f"
        self.btn_bg = "#333333"
        self.btn_fg = "#ffffff"
        self.op_bg = "#ff9500" # Orange for primary operators
        self.accent = "#4cd964" # Green for '=' button
        self.disp_font = ("Segoe UI", 24)
        self.btn_font = ("Segoe UI", 14, "bold")

        # expression
        self.expression = ""
        self.create_ui()
        self.bind_keys()

    def create_ui(self):
        # top frame for display
        top = tk.Frame(self, bg=self.panel_bg, bd=0)
        # Using padx/y on place to create a slight margin effect
        top.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.26)

        # display (label for expression and result)
        self.expr_var = tk.StringVar()
        self.result_var = tk.StringVar()

        # Expression history label
        expr_label = tk.Label(top, textvariable=self.expr_var, anchor='e', bg=self.panel_bg,
                              fg='#bdbdbd', font=("Segoe UI", 12))
        expr_label.pack(fill='both', padx=12, pady=(12, 0))

        # Result label
        result_label = tk.Label(top, textvariable=self.result_var, anchor='e', bg=self.panel_bg,
                                fg=self.btn_fg, font=self.disp_font)
        result_label.pack(fill='both', padx=12, pady=(0, 12))

        # buttons frame
        btns = tk.Frame(self, bg=self.bg)
        btns.place(relx=0.05, rely=0.35, relwidth=0.9, relheight=0.6)

        # layout buttons in grid
        btn_layout = [
            ['AC', 'C', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['+/-', '0', '.', '=']
        ]

        for r, row in enumerate(btn_layout):
            for c, key in enumerate(row):
                is_op = key in ['/', '*', '-', '+', '=']
                # Determine background color
                if key == '=':
                    bg = self.accent
                elif key in ['AC', 'C', '+/-', '%']:
                    bg = '#555555' # Secondary function color
                elif is_op:
                    bg = self.op_bg
                else:
                    bg = self.btn_bg
                
                # Determine foreground color (all white/light grey for contrast)
                fg = self.btn_fg

                btn = tk.Label(btns, text=key, bg=bg, fg=fg, font=self.btn_font, bd=0,
                               relief='flat', cursor="hand2")
                btn.grid(row=r, column=c, sticky='nsew', padx=5, pady=5) # Reduced padding for compact look

                # make grid cells expand evenly
                btns.grid_rowconfigure(r, weight=1)
                btns.grid_columnconfigure(c, weight=1)

                # bindings
                btn.bind('<Button-1>', lambda e, k=key: self.on_button_click(k))
                btn.bind('<Enter>', lambda e, w=btn: w.configure(bg=self.hover_color(w)))
                btn.bind('<Leave>', lambda e, w=btn, key=key: w.configure(bg=self.reset_color(key)))

        # small footer
        footer = tk.Label(self, text='Designed by Gemini • Safe eval for basic math',
                          bg=self.bg, fg='#888', font=("Segoe UI", 8))
        footer.place(relx=0.05, rely=0.94, relwidth=0.9)

    def hover_color(self, widget):
        cur = widget.cget('text')
        if cur == '=':
            return '#2e7d32' # darker green
        if cur in ['/', '*', '-', '+']:
            return '#e67e22' # darker orange
        if cur in ['AC', 'C', '+/-', '%']:
            return '#666666'
        return '#444444' # darker number color

    def reset_color(self, key):
        if key == '=':
            return self.accent
        if key in ['/', '*', '-', '+']:
            return self.op_bg
        if key in ['AC', 'C', '+/-', '%']:
            return '#555555'
        return self.btn_bg

    def bind_keys(self):
        # Bind number and operator keys
        for char in '0123456789.+-*/()%':
            self.bind(char, self.on_key)
        # Bind commands
        self.bind('<Return>', lambda e: self.on_button_click('='))
        self.bind('<BackSpace>', lambda e: self.on_button_click('C'))
        self.bind('<Escape>', lambda e: self.on_button_click('AC'))

    def on_key(self, event):
        self.on_button_click(event.char)

    def on_button_click(self, key):
        try:
            if key == 'AC':
                self.expression = ''
                self.result_var.set('')
                self.expr_var.set('')
                return

            if key == 'C':
                # backspace
                self.expression = self.expression[:-1]
                self.expr_var.set(self.expression)
                return

            if key == '+/-':
                # toggle sign of the last number
                self.toggle_sign()
                return

            if key == '%':
                # percent: divide current number by 100 (attempts to evaluate current expression)
                if not self.expression.strip():
                    return
                try:
                    val = safe_eval(self.expression)
                    val = val / 100
                    # For simplicity, we restart the expression with the calculated percentage value
                    self.expression = str(val)
                    self.expr_var.set(self.expression)
                    self.result_var.set(self.expression)
                except Exception:
                    self.result_var.set('Error')
                return

            if key == '=':
                # evaluate
                # Fix 2: Added space after 'not'
                if not self.expression.strip():
                    return
                try:
                    result = safe_eval(self.expression)
                    
                    # format: drop .0 for integers
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    
                    self.result_var.set(str(result))
                    self.expr_var.set(self.expression + ' =')
                    self.expression = str(result) # Start new calculations from the result
                except Exception as e:
                    print(f"Evaluation error: {e}")
                    self.result_var.set('Error')
                    self.expression = '' # Reset expression on error
                return

            # otherwise append key
            self.expression += str(key)
            self.expr_var.set(self.expression)
            
        except Exception as e:
            # Catch errors in the button click logic itself (not evaluation)
            print(f"UI Error: {e}")
            self.result_var.set('Error')
            self.expression = ''

    def toggle_sign(self):
        # find last number in the expression and toggle its sign
        # Looks for any floating point or integer number at the end, optionally preceded by a minus sign
        m = re.search(r'(-?\d*\.?\d+)$', self.expression)
        if not m:
            return
        
        num = m.group(1)
        start = m.start(1)

        if num.startswith('-'):
            new = num[1:]
        else:
            new = '-' + num
            
        self.expression = self.expression[:start] + new
        self.expr_var.set(self.expression)

# Fix 3: Corrected main execution block name from 'name == ' main '' to '__name__ == '__main__''
if __name__ == '__main__':
    app = ModernCalculator()
    app.mainloop()
