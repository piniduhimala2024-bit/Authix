import os
import sys
import sqlite3
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from typing import Optional, List, Dict, Tuple

import psutil
from plyer import notification
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QMessageBox,
    QTextEdit,
    QDialog,
    QDateEdit,
    QTimeEdit,
    QListWidget,
    QProgressBar,
    QGridLayout,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

DB_PATH = "study_with_pinta.db"
TZ = ZoneInfo("Asia/Colombo")
SUBJECTS = ["Combined Maths", "Physics", "ICT"]
BLOCK_TYPES = ["Theory", "Practice", "Past Paper", "Revision"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class DatabaseManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id INTEGER,
                subject TEXT,
                topic TEXT,
                planned_minutes INTEGER,
                real_minutes INTEGER,
                started_at TEXT,
                ended_at TEXT,
                status TEXT,
                distractions INTEGER DEFAULT 0,
                completion_ratio REAL DEFAULT 0
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS timetable_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_name TEXT,
                subject TEXT,
                topic TEXT,
                start_time TEXT,
                end_time TEXT,
                estimated_minutes INTEGER,
                block_type TEXT,
                status TEXT DEFAULT 'planned'
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS past_papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                year INTEGER,
                paper_number INTEGER,
                marks_obtained REAL,
                total_marks REAL,
                time_taken_minutes INTEGER,
                topic_area TEXT,
                created_at TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reflection_date TEXT,
                learned TEXT,
                distraction TEXT,
                improve_tomorrow TEXT,
                created_at TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS subject_stats (
                subject TEXT PRIMARY KEY,
                total_minutes INTEGER DEFAULT 0,
                weekly_minutes INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0,
                last_updated TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS discipline_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT,
                event_type TEXT,
                points INTEGER,
                note TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_date TEXT,
                a_prob REAL,
                b_prob REAL,
                c_prob REAL,
                confidence REAL,
                focus_score REAL,
                discipline_score REAL
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        for s in SUBJECTS:
            c.execute("INSERT OR IGNORE INTO subject_stats(subject) VALUES(?)", (s,))
        self.conn.commit()

    def fetchone(self, q: str, params: tuple = ()):
        return self.conn.execute(q, params).fetchone()

    def fetchall(self, q: str, params: tuple = ()):
        return self.conn.execute(q, params).fetchall()

    def execute(self, q: str, params: tuple = ()):
        self.conn.execute(q, params)
        self.conn.commit()


class ReflectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Reflection - 9:30 PM")
        lay = QVBoxLayout(self)
        self.learned = QTextEdit()
        self.distraction = QTextEdit()
        self.improve = QTextEdit()
        lay.addWidget(QLabel("What did I learn today?"))
        lay.addWidget(self.learned)
        lay.addWidget(QLabel("Biggest distraction?"))
        lay.addWidget(self.distraction)
        lay.addWidget(QLabel("What will I improve tomorrow?"))
        lay.addWidget(self.improve)
        btn = QPushButton("Save Reflection")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)


class StatsCanvas(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(10, 8), facecolor="#0c1220")
        super().__init__(self.figure)


class StudyWithPinTaElite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager(DB_PATH)
        self.setWindowTitle("Study With PinTa Elite")
        self.resize(1400, 850)
        self.daily_target_minutes = int(self.get_setting("daily_target", "180"))
        self.active_block_id: Optional[int] = None
        self.session_started_at: Optional[datetime] = None
        self.session_remaining = 0
        self.current_distractions = 0
        self.lock_mode_enabled = False
        self.blocked_apps = self.get_setting("blocked_apps", "chrome.exe,youtube.exe").split(",")

        self.init_ui()
        self.apply_theme()
        self.load_timetable()
        self.load_past_papers()
        self.refresh_all_metrics()

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.refresh_time_and_countdown)
        self.clock_timer.start(1000)

        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.tick_session)

        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)

        self.lock_timer = QTimer(self)
        self.lock_timer.timeout.connect(self.monitor_distraction)
        self.lock_timer.start(5000)

    def init_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QHBoxLayout(root)

        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        sidebar.addWidget(QLabel("Study With PinTa"))
        for name in ["Dashboard", "Timetable", "Past Papers", "Statistics", "Lock Mode", "Settings"]:
            b = QPushButton(name)
            b.clicked.connect(lambda _, n=name: self.switch_page(n))
            sidebar.addWidget(b)
        sidebar.addStretch()

        self.stack = QStackedWidget()
        self.pages = {
            "Dashboard": self.build_dashboard_page(),
            "Timetable": self.build_timetable_page(),
            "Past Papers": self.build_pastpaper_page(),
            "Statistics": self.build_statistics_page(),
            "Lock Mode": self.build_lockmode_page(),
            "Settings": self.build_settings_page(),
        }
        for p in self.pages.values():
            self.stack.addWidget(p)

        main.addLayout(sidebar, 1)
        main.addWidget(self.stack, 5)

    def build_dashboard_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        grid = QGridLayout()

        self.lbl_datetime = QLabel()
        self.lbl_countdown = QLabel()
        self.lbl_daily = QLabel()
        self.lbl_weekly = QLabel()
        self.lbl_focus = QLabel()
        self.lbl_discipline = QLabel()
        self.lbl_prediction = QLabel()
        self.lbl_recommend = QLabel()
        self.lbl_sprint = QLabel()

        for i, w in enumerate([
            self.lbl_datetime,
            self.lbl_countdown,
            self.lbl_daily,
            self.lbl_weekly,
            self.lbl_focus,
            self.lbl_discipline,
            self.lbl_prediction,
            self.lbl_recommend,
            self.lbl_sprint,
        ]):
            grid.addWidget(w, i // 2, i % 2)

        lay.addLayout(grid)
        lay.addWidget(QLabel("Subject Balance Meter"))
        self.subject_bars = {}
        for s in SUBJECTS:
            lay.addWidget(QLabel(s))
            bar = QProgressBar()
            self.subject_bars[s] = bar
            lay.addWidget(bar)
        return page

    def build_timetable_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)

        form = QFormLayout()
        self.day_combo = QComboBox(); self.day_combo.addItems(DAYS)
        self.subject_combo = QComboBox(); self.subject_combo.addItems(SUBJECTS)
        self.topic_edit = QLineEdit()
        self.start_time = QTimeEdit(); self.start_time.setDisplayFormat("HH:mm")
        self.end_time = QTimeEdit(); self.end_time.setDisplayFormat("HH:mm")
        self.type_combo = QComboBox(); self.type_combo.addItems(BLOCK_TYPES)
        form.addRow("Day", self.day_combo)
        form.addRow("Subject", self.subject_combo)
        form.addRow("Topic", self.topic_edit)
        form.addRow("Start", self.start_time)
        form.addRow("End", self.end_time)
        form.addRow("Type", self.type_combo)
        lay.addLayout(form)
        add_btn = QPushButton("Add Timetable Block")
        add_btn.clicked.connect(self.add_timetable_block)
        lay.addWidget(add_btn)

        self.timetable = QTableWidget(0, 11)
        self.timetable.setHorizontalHeaderLabels([
            "ID", "Day", "Subject", "Topic", "Start", "End", "Est Min", "Type", "Status", "Countdown", "Actions"
        ])
        self.timetable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.timetable)
        return page

    def build_pastpaper_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        form = QFormLayout()
        self.pp_subject = QComboBox(); self.pp_subject.addItems(SUBJECTS)
        self.pp_year = QSpinBox(); self.pp_year.setRange(2000, 2100); self.pp_year.setValue(datetime.now(TZ).year)
        self.pp_num = QSpinBox(); self.pp_num.setRange(1, 5)
        self.pp_marks = QSpinBox(); self.pp_marks.setRange(0, 200)
        self.pp_total = QSpinBox(); self.pp_total.setRange(1, 200); self.pp_total.setValue(100)
        self.pp_time = QSpinBox(); self.pp_time.setRange(1, 400)
        self.pp_topic = QLineEdit()
        form.addRow("Subject", self.pp_subject)
        form.addRow("Year", self.pp_year)
        form.addRow("Paper", self.pp_num)
        form.addRow("Marks", self.pp_marks)
        form.addRow("Total", self.pp_total)
        form.addRow("Time Taken (min)", self.pp_time)
        form.addRow("Weak Topic Area", self.pp_topic)
        lay.addLayout(form)
        add = QPushButton("Log Past Paper")
        add.clicked.connect(self.add_past_paper)
        lay.addWidget(add)

        self.past_table = QTableWidget(0, 8)
        self.past_table.setHorizontalHeaderLabels(["ID", "Subject", "Year", "Paper", "Marks", "Total", "Accuracy%", "Topic"])
        self.past_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.past_table)
        return page

    def build_statistics_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        self.stats_canvas = StatsCanvas()
        lay.addWidget(self.stats_canvas)
        refresh = QPushButton("Refresh Statistics")
        refresh.clicked.connect(self.draw_stats)
        lay.addWidget(refresh)
        return page

    def build_lockmode_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        self.lock_state_label = QLabel("Lock Mode: OFF")
        lay.addWidget(self.lock_state_label)
        toggle = QPushButton("Toggle Lock Mode")
        toggle.clicked.connect(self.toggle_lock_mode)
        lay.addWidget(toggle)
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("Add blocked executable e.g. chrome.exe")
        lay.addWidget(self.app_input)
        add_btn = QPushButton("Add blocked app")
        add_btn.clicked.connect(self.add_blocked_app)
        lay.addWidget(add_btn)
        self.blocked_list = QListWidget()
        lay.addWidget(self.blocked_list)
        rem_btn = QPushButton("Remove selected")
        rem_btn.clicked.connect(self.remove_blocked_app)
        lay.addWidget(rem_btn)
        self.lock_log = QLabel("No distraction logs yet.")
        lay.addWidget(self.lock_log)
        self.refresh_blocked_list()
        return page

    def build_settings_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        self.target_spin = QSpinBox(); self.target_spin.setRange(30, 720); self.target_spin.setValue(self.daily_target_minutes)
        lay.addWidget(QLabel("Daily Target Minutes"))
        lay.addWidget(self.target_spin)
        save_target = QPushButton("Save Target")
        save_target.clicked.connect(self.save_target)
        lay.addWidget(save_target)
        backup = QPushButton("Create Database Backup")
        backup.clicked.connect(self.backup_db)
        lay.addWidget(backup)
        lay.addStretch()
        return page

    def switch_page(self, name: str):
        self.stack.setCurrentWidget(self.pages[name])
        if name == "Statistics":
            self.draw_stats()

    def apply_theme(self):
        days_left = self.days_to_exam()
        accent = "#e63946" if days_left < 30 else "#3fa7ff"
        sprint_text = "FINAL SPRINT MODE ACTIVE" if days_left < 30 else "Sprint mode inactive"
        self.setStyleSheet(f"""
            QWidget {{ background:#0b132b; color:#e5ecff; font-family:Segoe UI; font-size:13px; }}
            QPushButton {{ background:{accent}; color:white; border-radius:6px; padding:8px; }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QTimeEdit {{ background:#1c2541; border:1px solid #3a506b; border-radius:4px; padding:6px; }}
            QTableWidget {{ background:#1c2541; gridline-color:#3a506b; }}
            QHeaderView::section {{ background:#243b55; color:white; padding:5px; }}
            QProgressBar {{ border:1px solid #3a506b; text-align:center; }}
            QProgressBar::chunk {{ background:{accent}; }}
        """)
        if hasattr(self, "lbl_sprint"):
            self.lbl_sprint.setText(sprint_text)

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.db.fetchone("SELECT value FROM app_settings WHERE key=?", (key,))
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        self.db.execute("INSERT INTO app_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def days_to_exam(self) -> int:
        now = datetime.now(TZ).date()
        exam = datetime(now.year, 8, 1, tzinfo=TZ).date()
        if now > exam:
            exam = datetime(now.year + 1, 8, 1, tzinfo=TZ).date()
        return (exam - now).days

    def refresh_time_and_countdown(self):
        now = datetime.now(TZ)
        self.lbl_datetime.setText(f"Sri Lanka Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        self.lbl_countdown.setText(f"Countdown to Exam (Aug 1): {self.days_to_exam()} days")

    def add_timetable_block(self):
        start = self.start_time.time().toString("HH:mm")
        end = self.end_time.time().toString("HH:mm")
        st = datetime.strptime(start, "%H:%M")
        et = datetime.strptime(end, "%H:%M")
        minutes = int((et - st).total_seconds() / 60)
        if minutes <= 0:
            QMessageBox.warning(self, "Invalid", "End time must be after start time.")
            return
        self.db.execute(
            "INSERT INTO timetable_blocks(day_name,subject,topic,start_time,end_time,estimated_minutes,block_type) VALUES(?,?,?,?,?,?,?)",
            (self.day_combo.currentText(), self.subject_combo.currentText(), self.topic_edit.text().strip(), start, end, minutes, self.type_combo.currentText()),
        )
        self.topic_edit.clear()
        self.load_timetable()
        self.refresh_all_metrics()

    def load_timetable(self):
        rows = self.db.fetchall("SELECT * FROM timetable_blocks ORDER BY id DESC")
        self.timetable.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row["id"], row["day_name"], row["subject"], row["topic"], row["start_time"], row["end_time"], row["estimated_minutes"], row["block_type"], row["status"], "--"]
            for c, val in enumerate(vals):
                self.timetable.setItem(r, c, QTableWidgetItem(str(val)))
            action_widget = QWidget()
            a_lay = QHBoxLayout(action_widget)
            a_lay.setContentsMargins(0, 0, 0, 0)
            for txt, fn in [
                ("Start", lambda _, bid=row["id"]: self.start_session(bid)),
                ("Pause", self.pause_session),
                ("Stop", self.stop_session),
                ("Done", lambda _, bid=row["id"]: self.mark_status(bid, "done")),
                ("Partial", lambda _, bid=row["id"]: self.mark_status(bid, "partial")),
            ]:
                b = QPushButton(txt)
                b.clicked.connect(fn)
                a_lay.addWidget(b)
            self.timetable.setCellWidget(r, 10, action_widget)

    def start_session(self, block_id: int):
        row = self.db.fetchone("SELECT * FROM timetable_blocks WHERE id=?", (block_id,))
        if not row:
            return
        if self.active_block_id:
            QMessageBox.warning(self, "Active Session", "Stop current session first.")
            return
        self.active_block_id = block_id
        self.session_started_at = datetime.now(TZ)
        self.session_remaining = int(row["estimated_minutes"] * 60)
        self.current_distractions = 0
        self.session_timer.start(1000)
        self.notify("Session Started", f"{row['subject']} - {row['topic']}")

    def pause_session(self):
        if self.session_timer.isActive():
            self.session_timer.stop()
        else:
            if self.active_block_id:
                self.session_timer.start(1000)

    def stop_session(self):
        if not self.active_block_id:
            return
        self.finish_session("stopped")

    def mark_status(self, block_id: int, status: str):
        self.db.execute("UPDATE timetable_blocks SET status=? WHERE id=?", (status, block_id))
        self.load_timetable()
        points = 8 if status == "done" else 3
        self.log_discipline("completion", points, f"Block {block_id} marked {status}")
        self.refresh_all_metrics()

    def tick_session(self):
        if not self.active_block_id:
            return
        self.session_remaining -= 1
        if self.session_remaining == 300:
            self.notify("5 Minutes Remaining", "Push till the finish!")
        for r in range(self.timetable.rowCount()):
            if self.timetable.item(r, 0) and int(self.timetable.item(r, 0).text()) == self.active_block_id:
                self.timetable.setItem(r, 9, QTableWidgetItem(str(timedelta(seconds=max(0, self.session_remaining)))))
        if self.session_remaining <= 0:
            self.finish_session("done")

    def finish_session(self, status: str):
        self.session_timer.stop()
        block = self.db.fetchone("SELECT * FROM timetable_blocks WHERE id=?", (self.active_block_id,))
        now = datetime.now(TZ)
        real_minutes = max(1, int((now - self.session_started_at).total_seconds() / 60))
        completion = min(1.0, real_minutes / max(1, block["estimated_minutes"]))
        self.db.execute(
            """INSERT INTO sessions(block_id,subject,topic,planned_minutes,real_minutes,started_at,ended_at,status,distractions,completion_ratio)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (self.active_block_id, block["subject"], block["topic"], block["estimated_minutes"], real_minutes,
             self.session_started_at.isoformat(), now.isoformat(), status, self.current_distractions, completion),
        )
        self.db.execute("UPDATE timetable_blocks SET status=? WHERE id=?", (status, self.active_block_id))
        self.update_subject_stats()
        self.log_discipline("session", 10 if status == "done" else 4, f"Session {status}")
        self.active_block_id = None
        self.notify("Session Complete", f"{block['subject']} session {status}.")
        QApplication.beep()
        self.load_timetable()
        self.refresh_all_metrics()

    def add_past_paper(self):
        marks = self.pp_marks.value(); total = self.pp_total.value()
        self.db.execute(
            "INSERT INTO past_papers(subject,year,paper_number,marks_obtained,total_marks,time_taken_minutes,topic_area,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (self.pp_subject.currentText(), self.pp_year.value(), self.pp_num.value(), marks, total, self.pp_time.value(), self.pp_topic.text().strip(), datetime.now(TZ).isoformat()),
        )
        self.pp_topic.clear()
        self.load_past_papers()
        self.update_subject_stats()
        self.refresh_all_metrics()

    def load_past_papers(self):
        rows = self.db.fetchall("SELECT * FROM past_papers ORDER BY id DESC")
        self.past_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            acc = (row["marks_obtained"] / row["total_marks"]) * 100
            vals = [row["id"], row["subject"], row["year"], row["paper_number"], row["marks_obtained"], row["total_marks"], f"{acc:.1f}", row["topic_area"]]
            for c, v in enumerate(vals):
                self.past_table.setItem(r, c, QTableWidgetItem(str(v)))

    def update_subject_stats(self):
        week_start = (datetime.now(TZ) - timedelta(days=datetime.now(TZ).weekday())).date().isoformat()
        for s in SUBJECTS:
            total = self.db.fetchone("SELECT COALESCE(SUM(real_minutes),0) v FROM sessions WHERE subject=?", (s,))["v"]
            weekly = self.db.fetchone(
                "SELECT COALESCE(SUM(real_minutes),0) v FROM sessions WHERE subject=? AND date(started_at)>=date(?)", (s, week_start)
            )["v"]
            acc_row = self.db.fetchone("SELECT AVG((marks_obtained/total_marks)*100) a FROM past_papers WHERE subject=?", (s,))
            acc = round(acc_row["a"] or 0, 2)
            self.db.execute(
                "UPDATE subject_stats SET total_minutes=?, weekly_minutes=?, accuracy=?, last_updated=? WHERE subject=?",
                (int(total), int(weekly), acc, datetime.now(TZ).isoformat(), s),
            )

    def calculate_scores(self) -> Dict[str, float]:
        today = datetime.now(TZ).date().isoformat()
        week_start = (datetime.now(TZ) - timedelta(days=datetime.now(TZ).weekday())).date().isoformat()
        daily = self.db.fetchone("SELECT COALESCE(SUM(real_minutes),0) v FROM sessions WHERE date(started_at)=date(?)", (today,))["v"]
        weekly = self.db.fetchone("SELECT COALESCE(SUM(real_minutes),0) v FROM sessions WHERE date(started_at)>=date(?)", (week_start,))["v"]
        completion = self.db.fetchone("SELECT AVG(completion_ratio) a FROM sessions")
        completion_score = (completion["a"] or 0) * 100
        distractions = self.db.fetchone("SELECT COALESCE(SUM(distractions),0) d FROM sessions WHERE date(started_at)>=date(?)", (week_start,))["d"]
        focus = max(0, min(100, (completion_score * 0.5) + (min(100, weekly / (self.daily_target_minutes * 7) * 100) * 0.5) - distractions * 2))
        discipline = self.compute_discipline_score()
        prediction = self.compute_prediction(focus, discipline)
        return {"daily": daily, "weekly": weekly, "focus": focus, "discipline": discipline, **prediction}

    def compute_discipline_score(self) -> float:
        week_start = (datetime.now(TZ) - timedelta(days=datetime.now(TZ).weekday())).date().isoformat()
        logs = self.db.fetchall("SELECT points FROM discipline_logs WHERE date(log_date)>=date(?)", (week_start,))
        total = sum([r["points"] for r in logs])
        return max(0, min(100, 50 + total))

    def compute_prediction(self, focus: float, discipline: float) -> Dict[str, float]:
        stats = self.db.fetchall("SELECT * FROM subject_stats")
        hours_component = min(100, sum([s["weekly_minutes"] for s in stats]) / 12)
        accuracy_component = sum([s["accuracy"] for s in stats]) / len(stats) if stats else 0
        consistency = self.compute_streaks()["daily"] * 5
        score = (hours_component * 0.30) + (accuracy_component * 0.30) + (focus * 0.20) + (discipline * 0.15) + (consistency * 0.05)
        a = max(5, min(95, score))
        b = max(3, min(90, 100 - abs(score - 70)))
        c = max(2, min(80, 100 - a - b + 20))
        total = a + b + c
        a, b, c = [round((x / total) * 100, 2) for x in (a, b, c)]
        confidence = round(min(100, (focus + discipline + accuracy_component) / 3), 2)
        self.db.execute(
            "INSERT INTO predictions(prediction_date,a_prob,b_prob,c_prob,confidence,focus_score,discipline_score) VALUES(?,?,?,?,?,?,?)",
            (datetime.now(TZ).isoformat(), a, b, c, confidence, round(focus, 2), round(discipline, 2)),
        )
        return {"a": a, "b": b, "c": c, "confidence": confidence}

    def compute_streaks(self) -> Dict[str, int]:
        days = self.db.fetchall("SELECT DISTINCT date(started_at) d FROM sessions ORDER BY d")
        if not days:
            return {"daily": 0, "longest": 0}
        day_list = [datetime.fromisoformat(d["d"]).date() for d in days]
        day_set = set(day_list)
        today = datetime.now(TZ).date()
        current = 0
        d = today
        while d in day_set:
            current += 1
            d -= timedelta(days=1)
        longest = 1
        run = 1
        for i in range(1, len(day_list)):
            if (day_list[i] - day_list[i - 1]).days == 1:
                run += 1
                longest = max(longest, run)
            else:
                run = 1
        return {"daily": current, "longest": longest}

    def recommend_next_session(self) -> str:
        stats = self.db.fetchall("SELECT * FROM subject_stats")
        if not stats:
            return "Combined Maths - Functions"
        weak = sorted(stats, key=lambda x: (x["weekly_minutes"], x["accuracy"]))[0]
        topic_map = {
            "Combined Maths": "Integration",
            "Physics": "Waves",
            "ICT": "Database Systems",
        }
        return f"{weak['subject']} - {topic_map.get(weak['subject'], 'Revision')}"

    def refresh_all_metrics(self):
        self.apply_theme()
        self.update_subject_stats()
        scores = self.calculate_scores()
        self.lbl_daily.setText(f"Daily Study Minutes: {scores['daily']}")
        self.lbl_weekly.setText(f"Weekly Study Minutes: {scores['weekly']}")
        self.lbl_focus.setText(f"Focus Score: {scores['focus']:.1f}/100")
        self.lbl_discipline.setText(f"Discipline Score: {scores['discipline']:.1f}/100")
        self.lbl_prediction.setText(f"Performance Prediction: A {scores['a']}% | B {scores['b']}% | C {scores['c']}% (Conf {scores['confidence']}%)")
        self.lbl_recommend.setText(f"Recommended Next Session: {self.recommend_next_session()}")
        sub = self.db.fetchall("SELECT subject, weekly_minutes FROM subject_stats")
        total = sum([s["weekly_minutes"] for s in sub]) or 1
        for s in sub:
            self.subject_bars[s["subject"]].setValue(int((s["weekly_minutes"] / total) * 100))
        self.refresh_time_and_countdown()

    def draw_stats(self):
        fig = self.stats_canvas.figure
        fig.clear()
        axs = fig.subplots(3, 3)
        daily = self.db.fetchall("SELECT date(started_at) d, SUM(real_minutes) m FROM sessions GROUP BY d ORDER BY d DESC LIMIT 14")
        d_x = [r["d"] for r in reversed(daily)]; d_y = [r["m"] for r in reversed(daily)]
        axs[0, 0].plot(d_x, d_y, color="#3fa7ff"); axs[0, 0].set_title("Daily Study Minutes")
        week = self.db.fetchall("SELECT strftime('%Y-%W', started_at) w, SUM(real_minutes) m FROM sessions GROUP BY w ORDER BY w DESC LIMIT 8")
        axs[0, 1].bar([r["w"] for r in reversed(week)], [r["m"] for r in reversed(week)], color="#66bb6a"); axs[0, 1].set_title("Weekly Totals")
        subj = self.db.fetchall("SELECT subject, SUM(real_minutes) m FROM sessions GROUP BY subject")
        if subj:
            axs[0, 2].pie([r["m"] for r in subj], labels=[r["subject"] for r in subj], autopct="%1.1f%%")
        axs[0, 2].set_title("Subject Distribution")
        pp = self.db.fetchall("SELECT created_at, AVG((marks_obtained/total_marks)*100) a FROM past_papers GROUP BY date(created_at) ORDER BY created_at")
        axs[1, 0].plot([r["created_at"][:10] for r in pp], [r["a"] for r in pp], color="#ffa726"); axs[1, 0].set_title("Past Paper Improvement")
        dl = self.db.fetchall("SELECT log_date, SUM(points) p FROM discipline_logs GROUP BY date(log_date) ORDER BY log_date")
        axs[1, 1].plot([r["log_date"][:10] for r in dl], [r["p"] for r in dl], color="#ef5350"); axs[1, 1].set_title("Discipline Score Trend")
        pr = self.db.fetchall("SELECT prediction_date, focus_score FROM predictions ORDER BY id DESC LIMIT 15")
        axs[1, 2].plot([r["prediction_date"][:10] for r in reversed(pr)], [r["focus_score"] for r in reversed(pr)], color="#ab47bc"); axs[1, 2].set_title("Focus Score")
        conf = self.db.fetchall("SELECT prediction_date, confidence FROM predictions ORDER BY id DESC LIMIT 15")
        axs[2, 0].plot([r["prediction_date"][:10] for r in reversed(conf)], [r["confidence"] for r in reversed(conf)], color="#26c6da"); axs[2, 0].set_title("Prediction Confidence")
        weak = self.db.fetchall("SELECT subject, AVG(100-(marks_obtained/total_marks)*100) w FROM past_papers GROUP BY subject")
        axs[2, 1].bar([r["subject"] for r in weak], [r["w"] or 0 for r in weak], color="#8d6e63"); axs[2, 1].set_title("Weak Area Intensity")
        streak = self.compute_streaks()
        axs[2, 2].bar(["Current", "Longest"], [streak["daily"], streak["longest"]], color=["#42a5f5", "#26a69a"]); axs[2, 2].set_title("Streaks")
        for row in axs:
            for ax in row:
                ax.tick_params(axis='x', labelrotation=40)
                ax.set_facecolor("#111b2f")
        fig.tight_layout()
        self.stats_canvas.draw()

    def notify(self, title: str, message: str):
        try:
            notification.notify(title=title, message=message, app_name="Study With PinTa Elite", timeout=5)
        except Exception:
            pass

    def check_reminders(self):
        now = datetime.now(TZ)
        today = now.date().isoformat()
        if now.hour == 18 and now.minute == 0:
            mins = self.db.fetchone("SELECT COALESCE(SUM(real_minutes),0) v FROM sessions WHERE date(started_at)=date(?)", (today,))["v"]
            if mins == 0:
                self.notify("No Study Logged", "No study done by 6 PM. Start now to protect streak.")

        if now.hour == 21 and now.minute == 30:
            existing = self.db.fetchone("SELECT id FROM reflections WHERE reflection_date=?", (today,))
            if not existing:
                dialog = ReflectionDialog()
                if dialog.exec_() == QDialog.Accepted:
                    self.db.execute(
                        "INSERT INTO reflections(reflection_date,learned,distraction,improve_tomorrow,created_at) VALUES(?,?,?,?,?)",
                        (today, dialog.learned.toPlainText(), dialog.distraction.toPlainText(), dialog.improve.toPlainText(), now.isoformat()),
                    )
        tomorrow = (now + timedelta(days=1)).strftime("%A")
        tmr = self.db.fetchone("SELECT COUNT(*) c FROM timetable_blocks WHERE day_name=?", (tomorrow,))["c"]
        if tmr == 0:
            self.lbl_sprint.setText(self.lbl_sprint.text() + " | ⚠ Tomorrow timetable missing")

    def toggle_lock_mode(self):
        self.lock_mode_enabled = not self.lock_mode_enabled
        self.lock_state_label.setText(f"Lock Mode: {'ON' if self.lock_mode_enabled else 'OFF'}")

    def add_blocked_app(self):
        app = self.app_input.text().strip().lower()
        if app and app not in self.blocked_apps:
            self.blocked_apps.append(app)
            self.set_setting("blocked_apps", ",".join(self.blocked_apps))
            self.refresh_blocked_list()
            self.app_input.clear()

    def remove_blocked_app(self):
        item = self.blocked_list.currentItem()
        if item:
            app = item.text()
            if app in self.blocked_apps:
                self.blocked_apps.remove(app)
                self.set_setting("blocked_apps", ",".join(self.blocked_apps))
                self.refresh_blocked_list()

    def refresh_blocked_list(self):
        self.blocked_list.clear()
        for app in sorted([a for a in self.blocked_apps if a]):
            self.blocked_list.addItem(app)

    def monitor_distraction(self):
        if not (self.lock_mode_enabled and self.active_block_id):
            return
        current = self.get_active_process_name()
        if current and current.lower() in [a.lower() for a in self.blocked_apps if a]:
            self.current_distractions += 1
            self.log_discipline("distraction", -3, f"Blocked app opened: {current}")
            self.lock_log.setText(f"Warning: Distraction detected - {current}")
            QMessageBox.warning(self, "Distraction Warning", f"Blocked app in use during study: {current}")

    def get_active_process_name(self) -> Optional[str]:
        if os.name != "nt":
            return None
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            p = psutil.Process(pid.value)
            return p.name()
        except Exception:
            return None

    def log_discipline(self, event_type: str, points: int, note: str):
        self.db.execute(
            "INSERT INTO discipline_logs(log_date,event_type,points,note) VALUES(?,?,?,?)",
            (datetime.now(TZ).isoformat(), event_type, points, note),
        )

    def save_target(self):
        self.daily_target_minutes = self.target_spin.value()
        if self.days_to_exam() < 30:
            self.daily_target_minutes = int(self.daily_target_minutes * 1.2)
        self.set_setting("daily_target", str(self.daily_target_minutes))
        QMessageBox.information(self, "Saved", f"Daily target set to {self.daily_target_minutes} minutes.")
        self.refresh_all_metrics()

    def backup_db(self):
        ts = datetime.now(TZ).strftime("%Y%m%d_%H%M%S")
        target = f"backup_study_with_pinta_{ts}.db"
        self.db.conn.commit()
        shutil.copy(DB_PATH, target)
        QMessageBox.information(self, "Backup", f"Backup created: {target}")


def main():
    app = QApplication(sys.argv)
    win = StudyWithPinTaElite()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
