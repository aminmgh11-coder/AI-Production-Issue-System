import sqlite3

connection = sqlite3.connect("production_reports.db")
cursor = connection.cursor()

cursor.execute("""
SELECT report_id, machine_id, problem_type, final_severity
FROM production_reports
WHERE final_severity = 'HIGH'
""")

reports = cursor.fetchall()

for report in reports:
    print(report)

connection.close()