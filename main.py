import tkinter as tk

from data import PATHS, load_data, save_data
from ui import create_menu, build_intro_dashboard, run_questionnaire, build_dashboard, check_compatibility, update_task_list, add_task_window, add_task, complete_task, edit_task, save_edited_task, show_guides, add_guide_task, show_tech_tree, show_debug, customize_dashboard, save_custom_config

class LifeQuestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LifeQuest - Grywalizacja Życia")
        self.data = load_data()
        save_data(self.data)  # Zapisz po migrate
        create_menu(self)
        if not self.data["levels"] or self.data.get("question_version") != PATHS["question_version"]:
            build_intro_dashboard(self)
        else:
            build_dashboard(self)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = LifeQuestApp(root)
    root.mainloop()
