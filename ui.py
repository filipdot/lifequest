import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data import PATHS, save_data

def create_menu(self):
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Quit", command=self.root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_command(label="Guides", command=show_guides)
    view_menu.add_command(label="Tech Tree", command=show_tech_tree)
    view_menu.add_command(label="Debug Mode", command=show_debug)
    view_menu.add_command(label="Customize Dashboard", command=customize_dashboard)
    menubar.add_cascade(label="View", menu=view_menu)
    tasks_menu = tk.Menu(menubar, tearoff=0)
    tasks_menu.add_command(label="Add Task", command=add_task_window)
    menubar.add_cascade(label="Tasks", menu=tasks_menu)

def build_intro_dashboard(self):
    tk.Label(self.root, text="Witaj w LifeQuest! To aplikacja do grywalizacji życia.\n"
                             "Śledź rozwój w ścieżkach: Fizyczna, Społeczna, Zawodowa.\n"
                             "Naciśnij przycisk, by ustalić startowy poziom.", padx=10, pady=10).pack()
    tk.Button(self.root, text="Ustal swój obecny poziom", command=run_questionnaire).pack(pady=10)

def run_questionnaire(self):
    self.data["responses"] = {}
    self.data["question_version"] = PATHS["question_version"]
    for widget in self.root.winfo_children():
        widget.destroy()
    create_menu(self)
    for path in ["Fizyczna", "Społeczna", "Zawodowa"]:
        total = 0
        responses = []
        info = PATHS[path]
        for i, (q, min_val, max_val) in enumerate(info["questions"]):
            response = simpledialog.askinteger(path, q, minvalue=min_val, maxvalue=max_val)
            if response is not None:
                total += response
                responses.append(response)
            if path == "Zawodowa" and i == 0:  # Backlog
                backlog_resp = response
                if backlog_resp is not None:
                    if backlog_resp == 1:
                        tasks_q = "Ile zadań kończysz dziennie? (0-10)"
                        tasks_min, tasks_max = 0, 10
                    else:
                        tasks_q = "Ile zadań pamiętasz, że masz do zrobienia? (0-20)"
                        tasks_min, tasks_max = 0, 20
                    tasks_resp = simpledialog.askinteger(path, tasks_q, minvalue=tasks_min, maxvalue=tasks_max)
                    if tasks_resp is not None:
                        total += tasks_resp
                        responses.append(tasks_resp)
            if '0 jeśli nie wiesz' in q and response == 0:
                est_q = "Estymacja: Jak czujesz się po 30 min spaceru? (1=zmęczony, 5=pełen energii)"
                est_response = simpledialog.askinteger(path, est_q, minvalue=1, maxvalue=5)
                if est_response:
                    total += est_response * 5
                    responses.append(est_response)
        level = max(lv for lv, pts in sorted(info["levels"].items()) if total >= pts)
        self.data["levels"][path] = level
        self.data["exp"][path] = total
        self.data["responses"][path] = responses
    save_data(self.data)
    messagebox.showinfo("Start Level", "Twój startowy build gotowy!")
    build_dashboard(self)

def build_dashboard(self):
    for widget in self.root.winfo_children():
        widget.destroy()
    create_menu(self)
    canvas = tk.Canvas(self.root)
    scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Dynamic grid
    scrollable_frame.grid_rowconfigure(0, weight=1)
    scrollable_frame.grid_columnconfigure(0, weight=1)
    scrollable_frame.grid_columnconfigure(1, weight=1)

    left_frame = tk.Frame(scrollable_frame)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    right_frame = tk.Frame(scrollable_frame)
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    if self.data["question_version"] != PATHS["question_version"]:
        tk.Label(left_frame, text="Warning: Dane pytań niekompatybilne. Rerun kwestionariusz?", fg="red").pack(pady=5)

    tk.Button(left_frame, text="Sprawdź kompatybilność pytań", command=check_compatibility).pack(pady=5)
    tk.Button(left_frame, text="Rerun Pytania Startowe", command=run_questionnaire).pack(pady=5)

    if self.data["dashboard_config"]["show_levels"]:
        tk.Label(left_frame, text="Dashboard Postaci").pack(pady=5)
        fig, ax = plt.subplots(figsize=(5, 3))
        paths = [p for p in PATHS if p != "question_version"]
        levels = [self.data["levels"].get(p, 1) for p in paths]
        ax.bar(paths, levels)
        ax.set_ylim(0, 10)
        ax.set_title("Poziomy Ścieżek")
        canvas_fig = FigureCanvasTkAgg(fig, master=left_frame)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack(fill="both", expand=True)

    if self.data["dashboard_config"]["show_ach"]:
        tk.Label(left_frame, text="Achievements:").pack()
        self.ach_list = tk.Listbox(left_frame, height=5, width=40)
        for ach in self.data["achievements"]:
            self.ach_list.insert(tk.END, ach)
        self.ach_list.pack(fill="x")

    if self.data["dashboard_config"]["show_tasks"]:
        tk.Label(right_frame, text="Lista Zadań:").pack()
        self.task_text = scrolledtext.ScrolledText(right_frame, width=50, height=10, wrap=tk.WORD)
        self.task_text.pack(fill="both", expand=True)
        update_task_list(self)

