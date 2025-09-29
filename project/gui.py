# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from controller import Controller
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv


class SkillForgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkillForge - Personal Growth Tracker")
        self.root.geometry("1000x650")
        self.controller = Controller()

        # --- Dark Theme ---
        style = ttk.Style(self.root)
        self.root.tk_setPalette(background="#1e1e1e", foreground="white")
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Arial", 11))
        style.configure("TButton", background="#3a3a3a", foreground="white", padding=6)
        style.map("TButton", background=[("active", "#5a5a5a")])
        style.configure("Treeview", background="#2d2d2d", fieldbackground="#2d2d2d", foreground="white")
        style.configure("Treeview.Heading", background="#3a3a3a", foreground="white")

        # --- Notebook (Tabs) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.frame_users = ttk.Frame(self.notebook)
        self.frame_skills = ttk.Frame(self.notebook)
        self.frame_dashboard = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_users, text="Users")
        self.notebook.add(self.frame_skills, text="Skills")
        self.notebook.add(self.frame_dashboard, text="Dashboard")

        self.setup_users_tab()
        self.setup_skills_tab()
        self.setup_dashboard_tab()

    # ---------------- Users Tab ----------------
    def setup_users_tab(self):
        ttk.Label(self.frame_users, text="Users", font=("Arial", 14, "bold")).pack(pady=5)

        self.user_tree = ttk.Treeview(self.frame_users, columns=("ID", "Name", "Email"), show="headings", height=15)
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Name", text="Name")
        self.user_tree.heading("Email", text="Email")
        self.user_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.frame_users)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add User", command=self.add_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_users).pack(side="left", padx=5)

        self.load_users()

    def load_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        for u in self.controller.get_users():
            self.user_tree.insert("", "end", values=(u.id, u.name, u.email))

    def add_user(self):
        name = simpledialog.askstring("Add User", "Enter user name:")
        email = simpledialog.askstring("Add User", "Enter email:")
        if name and email:
            self.controller.add_user(name, email)
            self.load_users()

    # ---------------- Skills Tab ----------------
    def setup_skills_tab(self):
        ttk.Label(self.frame_skills, text="Skills", font=("Arial", 14, "bold")).pack(pady=5)

        self.skill_tree = ttk.Treeview(self.frame_skills, columns=("ID", "Name", "Level", "Target"), show="headings", height=15)
        for col in ("ID", "Name", "Level", "Target"):
            self.skill_tree.heading(col, text=col)
        self.skill_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.frame_skills)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Skill", command=self.add_skill).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Log Practice", command=self.log_practice).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Take Quiz", command=self.take_quiz).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_skills).pack(side="left", padx=5)

    def load_skills(self, user_id=None):
        for row in self.skill_tree.get_children():
            self.skill_tree.delete(row)

        selected = self.user_tree.selection()
        if not selected:
            return
        user_id = self.user_tree.item(selected[0])["values"][0]

        for s in self.controller.get_skills(user_id):
            self.skill_tree.insert("", "end", values=(s.id, s.name, s.level, s.target_level))

    def add_skill(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Select User", "Select a user in Users tab first!")
            return
        user_id = self.user_tree.item(selected[0])["values"][0]
        name = simpledialog.askstring("Add Skill", "Enter skill name:")
        if name:
            self.controller.add_skill(user_id, name)
            self.load_skills(user_id)

    def log_practice(self):
        selected = self.skill_tree.selection()
        if not selected:
            messagebox.showwarning("Select Skill", "Select a skill first!")
            return
        skill_id = self.skill_tree.item(selected[0])["values"][0]
        minutes = simpledialog.askinteger("Practice", "Minutes practiced:")
        quality = simpledialog.askinteger("Practice", "Quality (1-10):")
        if minutes and quality:
            new_level = self.controller.log_session(skill_id, minutes, quality)
            messagebox.showinfo("Updated", f"New Level: {new_level}")
            self.load_skills()

    def export_csv(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Select User", "Select a user first!")
            return
        user_id = self.user_tree.item(selected[0])["values"][0]
        skills = self.controller.get_skills(user_id)

        if not skills:
            messagebox.showinfo("No Data", "This user has no skills.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Skill ID", "Skill Name", "Current Level", "Target Level", "Gap (Target - Current)", "Progress %"])
                for s in skills:
                    gap = s.target_level - s.level
                    progress = round((s.level / max(1, s.target_level)) * 100, 2)
                    writer.writerow([s.id, s.name, s.level, s.target_level, gap, progress])
            messagebox.showinfo("Exported", f"Report saved at {filepath}\n\nContains graph data (Gap + Progress %)")

    def take_quiz(self):
        selected = self.skill_tree.selection()
        if not selected:
            messagebox.showwarning("Select Skill", "Select a skill first!")
            return

        skill_id = self.skill_tree.item(selected[0])["values"][0]
        qa = self.controller.get_random_question(skill_id)
        if not qa:
            messagebox.showinfo("No Questions", "No quiz questions for this skill yet.")
            return

        question, answer = qa
        user_answer = simpledialog.askstring("Quiz", question)

        if user_answer is None:
            return
        elif user_answer.strip().lower() == answer.lower():
            messagebox.showinfo("Correct ✅", "Great job! You got it right.")
        else:
            messagebox.showerror("Wrong ❌", f"Correct Answer: {answer}")

    # ---------------- Dashboard Tab ----------------
    def setup_dashboard_tab(self):
        ttk.Label(self.frame_dashboard, text="Progress Dashboard", font=("Arial", 14, "bold")).pack(pady=10)
        self.chart_frame = ttk.Frame(self.frame_dashboard)
        self.chart_frame.pack(fill="both", expand=True)
        ttk.Button(self.frame_dashboard, text="Show Progress Graph", command=self.show_chart).pack(pady=5)

    def show_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Select User", "Select a user first in Users tab!")
            return
        user_id = self.user_tree.item(selected[0])["values"][0]

        skills = self.controller.get_skills(user_id)
        if not skills:
            messagebox.showinfo("No Data", "This user has no skills yet.")
            return

        names = [s.name for s in skills]
        levels = [s.level for s in skills]
        targets = [s.target_level for s in skills]

        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#1e1e1e")
        ax.bar(names, targets, color="gray", label="Target Level")
        ax.bar(names, levels, color="cyan", label="Knowledge Gained")
        ax.set_facecolor("#1e1e1e")
        ax.tick_params(colors="white")
        ax.set_ylabel("Level", color="white")
        ax.set_title("Training vs Knowledge Gain", color="white")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
