import json

with open("machine_reports.json", "r") as file:
    reports = json.load(file)
new_report = {
    "machine_id": input("Machine ID: "),
    "problem_type": input("Problem Type: "),
    "problem_description": input("Problem Description: "),
    "downtime_minutes": int(input("Downtime (minutes): ")),
    "temperature_c": float(input("Temperature (°C): ")),
    "injection_pressure_bar": float(input("Injection Pressure (bar): ")),
    "cycle_time_seconds": float(input("Cycle Time (seconds): ")),
    "operator_comment": input("Operator Comment: ")
}

reports.append(new_report)
for report in reports:
    downtime = report["downtime_minutes"]

    if downtime > 25:
        severity = "HIGH"
    elif downtime > 15:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    print(
        f'{report["machine_id"]} | '
        f'{report["problem_type"]} | '
        f'Downtime: {downtime} min | '
        f'Severity: {severity}'
    )
    report["severity"] = severity
print(reports)
with open("processed_reports.json", "w") as file:
    json.dump(reports, file, indent=4)