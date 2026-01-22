# main77.py
# -*- coding: utf-8 -*-

import flet as ft
import sqlite3
from datetime import datetime

# =========================
# CONFIG
# =========================
DB_NAME = "tasks.db"


# =========================
# DATABASE LAYER
# =========================
class TaskDatabase:
    def init(self, db_name: str):
        self.db_name = db_name
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def add_task(self, title: str):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done, created_at) VALUES (?, 0, ?)",
            (title, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def get_tasks(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_status(self, task_id: int, done: int):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (done, task_id),
        )
        conn.commit()
        conn.close()

    def clear_completed(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE done = 1")
        conn.commit()
        conn.close()


# =========================
# UI LAYER
# =========================
def main(page: ft.Page):
    page.title = "TODO | Автоочистка"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    db = TaskDatabase(DB_NAME)

    tasks_column = ft.Column(spacing=10)

    def load_tasks():
        tasks_column.controls.clear()
        for task_id, title, done in db.get_tasks():
            checkbox = ft.Checkbox(
                label=title,
                value=bool(done),
                on_change=lambda e, tid=task_id: toggle_task(e, tid),
            )
            tasks_column.controls.append(checkbox)
        page.update()

    def toggle_task(e, task_id):
        db.update_status(task_id, int(e.control.value))

    def add_task(e):
        if task_input.value.strip():
            db.add_task(task_input.value.strip())
            task_input.value = ""
            load_tasks()

    def clear_done(e):
        db.clear_completed()
        load_tasks()

    task_input = ft.TextField(
        hint_text="Новая задача",
        expand=True,
        on_submit=add_task,
    )

    add_button = ft.IconButton(
        icon=ft.icons.ADD,
        on_click=add_task,
    )

    clear_button = ft.ElevatedButton(
        text="Очистить выполненные",
        icon=ft.icons.DELETE_FOREVER,
        bgcolor=ft.colors.RED_400,
        on_click=clear_done,
    )

    page.add(
        ft.Text("Умный TODO-лист", size=22, weight=ft.FontWeight.BOLD),
        ft.Row([task_input, add_button]),
        clear_button,
        ft.Divider(),
        tasks_column,
    )

    load_tasks()


# =========================
# APP START
# =========================
ft.app(target=main)