def update_task_list(self):
    self.task_text.delete(1.0, tk.END)
    for i, task in enumerate(self.data["tasks"]):
        color = "green" if task["completed"] else "black"
        self.task_text.insert(tk.END, f"{task['text']} (Exp: {task['exp']}, Condition: {task['condition']}, Completed: {task['completed']})\n", color)
        self.task_text.tag_config(color, foreground=color)
    self.task_text.config(state=tk.DISABLED)

def add_task_window(self):
    add_window = tk.Toplevel(self.root)
    add_window.title("Dodaj Zadanie")
    tk.Label(add_window, text="Treść:").pack()
    text_entry = tk.Entry(add_window, width=40)
    text_entry.pack()
    tk.Label(add_window, text="Exp (1-10):").pack()
    exp_entry = tk.Entry(add_window, width=40)
    exp_entry.pack()
    tk.Label(add_window, text="Warunek wykonania:").pack()
    cond_entry = tk.Entry(add_window, width=40)
    cond_entry.pack()
    tk.Label(add_window, text="Ścieżka:").pack()
    path_combo = ttk.Combobox(add_window, values=list([p for p in PATHS if p != "question_version"]), state="readonly")
    path_combo.pack()
    tk.Button(add_window, text="Dodaj", command=lambda: add_task(self, text_entry.get(), exp_entry.get(), cond_entry.get(), path_combo.get(), add_window)).pack(pady=10)

def add_task(self, text, exp_str, condition, path, window=None):
    try:
        exp = int(exp_str)
        if 1 <= exp <= 10 and text and condition and path in PATHS:
            self.data["tasks"].append({"text": text, "path": path, "exp": exp, "condition": condition, "completed": False})
            save_data(self.data)
            update_task_list(self)
            if window:
                window.destroy()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowe dane (exp 1-10, pola wymagane).")
    except ValueError:
        messagebox.showerror("Błąd", "Exp musi być liczbą.")

def complete_task(self, idx):
    task = self.data["tasks"][idx]
    if not task["completed"]:
        task["completed"] = True
        path = task["path"]
        if path in PATHS:
            self.data["exp"][path] = self.data["exp"].get(path, 0) + task["exp"]
            info = PATHS[path]
            new_level = max(lv for lv, pts in sorted(info["levels"].items()) if self.data["exp"][path] >= pts)
            if new_level > self.data["levels"][path]:
                self.data["levels"][path] = new_level
                ach = f"Level Up w {path} do {new_level}!"
                self.data["achievements"].append(ach)
                messagebox.showinfo("Achievement", ach)
        else:
            messagebox.showwarning("Warning", "Nieznana ścieżka - skip lvl up")
        save_data(self.data)
        update_task_list(self)

def edit_task(self, idx):
    task = self.data["tasks"][idx]
    edit_window = tk.Toplevel(self.root)
    edit_window.title("Edytuj Zadanie")
    tk.Label(edit_window, text="Treść:").pack()
    text_entry = tk.Entry(edit_window, width=40)
    text_entry.insert(0, task["text"])
    text_entry.pack()
    tk.Label(edit_window, text="Exp (1-10):").pack()
    exp_entry = tk.Entry(edit_window, width=40)
    exp_entry.insert(0, str(task["exp"]))
    exp_entry.pack()
    tk.Label(edit_window, text="Warunek wykonania:").pack()
    cond_entry = tk.Entry(edit_window, width=40)
    cond_entry.insert(0, task["condition"])
    cond_entry.pack()
    tk.Button(edit_window, text="Zapisz", command=lambda: save_edited_task(self, idx, text_entry.get(), exp_entry.get(), cond_entry.get(), edit_window)).pack(pady=10)

