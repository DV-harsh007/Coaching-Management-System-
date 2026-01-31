import tkinter as tk
from tkinter import messagebox, ttk
import pywhatkit
import matplotlib.pyplot as plt
import schedule
import time
import threading
import json
import os

# ===================== JSON =====================
DATA_FILE = "students.json"

def load_data():
    global students, next_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            students = {int(k): v for k, v in data.get("students", {}).items()}
            next_id = data.get("next_id", 1)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "students": students,
            "next_id": next_id
        }, f, indent=4)

# ===================== DATA =====================
students = {}
current_student_id = None
next_id = 1
load_data()

# ===================== AI-STYLE PROGRESS ANALYSIS =====================
def progress_analysis(scores):
    if len(scores) < 2:
        return "Insufficient data"
    trend = scores[-1] - scores[0]
    if trend > 5:
        return "Improving"
    elif trend < -5:
        return "Declining"
    else:
        return "Stable"

def ai_remark(percent):
    if percent >= 85:
        return "Excellent consistency and academic dedication."
    elif percent >= 75:
        return "Good progress. Consistency should be maintained."
    elif percent >= 60:
        return "Average performance. Improvement is required."
    else:
        return "Immediate academic attention is advised."

# ===================== STUDENT MANAGEMENT =====================
def refresh_dropdown():
    menu = student_menu["menu"]
    menu.delete(0, "end")
    for sid, data in students.items():
        menu.add_command(
            label=f"{sid} - {data['name']}",
            command=lambda value=sid: select_student(value)
        )
    student_var.set("Select Student")

def select_student(sid):
    global current_student_id
    current_student_id = sid
    student_var.set(f"{sid} - {students[sid]['name']}")
    update_dashboard()

def add_student():
    global next_id
    name = name_entry.get().strip()
    phone = phone_entry.get().strip()

    if not name or not phone:
        messagebox.showerror("Error", "Enter student name and parent phone")
        return

    if not phone.startswith("+") or len(phone) < 10:
        messagebox.showerror("Error", "Enter valid phone with country code")
        return

    students[next_id] = {
        "name": name,
        "parent_phone": phone,
        "attendance": [],
        "marks": {}
    }

    next_id += 1
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    save_data()
    refresh_dropdown()

def remove_student():
    global current_student_id
    if current_student_id is None:
        messagebox.showwarning("Warning", "Select a student first")
        return
    del students[current_student_id]
    current_student_id = None
    save_data()
    refresh_dropdown()
    report_box.delete("1.0", tk.END)
    clear_dashboard()

# ===================== ATTENDANCE =====================
def mark_attendance(status):
    if current_student_id is None:
        messagebox.showwarning("Warning", "Select a student first")
        return
    students[current_student_id]["attendance"].append(status)
    students[current_student_id]["attendance"] = students[current_student_id]["attendance"][-30:]
    save_data()
    update_dashboard()

def weekly_attendance():
    if current_student_id is None:
        return 0,0,0,0
    records = students[current_student_id]["attendance"][-7:]
    present = records.count("P")
    absent = records.count("A")
    total = len(records)
    percent = round((present / total) * 100, 2) if total else 0
    return present, absent, total, percent

# ===================== MARKS =====================
def add_marks():
    if current_student_id is None:
        messagebox.showwarning("Warning", "Select a student first")
        return

    subject = subject_entry.get().strip().lower()
    try:
        score = float(marks_entry.get())
    except:
        messagebox.showerror("Error", "Enter valid marks")
        return

    students[current_student_id]["marks"].setdefault(subject, []).append(score)
    subject_entry.delete(0, tk.END)
    marks_entry.delete(0, tk.END)
    save_data()
    update_dashboard()

# ===================== DASHBOARD =====================
def update_dashboard():
    if current_student_id is None:
        return
    p, a, t, per = weekly_attendance()
    dash_present.config(text=f"Present: {p}")
    dash_absent.config(text=f"Absent: {a}")
    dash_total.config(text=f"Classes: {t}")
    dash_percent.config(text=f"Weekly %: {per}%")

def clear_dashboard():
    dash_present.config(text="Present: -")
    dash_absent.config(text="Absent: -")
    dash_total.config(text="Classes: -")
    dash_percent.config(text="Weekly %: -")

