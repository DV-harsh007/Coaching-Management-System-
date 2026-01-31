# 🎓 AI Coaching Class Manager  
This project is a **simple AI-style class manager** made using Python + Tkinter.  
It helps track students, attendance, parent contacts, and gives a basic weekly report — all stored in JSON.

---

## 🚀 Features

✅ Add students with name & parent phone  
✅ Auto-generate student IDs  
✅ Mark Present/Absent  
✅ Weekly attendance summary  
✅ Basic trend/progress analysis  
✅ JSON-based local storage (no database needed)  
✅ Clean Tkinter UI  
✅ Optional WhatsApp messaging using pywhatkit  

---

## 🧠 How It Works

- Students are stored in a JSON file  
- Each student has:
  - name  
  - parent contact  
  - attendance list  
  - marks dictionary  
- You select a student from the dropdown  
- Mark attendance or generate their weekly report  
- Data updates automatically in JSON  
- No external database needed  

---

## 🛠️ Concepts Used

- Tkinter GUI  
- JSON read/write  
- Python dictionaries & lists  
- Functions & event handling  
- Simple attendance analytics  
- Optional WhatsApp automation  
- Threading + scheduling (if enabled)

---

## ▶️ How to Run

### Requirements
- Python 3.x  
- tkinter (comes by default)  
- pywhatkit (optional for WhatsApp)

### Install Dependencies
```bash
pip install pywhatkit schedule
