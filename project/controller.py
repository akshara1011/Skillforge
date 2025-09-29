from db import Database
from models import User, Skill
import random

class Controller:
    def __init__(self):
        self.db = Database()

    # ---------- Users ----------
    def add_user(self, name, email):
        self.db.execute("INSERT INTO users(name, email) VALUES(?, ?)", (name, email))

    def get_users(self):
        rows = self.db.fetchall("SELECT * FROM users")
        return [User(*row) for row in rows]

    # ---------- Skills ----------
    def add_skill(self, user_id, name, target_level=80):
        self.db.execute(
            "INSERT INTO skills(user_id, name, target_level) VALUES(?, ?, ?)",
            (user_id, name, target_level)
        )

    def get_skills(self, user_id):
        rows = self.db.fetchall("SELECT * FROM skills WHERE user_id=?", (user_id,))
        return [Skill(*row) for row in rows]

    def log_session(self, skill_id, minutes, quality):
        row = self.db.fetchall("SELECT * FROM skills WHERE id=?", (skill_id,))
        if not row:
            return None
        skill = Skill(*row[0])
        new_level = skill.update_progress(minutes, quality)
        self.db.execute("UPDATE skills SET level=? WHERE id=?", (new_level, skill_id))
        return new_level

    # ---------- Quiz ----------
    def add_question(self, skill_id, question, answer):
        self.db.execute(
            "INSERT INTO questions(skill_id, question, answer) VALUES(?, ?, ?)",
            (skill_id, question, answer)
        )

    def get_random_question(self, skill_id):
        rows = self.db.fetchall("SELECT question, answer FROM questions WHERE skill_id=?", (skill_id,))
        if not rows:
            return None
        return random.choice(rows)  # (question, answer)