# ===================== REPORT =====================
def generate_report():
    if current_student_id is None:
        messagebox.showwarning("Warning", "Select a student first")
        return

    s = students[current_student_id]
    present, absent, total, percent = weekly_attendance()

    report = f"""V.R CLASSES
STUDENT MANAGEMENT SYSTEM

WEEKLY STUDENT REPORT

Student Name: {s['name']}

Attendance Summary (Last 7 Classes)
• Classes Conducted : {total}
• Present            : {present}
• Absent             : {absent}
• Attendance %       : {percent}%

Academic Performance
"""

    if not s["marks"]:
        report += "No academic evaluations conducted.\n"
    else:
        for sub, scores in s["marks"].items():
            latest = scores[-1]
            avg = round(sum(scores) / len(scores), 1)
            trend = progress_analysis(scores)
            report += f"• {sub.capitalize():8}: Latest {latest} | Average {avg} | {trend}\n"

    remark = ai_remark(percent)

    report += f"""

Overall Remark:
{remark}

Yours faithfully,
V.R CLASSES STUDENT MANAGEMENT SYSTEM
Dev – HARSHAL G.
"""
    report_box.delete("1.0", tk.END)
    report_box.insert(tk.END, report)

# ===================== WHATSAPP MESSAGE =====================
def generate_parent_message():
    if current_student_id is None:
        return "No student selected."
    s = students[current_student_id]
    present, absent, total, percent = weekly_attendance()

    marks_text = ""
    if not s["marks"]:
        marks_text = "No academic evaluations conducted this week."
    else:
        for sub, scores in s["marks"].items():
            latest = scores[-1]
            avg = round(sum(scores) / len(scores), 1)
            trend = progress_analysis(scores)
            marks_text += f"{sub.capitalize()}: Latest {latest}, Average {avg}, {trend}\n"

    remark = ai_remark(percent)

    return f"""
Dear Parent,

Greetings from V.R Classes.

Please find below the weekly academic update for your ward {s['name']}.

Attendance Summary (Last 7 Classes):
Classes Conducted : {total}
Present            : {present}
Absent             : {absent}
Attendance %       : {percent}%

Academic Performance:
{marks_text}

Overall Remark:
{remark}

Yours faithfully,
V.R CLASSES STUDENT MANAGEMENT SYSTEM
Dev – HARSHAL G.
"""

def send_whatsapp():
    if current_student_id is None:
        messagebox.showwarning("Warning", "Select a student first")
        return
    try:
        pywhatkit.sendwhatmsg_instantly(
            students[current_student_id]["parent_phone"],
            generate_parent_message(),
            wait_time=12,
            tab_close=True
        )
    except Exception as e:
        messagebox.showerror("WhatsApp Error", f"Failed to send message:\n{e}")

# ===================== GRAPHS =====================
def show_graph():
    if current_student_id is None:
        messagebox.showwarning("Warning", "Select a student first")
        return

    marks = students[current_student_id]["marks"]
    if not marks:
        messagebox.showinfo("Info", "No marks available")
        return

    for sub, scores in marks.items():
        plt.figure()
        plt.plot(scores, marker="o")
        plt.title(f"{sub.capitalize()} Performance")
        plt.xlabel("Test Number")
        plt.ylabel("Marks")
        plt.show()

# ===================== AUTO WEEKLY WHATSAPP =====================
def weekly_auto_send():
    if not students:
        return
    for sid in students:
        global current_student_id
        current_student_id = sid
        send_whatsapp()

def run_scheduler():
    schedule.every().sunday.at("20:00").do(weekly_auto_send)
    while True:
        schedule.run_pending()
        time.sleep(60)

# ===================== UI =====================
root = tk.Tk()
root.title("Weekly Student Management System")
root.geometry("720x760")
root.configure(bg="#1e1e1e")

# ===================== STYLES =====================
label_font = ("Segoe UI", 16, "bold")
entry_font = ("Segoe UI", 12)
button_font = ("Segoe UI", 10, "bold")
text_bg = "#2e2e2e"
text_fg = "#ffffff"
entry_bg = "#2e2e2e"
entry_fg = "#cccccc"
button_bg = "#4CAF50"
button_fg = "#ffffff"

# Header
tk.Label(root, text="STUDENT MANAGEMENT DASHBOARD",
         font=label_font, fg="#ffffff", bg="#1e1e1e").pack(pady=10)

# Add student
top = tk.Frame(root, bg="#1e1e1e")
top.pack(pady=5)

