import customtkinter as ctk
from tkcalendar import Calendar
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

tasks = []

# ---------- IA ORGANISATION ----------
def ai_schedule(task, start_date, days, duration):

    plan = []

    for i in range(days):

        day = start_date + timedelta(days=i)

        # simple logique IA : matin si durée longue
        if duration >= 3:
            slot = "09:00"
        elif duration >= 2:
            slot = "14:00"
        else:
            slot = "18:00"

        plan.append((task, day.strftime("%Y-%m-%d"), duration, slot))

    return plan


# ---------- APPLICATION ----------

app = ctk.CTk()
app.title("Smart Time Manager")
app.geometry("1200x700")

# sidebar style Google Calendar
sidebar = ctk.CTkFrame(app, width=200)
sidebar.pack(side="left", fill="y")

main = ctk.CTkFrame(app)
main.pack(side="right", fill="both", expand=True)

title = ctk.CTkLabel(sidebar, text="Menu", font=("Arial", 20))
title.pack(pady=20)

# ---------- CALENDRIER ----------

calendar = Calendar(main)
calendar.pack(pady=20)

entry_task = ctk.CTkEntry(main, placeholder_text="Nom tâche", width=300)
entry_task.pack(pady=5)

entry_days = ctk.CTkEntry(main, placeholder_text="Nombre jours", width=300)
entry_days.pack(pady=5)

entry_duration = ctk.CTkEntry(main, placeholder_text="Durée (h)", width=300)
entry_duration.pack(pady=5)

columns = ("Tâche", "Date", "Durée", "Heure")

table = ttk.Treeview(main, columns=columns, show="headings")

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=150)

table.pack(pady=20)


# ---------- FONCTIONS ----------

def update_table():

    for row in table.get_children():
        table.delete(row)

    for t in tasks:
        table.insert("", "end", values=t)


def add_task():

    task = entry_task.get()
    days = int(entry_days.get())
    duration = float(entry_duration.get())

    date = datetime.strptime(calendar.get_date(), "%m/%d/%y")

    plan = ai_schedule(task, date, days, duration)

    for p in plan:
        tasks.append(p)

    update_table()
    save_excel()


def save_excel():

    df = pd.DataFrame(tasks,
                      columns=["Task", "Date", "Duration", "Hour"])

    df.to_excel("planning.xlsx", index=False)


def export_pdf():

    data = [["Task", "Date", "Duration", "Hour"]] + list(tasks)

    pdf = SimpleDocTemplate("planning.pdf", pagesize=letter)

    table_pdf = Table(data)

    pdf.build([table_pdf])


def show_graph():

    df = pd.DataFrame(tasks,
                      columns=["Task", "Date", "Duration", "Hour"])

    stats = df.groupby("Task")["Duration"].sum()

    plt.figure()

    stats.plot(kind="bar")

    plt.title("Temps par tâche")

    plt.ylabel("Heures")

    plt.show()


# ---------- BOUTONS ----------

btn_add = ctk.CTkButton(sidebar, text="Ajouter tâche", command=add_task)
btn_add.pack(pady=10)

btn_graph = ctk.CTkButton(sidebar, text="Statistiques", command=show_graph)
btn_graph.pack(pady=10)

btn_pdf = ctk.CTkButton(sidebar, text="Exporter PDF", command=export_pdf)
btn_pdf.pack(pady=10)

app.mainloop()