#!/usr/bin/env python3

import os
import sys

try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, filedialog
except ImportError:
    print("Missing tkinter. To install, run: sudo apt install python3-tk")
    sys.exit(1)

APP_NAME = "NeoLT"
NEOLT_DIR = os.path.expanduser("~/.neolt_gui")
USERS_FILE = os.path.join(NEOLT_DIR, "users.txt")
SETTINGS_FILE = os.path.join(NEOLT_DIR, "settings.txt")

current_user = None
dark_mode = False
bg_color = "#f0f0f0"
fg_color = "#000000"

# === Theme handling ===
def load_settings():
    global dark_mode
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            for line in f:
                if line.strip() == "dark=true":
                    dark_mode = True
    update_theme()

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        f.write("dark=true\n" if dark_mode else "dark=false\n")

def update_theme():
    global bg_color, fg_color
    bg_color = "#202124" if dark_mode else "#f0f0f0"
    fg_color = "#ffffff" if dark_mode else "#000000"

# === First time setup ===
def first_time_setup():
    os.makedirs(NEOLT_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write("admin:admin\n")

def user_exists(username, password):
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return any(line.strip() == f"{username}:{password}" for line in f)
    return False

def add_user(username, password):
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}:{password}\n")

def powerwash():
    import shutil
    if messagebox.askyesno("Powerwash", "Reset NeoLT? All users and settings will be lost."):
        shutil.rmtree(NEOLT_DIR, ignore_errors=True)
        messagebox.showinfo("Reset", "NeoLT has been reset.")
        sys.exit(0)

# === Apps ===
def neonote():
    win = tk.Toplevel()
    win.title("NeoNote")
    text = tk.Text(win, bg=bg_color, fg=fg_color)
    text.pack(expand=True, fill="both")
    def save():
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w") as f:
                f.write(text.get("1.0", "end-1c"))
    tk.Button(win, text="Save", command=save).pack()

def neocalc():
    win = tk.Toplevel()
    win.title("NeoCalc")
    expr = tk.Entry(win)
    result = tk.StringVar()
    def calc():
        try:
            result.set(str(eval(expr.get())))
        except:
            result.set("Error")
    expr.pack()
    tk.Button(win, text="Calculate", command=calc).pack()
    tk.Label(win, textvariable=result).pack()

def neoterminal():
    win = tk.Toplevel()
    win.title("NeoTerminal")
    out = tk.Text(win, bg="black", fg="lime")
    cmd = tk.Entry(win)
    out.pack(expand=True, fill="both")
    cmd.pack(fill="x")
    def run_cmd(event=None):
        c = cmd.get()
        out.insert("end", f"> {c}\n")
        try:
            r = os.popen(c).read()
            out.insert("end", r + "\n")
        except:
            out.insert("end", "Error running command\n")
        cmd.delete(0, "end")
    cmd.bind("<Return>", run_cmd)

def neosys():
    win = tk.Toplevel()
    win.title("NeoSys")
    uname = os.popen("uname -a").read()
    uptime = os.popen("uptime").read()
    tk.Label(win, text=f"User: {current_user}").pack()
    tk.Label(win, text=f"System: {uname}").pack()
    tk.Label(win, text=f"Uptime: {uptime}").pack()

def settings_menu():
    global dark_mode
    choice = messagebox.askyesno("Dark Mode", "Enable Dark Mode?")
    dark_mode = choice
    save_settings()
    update_theme()
    messagebox.showinfo("Saved", "Restart NeoLT to apply the theme.")

# === Start Menu ===
def show_start_menu(parent):
    start_win = tk.Toplevel(parent)
    start_win.title("Start Menu")
    start_win.geometry("400x300")
    start_win.configure(bg=bg_color)
    start_win.transient(parent)
    start_win.grab_set()

    tk.Label(start_win, text="Apps", font=("Arial", 14), bg=bg_color, fg=fg_color).pack(pady=10)

    app_frame = tk.Frame(start_win, bg=bg_color)
    app_frame.pack()

    def app_button(name, command):
        tk.Button(app_frame, text=name, command=command, width=15).pack(pady=2)

    app_button("NeoNote", neonote)
    app_button("NeoCalc", neocalc)
    app_button("NeoTerminal", neoterminal)
    app_button("NeoSys", neosys)
    app_button("Settings", settings_menu)

# === Main Menu ===
def main_menu():
    app = tk.Tk()
    app.title(f"NeoLT - {current_user}")
    app.attributes("-fullscreen", True)
    app.configure(bg=bg_color)

    desktop = tk.Frame(app, bg=bg_color)
    desktop.pack(expand=True, fill="both")

    # Bottom "taskbar" frame
    taskbar = tk.Frame(app, bg="#333333", height=40)
    taskbar.pack(fill="x", side="bottom")

    start_button = tk.Button(taskbar, text="⦿ Start", command=lambda: show_start_menu(app), bg="#555555", fg="white")
    start_button.pack(side="left", padx=10, pady=5)

    tk.Button(taskbar, text="Logout", command=lambda: [app.destroy(), login_screen()], bg="#555555", fg="white").pack(side="right", padx=10)
    tk.Button(taskbar, text="Powerwash", command=powerwash, bg="#aa0000", fg="white").pack(side="right")

    app.mainloop()

# === Login screen ===
def login_screen():
    root = tk.Tk()
    root.title("NeoLT Login")
    root.geometry("300x220")
    root.configure(bg=bg_color)

    tk.Label(root, text="Username:", bg=bg_color, fg=fg_color).pack()
    user_entry = tk.Entry(root)
    user_entry.pack()

    tk.Label(root, text="Password:", bg=bg_color, fg=fg_color).pack()
    pass_entry = tk.Entry(root, show="*")
    pass_entry.pack()

    def login():
        u = user_entry.get()
        p = pass_entry.get()
        if user_exists(u, p):
            global current_user
            current_user = u
            root.destroy()
            main_menu()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

    tk.Button(root, text="Login", command=login).pack(pady=8)
    tk.Button(root, text="Powerwash", command=powerwash).pack()

    # Default user hint
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            if f.read().strip() == "admin:admin":
                tk.Label(root, text="Default login: admin / admin", bg=bg_color, fg="gray").pack(pady=5)

    root.mainloop()

# === Start ===
if __name__ == "__main__":
    if not os.path.exists(NEOLT_DIR):
        first_time_setup()
    load_settings()
    login_screen()
