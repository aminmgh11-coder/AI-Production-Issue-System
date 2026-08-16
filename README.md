# AI Production Issue Management System

## Version 1.0

An AI-assisted production issue analysis system for injection molding processes.

The project allows a machine operator to enter production and machine issue data through a graphical interface. The system validates the input, stores the report, calculates a rule-based severity level, and uses a local LLM to analyze the production issue.

---

## Current Features

- Operator input form using Tkinter
- Input validation
- Automatic Report ID generation
- Automatic timestamp
- JSON-based report storage
- Rule-based severity classification
- Local LLM integration using Ollama
- AI analysis of:
  - Problem Type
  - Problem Description
  - Downtime
  - Temperature
  - Injection Pressure
  - Cycle Time
  - Operator Comment
- AI-generated:
  - Issue Category
  - Severity
  - Possible Cause
- Local AI processing without external API costs

---

## Technology Stack

- Python
- Tkinter
- JSON
- Ollama
- Llama 3.2 3B
- Git
- GitHub

---

## System Workflow

Operator Input  
↓  
Input Validation  
↓  
Rule-Based Severity Analysis  
↓  
Local LLM Analysis  
↓  
AI Category / Severity / Possible Cause  
↓  
JSON Storage

---

## Example AI Output

```json
{
    "report_id": "RPT-0019",
    "machine_id": "IMM-05",
    "problem_type": "Abnormal Vibration",
    "downtime_minutes": 10,
    "temperature_c": 220,
    "injection_pressure_bar": 85,
    "cycle_time_seconds": 40,
    "rule_based_severity": "LOW",
    "ai_category": "Mechanical",
    "ai_severity": "MEDIUM",
    "ai_possible_cause": "Possible mold misalignment after mold change."
}