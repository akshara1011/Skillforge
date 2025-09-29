class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def __str__(self):
        return f"User({self.name}, {self.email})"


class Skill:
    def __init__(self, id, user_id, name, level=0, target_level=80):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.level = level
        self.target_level = target_level

    def update_progress(self, minutes, quality):
        points = (minutes * (quality / 10)) / 30
        self.level = min(100, self.level + int(points))
        return self.level

    def __str__(self):
        return f"Skill({self.name}, Level={self.level}/{self.target_level})"
