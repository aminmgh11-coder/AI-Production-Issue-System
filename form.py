import json
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import ollama
from PIL import Image, ImageTk
import sqlite3


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

Validated process window for this evaluation:

- Temperature: 215–225 °C
- Injection Pressure: 75–85 bar
- Cycle Time: 38–44 seconds

Do not determine severity from a single process parameter alone.
Consider the complete production situation.the comments and all of the informations 

Use these ranges when interpreting whether the current process parameters
are normal, near a boundary, or outside the validated process window.

Analyze the complete production issue using both
process data and the operator comment.

recommended_action must be a short practical next step for the operator or maintenance technician.
confidence must indicate how strongly the provided data supports the diagnosis.

Use only:
LOW
MEDIUM
HIGH

HIGH = the process data and operator comment strongly support the diagnosis.
MEDIUM = the diagnosis is plausible but other causes are possible.
LOW = there is insufficient, vague, or conflicting information. 
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
confidence
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
def update_report_status():
    report_id = status_report_id_entry.get().strip()
    new_status = status_var.get()

    if not report_id:
        messagebox.showerror(
            "Invalid Input",
            "Report ID cannot be empty."
        )
        return

    connection = sqlite3.connect("production_reports.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE production_reports
        SET status = ?
        WHERE report_id = ?
    """, (new_status, report_id))

    connection.commit()

    if cursor.rowcount == 0:
        messagebox.showerror(
            "Not Found",
            f"Report {report_id} was not found."
        )
    else:
        messagebox.showinfo(
            "Status Updated",
            f"Report {report_id}\nStatus: {new_status}"
        )

    connection.close()
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
    severity_rank = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3
    }

    ai_severity = ai_result.get("severity", "LOW")

    if severity_rank[ai_severity] > severity_rank[rule_severity]:
        final_severity = ai_severity
    else:
        final_severity = rule_severity
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
        ),
        "recommended_action": ai_result.get(
            "recommended_action",
            "Unknown"
        ),
        "confidence": ai_result.get(
            "confidence",
            "Unknown"
        ),
        "final_severity": final_severity,
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

Recommended Action:
{ai_result.get("recommended_action")}

Final Severity:
{final_severity}

Confidence:
{ai_result.get("confidence", "Unknown")}
"""
    )
    connection = sqlite3.connect("production_reports.db")
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO production_reports (
        report_id,
        timestamp,
        machine_id,
        problem_type,
        problem_description,
        downtime_minutes,
        temperature_c,
        injection_pressure_bar,
        cycle_time_seconds,
        operator_comment,
        rule_based_severity,
        ai_category,
        ai_severity,
        ai_possible_cause,
        recommended_action,
        confidence,
        final_severity
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id,
        timestamp,
        machine_id,
        problem_type,
        problem_description,
        downtime,
        temperature,
        pressure,
        cycle_time,
        operator_comment,
        rule_severity,
        ai_result.get("category", "Unknown"),
        ai_result.get("severity", "Unknown"),
        ai_result.get("possible_cause", "Unknown"),
        ai_result.get("recommended_action", "Unknown"),
        ai_result.get("confidence", "Unknown"),
        final_severity
    ))

    connection.commit()
    print("Saved to SQL:", report_id)
    connection.close()
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
def view_reports():

    # =====================================
    # DATABASE
    # =====================================

    connection = sqlite3.connect("production_reports.db")
    cursor = connection.cursor()

    # Get machine IDs automatically from SQL
    cursor.execute("""
        SELECT DISTINCT machine_id
        FROM production_reports
        ORDER BY machine_id
    """)

    machine_ids = [
        row[0] for row in cursor.fetchall()
    ]

    connection.close()

    # =====================================
    # WINDOW
    # =====================================

    reports_window = tk.Toplevel(root)
    reports_window.title("Production Reports")
    reports_window.geometry("1000x600")
    reports_window.configure(bg="#111111")

    tk.Label(
        reports_window,
        text="PRODUCTION REPORTS",
        font=("Arial", 18, "bold"),
        fg="white",
        bg="#111111"
    ).pack(pady=(20, 5))

    tk.Label(
        reports_window,
        text="Search and filter stored production issues",
        font=("Arial", 9),
        fg="#AAAAAA",
        bg="#111111"
    ).pack(pady=(0, 15))

    # =====================================
    # FILTER FRAME
    # =====================================

    filter_frame = tk.LabelFrame(
        reports_window,
        text="  FILTER REPORTS  ",
        font=("Arial", 10, "bold"),
        fg="white",
        bg="#111111",
        padx=15,
        pady=10
    )

    filter_frame.pack(
        fill="x",
        padx=25,
        pady=(0, 15)
    )

    # -----------------------------
    # Machine filter
    # -----------------------------

    tk.Label(
        filter_frame,
        text="Machine",
        fg="white",
        bg="#111111"
    ).grid(
        row=0,
        column=0,
        padx=5,
        pady=5
    )

    machine_filter = tk.StringVar(value="ALL")

    machine_menu = ttk.Combobox(
        filter_frame,
        textvariable=machine_filter,
        values=["ALL"] + machine_ids,
        state="readonly",
        width=15
    )

    machine_menu.grid(
        row=0,
        column=1,
        padx=10
    )

    # -----------------------------
    # Severity filter
    # -----------------------------

    tk.Label(
        filter_frame,
        text="Severity",
        fg="white",
        bg="#111111"
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    severity_filter = tk.StringVar(value="ALL")

    severity_menu = ttk.Combobox(
        filter_frame,
        textvariable=severity_filter,
        values=[
            "ALL",
            "LOW",
            "MEDIUM",
            "HIGH"
        ],
        state="readonly",
        width=15
    )

    severity_menu.grid(
        row=0,
        column=3,
        padx=10
    )

    # -----------------------------
    # Status filter
    # -----------------------------

    tk.Label(
        filter_frame,
        text="Status",
        fg="white",
        bg="#111111"
    ).grid(
        row=0,
        column=4,
        padx=5
    )

    status_filter = tk.StringVar(value="ALL")

    status_menu_filter = ttk.Combobox(
        filter_frame,
        textvariable=status_filter,
        values=[
            "ALL",
            "OPEN",
            "IN PROGRESS",
            "RESOLVED"
        ],
        state="readonly",
        width=15
    )

    status_menu_filter.grid(
        row=0,
        column=5,
        padx=10
    )

    # =====================================
    # TABLE FRAME
    # =====================================

    table_frame = tk.Frame(
        reports_window,
        bg="#111111"
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 25)
    )

    columns = (
        "report_id",
        "machine_id",
        "problem_type",
        "severity",
        "status"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    tree.heading(
        "report_id",
        text="Report ID"
    )

    tree.heading(
        "machine_id",
        text="Machine"
    )

    tree.heading(
        "problem_type",
        text="Problem Type"
    )

    tree.heading(
        "severity",
        text="Severity"
    )

    tree.heading(
        "status",
        text="Status"
    )

    tree.column(
        "report_id",
        width=120,
        anchor="center"
    )

    tree.column(
        "machine_id",
        width=120,
        anchor="center"
    )

    tree.column(
        "problem_type",
        width=280,
        anchor="w"
    )

    tree.column(
        "severity",
        width=120,
        anchor="center"
    )

    tree.column(
        "status",
        width=150,
        anchor="center"
    )

    # =====================================
    # SCROLLBAR
    # =====================================

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    # =====================================
    # LOAD / FILTER DATA
    # =====================================

    def load_reports():

        connection = sqlite3.connect(
            "production_reports.db"
        )

        cursor = connection.cursor()

        query = """
            SELECT
                report_id,
                machine_id,
                problem_type,
                final_severity,
                status
            FROM production_reports
            WHERE 1=1
        """

        parameters = []

        # Machine
        if machine_filter.get() != "ALL":

            query += """
                AND machine_id = ?
            """

            parameters.append(
                machine_filter.get()
            )

        # Severity
        if severity_filter.get() != "ALL":

            query += """
                AND final_severity = ?
            """

            parameters.append(
                severity_filter.get()
            )

        # Status
        if status_filter.get() != "ALL":

            query += """
                AND status = ?
            """

            parameters.append(
                status_filter.get()
            )

        query += """
            ORDER BY report_id DESC
        """

        cursor.execute(
            query,
            parameters
        )

        reports = cursor.fetchall()

        connection.close()

        # Clear old table data
        for item in tree.get_children():
            tree.delete(item)

        # Insert filtered data
        for report in reports:

            tree.insert(
                "",
                tk.END,
                values=report
            )

    # =====================================
    # CLEAR FILTER
    # =====================================

    def clear_filters():

        machine_filter.set("ALL")
        severity_filter.set("ALL")
        status_filter.set("ALL")

        load_reports()

    # =====================================
    # FILTER BUTTONS
    # =====================================

    tk.Button(
        filter_frame,
        text="APPLY FILTER",
        command=load_reports,
        width=15,
        cursor="hand2"
    ).grid(
        row=1,
        column=2,
        columnspan=2,
        padx=5,
        pady=(12, 2)
    )

    tk.Button(
        filter_frame,
        text="CLEAR FILTER",
        command=clear_filters,
        width=15,
        cursor="hand2"
    ).grid(
        row=1,
        column=4,
        columnspan=2,
        padx=5,
        pady=(12, 2)
    )

    # Initial load
    load_reports()
def show_machine_analytics():
    connection = sqlite3.connect("production_reports.db")
    cursor = connection.cursor()
    # -----------------------------
    # KPI DATA
    # -----------------------------

    # Total Reports
    cursor.execute("""
        SELECT COUNT(*)
        FROM production_reports
    """)

    total_reports = cursor.fetchone()[0]

    # Open Issues
    cursor.execute("""
        SELECT COUNT(*)
        FROM production_reports
        WHERE status = 'OPEN'
    """)

    open_issues = cursor.fetchone()[0]

    # High Severity Issues
    cursor.execute("""
        SELECT COUNT(*)
        FROM production_reports
        WHERE final_severity = 'HIGH'
    """)

    high_issues = cursor.fetchone()[0]

    # Total Downtime
    cursor.execute("""
        SELECT COALESCE(SUM(downtime_minutes), 0)
        FROM production_reports
    """)

    total_downtime = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            machine_id,
            COUNT(*) AS issue_count,
            SUM(downtime_minutes) AS total_downtime,
            AVG(downtime_minutes) AS avg_downtime
        FROM production_reports
        GROUP BY machine_id
        ORDER BY issue_count DESC, total_downtime DESC
    """)

    machines = cursor.fetchall()
    connection.close()

    # -----------------------------
    # Window
    # -----------------------------

    analytics_window = tk.Toplevel(root)
    analytics_window.title("Machine Analytics")
    analytics_window.geometry("900x550")
    analytics_window.configure(bg="#111111")

    tk.Label(
        analytics_window,
        text="MACHINE ANALYTICS",
        font=("Arial", 18, "bold"),
        fg="white",
        bg="#111111"
    ).pack(pady=(20, 5))

    tk.Label(
        analytics_window,
        text="Production issue and downtime analysis by machine",
        font=("Arial", 9),
        fg="#AAAAAA",
        bg="#111111"
    ).pack(pady=(0, 15))
    # -----------------------------
    # KPI CARDS
    # -----------------------------

    kpi_frame = tk.Frame(
        analytics_window,
        bg="#111111"
    )

    kpi_frame.pack(
        fill="x",
        padx=25,
        pady=(0, 15)
    )

    # Total Reports
    tk.Label(
        kpi_frame,
        text=f"TOTAL REPORTS\n{total_reports}",
        font=("Arial", 11, "bold"),
        width=16,
        height=3,
        bg="#1c1c1c",
        fg="white"
    ).grid(row=0, column=0, padx=5)

    # Open Issues
    tk.Label(
        kpi_frame,
        text=f"OPEN ISSUES\n{open_issues}",
        font=("Arial", 11, "bold"),
        width=16,
        height=3,
        bg="#1c1c1c",
        fg="white"
    ).grid(row=0, column=1, padx=5)

    # High Severity
    tk.Label(
        kpi_frame,
        text=f"HIGH ISSUES\n{high_issues}",
        font=("Arial", 11, "bold"),
        width=16,
        height=3,
        bg="#1c1c1c",
        fg="white"
    ).grid(row=0, column=2, padx=5)

    # Total Downtime
    tk.Label(
        kpi_frame,
        text=f"TOTAL DOWNTIME\n{total_downtime} min",
        font=("Arial", 11, "bold"),
        width=16,
        height=3,
        bg="#1c1c1c",
        fg="white"
    ).grid(row=0, column=3, padx=5)

    # -----------------------------
    # Table container
    # -----------------------------

    table_frame = tk.Frame(
        analytics_window,
        bg="#111111"
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 25)
    )

    # -----------------------------
    # Treeview
    # -----------------------------

    columns = (
        "machine_id",
        "issue_count",
        "total_downtime",
        "avg_downtime"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    tree.heading(
        "machine_id",
        text="Machine"
    )

    tree.heading(
        "issue_count",
        text="Issues"
    )

    tree.heading(
        "total_downtime",
        text="Total Downtime (min)"
    )

    tree.heading(
        "avg_downtime",
        text="Avg Downtime (min)"
    )

    tree.column(
        "machine_id",
        width=150,
        anchor="center"
    )

    tree.column(
        "issue_count",
        width=120,
        anchor="center"
    )

    tree.column(
        "total_downtime",
        width=180,
        anchor="center"
    )

    tree.column(
        "avg_downtime",
        width=180,
        anchor="center"
    )

    # -----------------------------
    # Scrollbar
    # -----------------------------

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    # -----------------------------
    # Insert SQL data
    # -----------------------------

    for machine in machines:

        machine_id = machine[0]
        issue_count = machine[1]
        total_downtime = machine[2]
        avg_downtime = machine[3]

        tree.insert(
            "",
            tk.END,
            values=(
                machine_id,
                issue_count,
                total_downtime,
                f"{avg_downtime:.1f}"
            )
        )
# =====================================
# MODERN GUI - VERSION 2.0
# =====================================

root = tk.Tk()
root.title("AI Production Issue Management System - Version 2.0")
root.geometry("900x760")
root.resizable(False, False)

# -----------------------------
# Background
# -----------------------------

image = Image.open("background_v2.png")
image = image.resize((900, 760))
bg_image = ImageTk.PhotoImage(image)

background_label = tk.Label(
    root,
    image=bg_image
)
background_label.place(
    x=0,
    y=0,
    relwidth=1,
    relheight=1
)

# -----------------------------
# Main container
# -----------------------------

main_frame = tk.Frame(
    root,
    bg="#111111",
    bd=1,
    relief="solid"
)

main_frame.place(
    relx=0.5,
    rely=0.5,
    anchor="center",
    width=700,
    height=700
)

# -----------------------------
# Header
# -----------------------------

tk.Label(
    main_frame,
    text="AI PRODUCTION ISSUE MANAGEMENT SYSTEM",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#111111"
).pack(pady=(15, 2))

tk.Label(
    main_frame,
    text="Industrial Monitoring & AI Analysis  •  V2.0",
    font=("Arial", 10),
    fg="#AAAAAA",
    bg="#111111"
).pack(pady=(0, 12))


# =====================================
# REPORT INFORMATION
# =====================================

report_frame = tk.LabelFrame(
    main_frame,
    text="  REPORT INFORMATION  ",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#111111",
    padx=15,
    pady=10
)

report_frame.pack(
    fill="x",
    padx=25,
    pady=5
)

tk.Label(
    report_frame,
    text="Machine ID",
    fg="white",
    bg="#111111"
).grid(row=0, column=0, sticky="w", padx=5, pady=5)

machine_id_entry = tk.Entry(
    report_frame,
    width=30
)
machine_id_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=5
)

tk.Label(
    report_frame,
    text="Problem Type",
    fg="white",
    bg="#111111"
).grid(row=1, column=0, sticky="w", padx=5, pady=5)

problem_type_entry = tk.Entry(
    report_frame,
    width=30
)
problem_type_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=5
)

tk.Label(
    report_frame,
    text="Problem Description",
    fg="white",
    bg="#111111"
).grid(row=2, column=0, sticky="w", padx=5, pady=5)

problem_description_entry = tk.Entry(
    report_frame,
    width=55
)
problem_description_entry.grid(
    row=2,
    column=1,
    columnspan=3,
    padx=10,
    pady=5
)


# =====================================
# PROCESS PARAMETERS
# =====================================

process_frame = tk.LabelFrame(
    main_frame,
    text="  PROCESS PARAMETERS  ",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#111111",
    padx=15,
    pady=10
)

process_frame.pack(
    fill="x",
    padx=25,
    pady=5
)

tk.Label(
    process_frame,
    text="Downtime (min)",
    fg="white",
    bg="#111111"
).grid(row=0, column=0, sticky="w", padx=5, pady=5)

downtime_entry = tk.Entry(
    process_frame,
    width=15
)
downtime_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(
    process_frame,
    text="Temperature (°C)",
    fg="white",
    bg="#111111"
).grid(row=0, column=2, sticky="w", padx=20, pady=5)

temperature_entry = tk.Entry(
    process_frame,
    width=15
)
temperature_entry.grid(row=0, column=3, padx=10, pady=5)

tk.Label(
    process_frame,
    text="Pressure (bar)",
    fg="white",
    bg="#111111"
).grid(row=1, column=0, sticky="w", padx=5, pady=5)

pressure_entry = tk.Entry(
    process_frame,
    width=15
)
pressure_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(
    process_frame,
    text="Cycle Time (sec)",
    fg="white",
    bg="#111111"
).grid(row=1, column=2, sticky="w", padx=20, pady=5)

cycle_time_entry = tk.Entry(
    process_frame,
    width=15
)
cycle_time_entry.grid(row=1, column=3, padx=10, pady=5)


# =====================================
# OPERATOR COMMENT
# =====================================

comment_frame = tk.LabelFrame(
    main_frame,
    text="  OPERATOR COMMENT  ",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#111111",
    padx=15,
    pady=10
)

comment_frame.pack(
    fill="x",
    padx=25,
    pady=5
)

operator_comment_entry = tk.Entry(
    comment_frame,
    width=80
)

operator_comment_entry.pack(
    padx=5,
    pady=5
)


# =====================================
# SUBMIT BUTTON
# =====================================

tk.Button(
    main_frame,
    text="ANALYZE & SUBMIT REPORT",
    command=submit_report,
    width=30,
    height=2,
    font=("Arial", 10, "bold"),
    cursor="hand2"
).pack(pady=12)


# =====================================
# ISSUE MANAGEMENT
# =====================================

status_frame = tk.LabelFrame(
    main_frame,
    text="  ISSUE MANAGEMENT  ",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#111111",
    padx=15,
    pady=10
)

status_frame.pack(
    fill="x",
    padx=25,
    pady=5
)

tk.Label(
    status_frame,
    text="Report ID",
    fg="white",
    bg="#111111"
).grid(row=0, column=0, padx=5)

status_report_id_entry = tk.Entry(
    status_frame,
    width=20
)
status_report_id_entry.grid(
    row=0,
    column=1,
    padx=10
)

tk.Label(
    status_frame,
    text="Status",
    fg="white",
    bg="#111111"
).grid(row=0, column=2, padx=10)

status_var = tk.StringVar(value="OPEN")

status_menu = tk.OptionMenu(
    status_frame,
    status_var,
    "OPEN",
    "IN PROGRESS",
    "RESOLVED"
)
status_menu.config(width=15)

status_menu.grid(
    row=0,
    column=3,
    padx=10
)

tk.Button(
    status_frame,
    text="UPDATE STATUS",
    command=update_report_status,
    cursor="hand2"
).grid(
    row=0,
    column=4,
    padx=10
)


# =====================================
# MANAGEMENT BUTTONS
# =====================================

management_frame = tk.Frame(
    main_frame,
    bg="#111111"
)

management_frame.pack(
    pady=15
)

tk.Button(
    management_frame,
    text="VIEW REPORTS",
    command=view_reports,
    width=20,
    cursor="hand2"
).grid(
    row=0,
    column=0,
    padx=10
)

tk.Button(
    management_frame,
    text="MACHINE ANALYTICS",
    command=show_machine_analytics,
    width=20,
    cursor="hand2"
).grid(
    row=0,
    column=1,
    padx=10
)


# =====================================
# FOOTER
# =====================================

tk.Label(
    main_frame,
    text="AI-assisted industrial issue analysis • Local LLM • SQLite",
    font=("Arial", 8),
    fg="#777777",
    bg="#111111"
).pack(pady=(5, 10))


root.mainloop()