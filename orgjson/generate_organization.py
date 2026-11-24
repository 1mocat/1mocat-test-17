#!/usr/bin/env python3
"""
JSON processor that transforms CSV data (departments, employees, projects)
into a structured organization.json following the schema in schema.json.
"""

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

def main():
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    output_path = base_dir / "organization.json"

    # Read departments
    departments = {}
    with open(data_dir / "departments.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            departments[row["id"]] = {
                "id": row["id"],
                "name": row["name"],
                "budget": float(row["budget"]),
                "employees": [],
                "projects": []
            }

    # Read employees
    all_employees = []
    skill_counts = defaultdict(int)
    years_list = []
    with open(data_dir / "employees.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            skills = [s.strip() for s in row["skills"].split(";") if s.strip()]
            emp = {
                "id": row["id"],
                "name": row["name"],
                "position": row["position"],
                "skills": skills,
                "years_of_service": int(row["years_of_service"])
            }
            dept_id = row["department_id"]
            if dept_id in departments:
                departments[dept_id]["employees"].append(emp)
            all_employees.append(emp)
            for skill in skills:
                skill_counts[skill] += 1
            years_list.append(emp["years_of_service"])

    # Read projects
    status_counts = defaultdict(int)
    with open(data_dir / "projects.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            members = [m.strip() for m in row["member_ids"].split(";") if m.strip()]
            proj = {
                "name": row["name"],
                "status": row["status"],
                "members": members,
                "deadline": row["deadline"]
            }
            dept_id = row["department_id"]
            if dept_id in departments:
                departments[dept_id]["projects"].append(proj)
            status_counts[row["status"]] += 1

    # Compute statistics
    budgets = [d["budget"] for d in departments.values()]
    avg_budget = sum(budgets) / len(budgets) if budgets else 0.0
    total_employees = len(all_employees)
    avg_years = sum(years_list) / len(years_list) if years_list else 0.0
    dept_sizes = {d["name"]: len(d["employees"]) for d in departments.values()}

    organization = {
        "metadata": {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generator": "csv-to-orgjson-processor"
        },
        "organization": {
            "name": "Elite Performance Technologies",
            "founded": "2010-03-15",
            "departments": list(departments.values())
        },
        "statistics": {
            "averageDepartmentBudget": round(avg_budget, 2),
            "totalEmployees": total_employees,
            "skillDistribution": dict(skill_counts),
            "departmentSizes": dept_sizes,
            "projectStatusDistribution": dict(status_counts),
            "averageYearsOfService": round(avg_years, 2)
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(organization, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()
