# AI Production Issue Management System

An AI-assisted production issue management and analysis system designed for injection molding processes.

The system allows machine operators to report production issues through a graphical interface. It validates process data, performs rule-based severity analysis, uses a local LLM for AI-assisted diagnosis, stores reports in a SQL database, and provides tools for issue management and production analytics.

---

## Version 2.0

Version 2 expands the original AI issue analyzer into a production issue management and analytics system.

### New in Version 2

- SQLite database integration
- SQL-based report storage
- Issue status management
  - OPEN
  - IN PROGRESS
  - RESOLVED
- Update existing report status
- Production Reports viewer
- Search and filter reports by:
  - Machine
  - Severity
  - Status
- Machine Analytics
- KPI Dashboard
- Total issue count by machine
- Total downtime by machine
- Average downtime by machine
- High-severity issue analysis
- Improved AI diagnosis
- AI-generated recommended action
- AI confidence level
- Final severity calculation combining rule-based and AI severity
- Redesigned Version 2 graphical interface

---

## AI Analysis

The local AI analyzes:

- Problem Type
- Problem Description
- Downtime
- Temperature
- Injection Pressure
- Cycle Time
- Operator Comment

The AI returns structured information including:

```json
{
    "category": "Mechanical",
    "severity": "HIGH",
    "possible_cause": "Possible mold misalignment",
    "recommended_action": "Inspect and realign the mold before restarting production.",
    "confidence": "HIGH"
}
```

The system then combines the AI severity with the rule-based severity to determine the final severity.

---

## Database & Analytics

Production reports are stored in a SQLite database.

The system uses SQL for operations such as:

- INSERT new production reports
- SELECT stored reports
- UPDATE issue status
- Filter reports
- Group issues by machine
- Calculate issue counts
- Calculate total downtime
- Calculate average downtime
- Identify machines with recurring issues

Example analytics query:

```sql
SELECT
    machine_id,
    COUNT(*) AS issue_count,
    SUM(downtime_minutes) AS total_downtime,
    AVG(downtime_minutes) AS avg_downtime
FROM production_reports
GROUP BY machine_id
ORDER BY issue_count DESC, total_downtime DESC;
```

---

## System Workflow

```text
Operator Input
      ↓
Input Validation
      ↓
Rule-Based Severity Analysis
      ↓
Local LLM Analysis
      ↓
AI Diagnosis + Recommended Action + Confidence
      ↓
Final Severity
      ↓
JSON + SQLite Storage
      ↓
Issue Management
      ↓
Search / Filter / Analytics
```

---

## Technology Stack

- Python
- Tkinter
- SQLite
- SQL
- JSON
- Ollama
- Llama 3.2 3B
- Pillow
- Git
- GitHub

---

## Version History

### V1.0 — AI Issue Analyzer

Initial version of the system.

Main features:

- Tkinter operator input form
- Input validation
- Automatic Report ID generation
- Automatic timestamp
- JSON report storage
- Rule-based severity classification
- Local LLM integration with Ollama
- AI-generated issue category
- AI-generated severity
- AI-generated possible cause

### V2.0 — Issue Management & Production Analytics

Expanded the system with:

- SQLite database
- SQL analytics
- Issue status management
- Report viewer
- Search and filtering
- Machine analytics
- KPI dashboard
- AI confidence
- Recommended actions
- Final severity calculation
- Redesigned graphical interface

---

## Privacy & Local AI

The AI model runs locally using Ollama.

Production data can therefore be analyzed locally without requiring an external AI API.

---

## Project Status

**Current stable version: V2.0**

Development will continue in future versions with additional production intelligence and AI capabilities.