def save_edited_task(self, idx, text, exp_str, condition, window):
    try:
        exp = int(exp_str)
        if 1 <= exp <= 10 and text and condition:
            self.data["tasks"][idx]["text"] = text
            self.data["tasks"][idx]["exp"] = exp
            self.data["tasks"][idx]["condition"] = condition
            save_data(self.data)
            update_task_list(self)
            window.destroy()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowe dane.")
    except ValueError:
        messagebox.showerror("Błąd", "Exp musi być liczbą.")

def show_guides(self):
    guide_window = tk.Toplevel(self.root)
    guide_window.title("Guides")
    for path in [p for p in PATHS if p != "question_version"]:
        level = self.data["levels"].get(path, 1)
        tk.Label(guide_window, text=f"{path} Lv{level}: {PATHS[path]['guides'].get(level, 'Brak guide')}").pack(padx=10)
        tk.Button(guide_window, text="Dodaj do zadań", command=lambda p=path, g=PATHS[path]['guides'][level]: add_guide_task(self, p, g)).pack()
        next_level = level + 1 if level < 10 else 10
        next_exp = PATHS[path]["levels"].get(next_level, 'Max')
        tk.Label(guide_window, text=f"Next: {PATHS[path]['guides'].get(next_level, 'Max level')} (Wymagane exp: {next_exp})").pack(padx=10)

def add_guide_task(self, path, guide):
    self.data["tasks"].append({"text": guide, "path": path, "exp": 5, "condition": "Wykonaj guide", "completed": False})
    save_data(self.data)
    update_task_list(self)

def show_tech_tree(self):
    path = simpledialog.askstring("Tech Tree", "Wybierz ścieżkę: Fizyczna, Społeczna, Zawodowa")
    if path in PATHS:
        tree_window = tk.Toplevel(self.root)
        tree_window.title(f"Tech Tree: {path}")
        for lv, exp_req in sorted(PATHS[path]["levels"].items()):
            guide = PATHS[path]["guides"].get(lv, "Brak guide")
            tk.Label(tree_window, text=f"Lv{lv} (Exp: {exp_req}): {guide}").pack(padx=10, pady=5)

def show_debug(self):
    debug_window = tk.Toplevel(self.root)
    debug_window.title("Debug Mode")
    text = scrolledtext.ScrolledText(debug_window, width=60, height=20)
    text.pack()
    for path in [p for p in PATHS if p != "question_version"]:
        text.insert(tk.END, f"Ścieżka: {path}\n")
        responses = self.data["responses"].get(path, [])
        for i, (q, _, _) in enumerate(PATHS[path]["questions"]):
            resp = responses[i] if i < len(responses) else "Brak"
            text.insert(tk.END, f"Pytanie: {q} | Odpowiedź: {resp}\n")
        text.insert(tk.END, "\n")
    text.config(state=tk.DISABLED)

def customize_dashboard(self):
    cust_window = tk.Toplevel(self.root)
    cust_window.title("Customize Dashboard")
    tk.Label(cust_window, text="Pokaż sekcje:").pack()
    show_levels = tk.BooleanVar(value=self.data["dashboard_config"]["show_levels"])
    tk.Checkbutton(cust_window, text="Poziomy", variable=show_levels).pack(anchor="w")
    show_ach = tk.BooleanVar(value=self.data["dashboard_config"]["show_ach"])
    tk.Checkbutton(cust_window, text="Achievements", variable=show_ach).pack(anchor="w")
    show_tasks = tk.BooleanVar(value=self.data["dashboard_config"]["show_tasks"])
    tk.Checkbutton(cust_window, text="Tasks", variable=show_tasks).pack(anchor="w")
    tk.Button(cust_window, text="Zapisz", command=lambda: save_custom_config(self, show_levels.get(), show_ach.get(), show_tasks.get(), cust_window)).pack(pady=10)

def save_custom_config(self, levels, ach, tasks, window):
    self.data["dashboard_config"] = {"show_levels": levels, "show_ach": ach, "show_tasks": tasks}
    save_data(self.data)
    window.destroy()
    build_dashboard(self)