def add_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg="#aaaaaa")
    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg=entry_fg)
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg="#aaaaaa")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

name_entry = tk.Entry(top, width=18, font=entry_font, bg=entry_bg, fg=entry_fg, insertbackground="white")
name_entry.grid(row=0, column=0, padx=5)
add_placeholder(name_entry, "Student Name")

phone_entry = tk.Entry(top, width=18, font=entry_font, bg=entry_bg, fg=entry_fg, insertbackground="white")
phone_entry.grid(row=0, column=1, padx=5)
add_placeholder(phone_entry, "+91XXXXXXXXXX")

tk.Button(top, text="ADD", font=button_font, bg=button_bg, fg=button_fg, width=10, command=add_student).grid(row=0, column=2, padx=5)
tk.Button(top, text="REMOVE", font=button_font, bg="#f44336", fg=button_fg, width=10, command=remove_student).grid(row=0, column=3, padx=5)

student_var = tk.StringVar()
student_menu = tk.OptionMenu(root, student_var, "")
student_menu.config(font=entry_font, bg="#2e2e2e", fg="#ffffff", width=40)
student_menu.pack(pady=10)

# 🔥 JSON Loaded Above  
# 🔥 NOW Refresh Dropdown AFTER menu exists
refresh_dropdown()

# Dashboard
dash = tk.Frame(root, bd=2, relief="groove", bg="#2e2e2e")
dash.pack(pady=10)

dash_present = tk.Label(dash, text="Present: -", width=20, font=entry_font, bg="#2e2e2e", fg="#ffffff")
dash_present.grid(row=0, column=0, padx=5, pady=5)

dash_absent = tk.Label(dash, text="Absent: -", width=20, font=entry_font, bg="#2e2e2e", fg="#ffffff")
dash_absent.grid(row=0, column=1, padx=5, pady=5)

dash_total = tk.Label(dash, text="Classes: -", width=20, font=entry_font, bg="#2e2e2e", fg="#ffffff")
dash_total.grid(row=1, column=0, padx=5, pady=5)

dash_percent = tk.Label(dash, text="Weekly %: -", width=20, font=entry_font, bg="#2e2e2e", fg="#ffffff")
dash_percent.grid(row=1, column=1, padx=5, pady=5)

# Attendance
att = tk.Frame(root, bg="#1e1e1e")
att.pack(pady=5)

tk.Button(att, text="PRESENT", font=button_font, bg="#2196F3", fg=button_fg, width=15,
          command=lambda: mark_attendance("P")).grid(row=0, column=0, padx=5, pady=5)

tk.Button(att, text="ABSENT", font=button_font, bg="#f44336", fg=button_fg, width=15,
          command=lambda: mark_attendance("A")).grid(row=0, column=1, padx=5, pady=5)

# Marks
marks_frame = tk.Frame(root, bg="#1e1e1e")
marks_frame.pack(pady=10)

subject_entry = tk.Entry(marks_frame, width=15, font=entry_font, bg=entry_bg, fg=entry_fg, insertbackground="white")
subject_entry.grid(row=0, column=0, padx=5)
add_placeholder(subject_entry, "Subject")

marks_entry = tk.Entry(marks_frame, width=10, font=entry_font, bg=entry_bg, fg=entry_fg, insertbackground="white")
marks_entry.grid(row=0, column=1, padx=5)
add_placeholder(marks_entry, "Marks")

tk.Button(marks_frame, text="ADD MARKS", font=button_font, bg=button_bg, fg=button_fg, width=15, command=add_marks).grid(row=0, column=2, padx=5)

# Actions
tk.Button(root, text="GENERATE WEEKLY REPORT", font=button_font, bg="#FFC107", fg="#000000", width=35,
          command=generate_report).pack(pady=5)

tk.Button(root, text="SEND WEEKLY UPDATE TO PARENT", font=button_font, bg="#4CAF50", fg=button_fg, width=35,
          command=send_whatsapp).pack(pady=5)

tk.Button(root, text="VIEW PERFORMANCE GRAPH", font=button_font, bg="#03A9F4", fg=button_fg, width=35,
          command=show_graph).pack(pady=5)

report_box = tk.Text(root, height=16, width=85, font=entry_font, bg="#2e2e2e", fg="#ffffff", insertbackground="white")
report_box.pack(pady=10)

# Start scheduler thread
threading.Thread(target=run_scheduler, daemon=True).start()

root.mainloop()



