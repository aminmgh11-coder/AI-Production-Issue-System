import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import ollama
from PIL import Image, ImageTk


def analyze_with_ai(
        problem_type,
        problem_description,
        downtime,
        temperature,
        pressure,
        cycle_time,
        comment
):
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": """
You are an industrial maintenance assistant specialized
in injection molding machines.

Analyze the complete production issue using both
process data and the operator comment.

Return ONLY valid JSON.

Use one category:
Mechanical
Electrical
Process
Quality
Tooling
Unknown

Use one severity:
LOW
MEDIUM
HIGH

Return:
category
severity
possible_cause
recommended_action
"""
            },
            {
                "role": "user",
                "content": f"""
Problem Type: {problem_type}
Problem Description: {problem_description}
Downtime: {downtime} minutes
Temperature: {temperature} °C
Injection Pressure: {pressure} bar
Cycle Time: {cycle_time} seconds
Operator Comment: {comment}

Analyze all information together.
"""
            }
        ],
        format="json"
    )

    return json.loads(response["message"]["content"])

def submit_report():

    # -----------------------------
    # 1. Check numeric inputs
    # -----------------------------

    try:
        downtime = int(downtime_entry.get())
        temperature = float(temperature_entry.get())
        pressure = float(pressure_entry.get())
        cycle_time = float(cycle_time_entry.get())

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Downtime, Temperature, Pressure and Cycle Time must be numbers."
        )
        return

    # -----------------------------
    # 2. Check text inputs
    # -----------------------------

    machine_id = machine_id_entry.get().strip()
    problem_type = problem_type_entry.get().strip()
    problem_description = problem_description_entry.get().strip()
    operator_comment = operator_comment_entry.get().strip()

    if not machine_id:
        messagebox.showerror(
            "Invalid Input",
            "Machine ID cannot be empty."
        )
        return

    if not problem_type:
        messagebox.showerror(
            "Invalid Input",
            "Problem Type cannot be empty."
        )
        return

    if not operator_comment:
        messagebox.showerror(
            "Invalid Input",
            "Operator Comment cannot be empty."
        )
        return

    # -----------------------------
    # 3. Engineering validation
    # -----------------------------

    if downtime < 0:
        messagebox.showerror(
            "Invalid Input",
            "Downtime cannot be negative."
        )
        return

    if temperature < 100 or temperature > 350:
        messagebox.showerror(
            "Invalid Input",
            "Temperature must be between 100 and 350 °C."
        )
        return

    if pressure <= 0:
        messagebox.showerror(
            "Invalid Input",
            "Injection pressure must be greater than 0."
        )
        return

    if cycle_time <= 0:
        messagebox.showerror(
            "Invalid Input",
            "Cycle time must be greater than 0."
        )
        return

    # -----------------------------
    # 4. Rule-based severity
    # -----------------------------

    if downtime > 25:
        rule_severity = "HIGH"

    elif downtime > 15:
        rule_severity = "MEDIUM"

    else:
        rule_severity = "LOW"

    # -----------------------------
    # 5. AI analysis
    # -----------------------------

    try:
        ai_result = analyze_with_ai(
            problem_type,
            problem_description,
            downtime,
            temperature,
            pressure,
            cycle_time,
            operator_comment
        )

    except Exception as error:
        messagebox.showerror(
            "AI Error",
            f"Ollama could not analyze the report.\n\n{error}"
        )
        return

    # -----------------------------
    # 6. Load existing reports
    # -----------------------------

    try:
        with open("processed_reports.json", "r") as file:
            reports = json.load(file)

    except FileNotFoundError:
        reports = []

    # -----------------------------
    # 7. Generate Report ID
    # -----------------------------

    report_number = len(reports) + 1
    report_id = f"RPT-{report_number:04d}"

    # -----------------------------
    # 8. Timestamp
    # -----------------------------

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -----------------------------
    # 9. Create final report
    # -----------------------------

    new_report = {

        "report_id": report_id,

        "timestamp": timestamp,

        "machine_id": machine_id,

        "problem_type": problem_type,

        "problem_description": problem_description,

        "downtime_minutes": downtime,

        "temperature_c": temperature,

        "injection_pressure_bar": pressure,

        "cycle_time_seconds": cycle_time,

        "operator_comment": operator_comment,

        "rule_based_severity": rule_severity,

        "ai_category": ai_result.get(
            "category",
            "Unknown"
        ),

        "ai_severity": ai_result.get(
            "severity",
            "Unknown"
        ),

        "ai_possible_cause": ai_result.get(
            "possible_cause",
            "Unknown"
        )
    }

    # -----------------------------
    # 10. Add report
    # -----------------------------

    reports.append(new_report)

    # -----------------------------
    # 11. Save JSON
    # -----------------------------

    with open(
        "processed_reports.json",
        "w"
    ) as file:

        json.dump(
            reports,
            file,
            indent=4
        )

    # -----------------------------
    # 12. Show result
    # -----------------------------

    messagebox.showinfo(
        "Report Saved",
        f"""
Report ID: {report_id}

Rule Severity: {rule_severity}

AI Category: {ai_result.get("category")}

AI Severity: {ai_result.get("severity")}

Possible Cause:
{ai_result.get("possible_cause")}
"""
    )

    # -----------------------------
    # 13. Clear form
    # -----------------------------

    machine_id_entry.delete(0, tk.END)

    problem_type_entry.delete(0, tk.END)

    problem_description_entry.delete(
        0,
        tk.END
    )

    downtime_entry.delete(0, tk.END)

    temperature_entry.delete(0, tk.END)

    pressure_entry.delete(0, tk.END)

    cycle_time_entry.delete(0, tk.END)

    operator_comment_entry.delete(
        0,
        tk.END
    )


# =====================================
# GUI
# =====================================

root = tk.Tk()
root.title("AI Production Issue Management System - Version 1.0")
root.geometry("550x650")

# Background image
image = Image.open("background.jpg")
image = image.resize((550, 650))

bg_image = ImageTk.PhotoImage(image)

background_label = tk.Label(root, image=bg_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


tk.Label(
    root,
    text="Production Issue Report",
    font=("Arial", 18, "bold")
).pack(pady=20)


tk.Label(
    root,
    text="Machine ID"
).pack()

machine_id_entry = tk.Entry(
    root,
    width=45
)

machine_id_entry.pack()


tk.Label(
    root,
    text="Problem Type"
).pack()

problem_type_entry = tk.Entry(
    root,
    width=45
)

problem_type_entry.pack()


tk.Label(
    root,
    text="Problem Description"
).pack()

problem_description_entry = tk.Entry(
    root,
    width=45
)

problem_description_entry.pack()


tk.Label(
    root,
    text="Downtime (minutes)"
).pack()

downtime_entry = tk.Entry(
    root,
    width=45
)

downtime_entry.pack()


tk.Label(
    root,
    text="Temperature (°C)"
).pack()

temperature_entry = tk.Entry(
    root,
    width=45
)

temperature_entry.pack()


tk.Label(
    root,
    text="Injection Pressure (bar)"
).pack()

pressure_entry = tk.Entry(
    root,
    width=45
)

pressure_entry.pack()


tk.Label(
    root,
    text="Cycle Time (seconds)"
).pack()

cycle_time_entry = tk.Entry(
    root,
    width=45
)

cycle_time_entry.pack()


tk.Label(
    root,
    text="Operator Comment"
).pack()

operator_comment_entry = tk.Entry(
    root,
    width=45
)

operator_comment_entry.pack()


tk.Button(
    root,
    text="Analyze & Submit Report",
    command=submit_report,
    width=25
).pack(pady=30)


root.mainloop()