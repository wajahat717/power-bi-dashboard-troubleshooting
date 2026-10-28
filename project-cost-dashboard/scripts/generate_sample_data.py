"""Generate made-up sample data for the Project Cost dashboard.

The tables have the same shape as the Gold layer in the Fabric repo
(gold.dim_date, gold.dim_organization, gold.dim_expenditure_type,
gold.fact_project_cost) plus a small dim_project, so the dashboard can be
opened and explored without access to any real system.

Every name and number here is random. Run:  python generate_sample_data.py
"""
import csv
import os
import random
from datetime import date, timedelta

random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "..", "sample-data")
os.makedirs(OUT, exist_ok=True)

START, END = date(2025, 1, 1), date(2026, 9, 30)


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


# dim_date
dates = []
d = START
while d <= END:
    dates.append([int(d.strftime("%Y%m%d")), d.isoformat(), d.year, (d.month - 1) // 3 + 1,
                  d.month, d.strftime("%B"), d.strftime("%b-%y"), d.strftime("%Y-%m"),
                  1 if d.weekday() < 5 else 0])
    d += timedelta(days=1)
write("dim_date.csv", ["date_key", "calendar_date", "calendar_year", "calendar_quarter",
                       "month_number", "month_name", "period_name", "year_month",
                       "is_working_day"], dates)

# dim_organization
regions = {"North": ["Branch 101", "Branch 102", "Branch 103"],
           "South": ["Branch 201", "Branch 202", "Branch 203"],
           "East": ["Branch 301", "Branch 302", "Branch 303"],
           "West": ["Branch 401", "Branch 402", "Branch 403"]}
orgs, org_weight = [], {}
key = 1
for region, branches in regions.items():
    for b in branches:
        orgs.append([key, b, f"{b} Operations", f"{region} Region"])
        org_weight[key] = random.uniform(0.6, 1.6)
        key += 1
orgs.append([-1, "Unknown", "Unknown", "Unknown"])
write("dim_organization.csv", ["organization_key", "organization_name", "location_name",
                               "region_name"], orgs)

# dim_expenditure_type
types = [
    ("Labor", ["Field Technician", "Project Manager", "Engineer", "Overtime Labor"], 0.38),
    ("Disposal", ["Disposal Fee", "Landfill Fee", "Recycling Fee"], 0.17),
    ("Transportation", ["Freight", "Truck Hire", "Fuel Surcharge"], 0.14),
    ("Supplies", ["Safety Supplies", "Containers", "Labels and Forms"], 0.09),
    ("Equipment", ["Equipment Rental", "Vehicle Usage"], 0.08),
    ("Subcontractors", ["Subcontract Labor", "Specialist Services"], 0.08),
    ("Travel & Expenses", ["Airfare", "Hotel", "Meals"], 0.04),
    ("Overhead", ["Admin Overhead"], 0.02),
]
etypes, type_pool = [], []
key = 1
for cat, names, share in types:
    for n in names:
        etypes.append([key, n, cat])
        type_pool.append((key, cat, share / len(names)))
        key += 1
etypes.append([-1, "Unknown", "Unknown"])
write("dim_expenditure_type.csv", ["expenditure_type_key", "expenditure_type_name",
                                   "expenditure_category_name"], etypes)

# dim_project
industries = ["Manufacturing", "Healthcare", "Education", "Life Sciences", "Retail"]
projects = []
for i in range(60):
    pk = 5001 + i
    org = random.choice([o[0] for o in orgs if o[0] > 0])
    projects.append([pk, f"PRJ-{pk}", f"Client {chr(65 + i % 26)}{i // 26 + 1} - Site {random.randint(1, 9)}",
                     random.choice(industries), org,
                     random.choice(["Routine", "Routine", "Non-Routine"]),
                     round(random.uniform(0.4, 3.0), 2)])
write("dim_project.csv", ["project_key", "project_number", "project_name", "industry",
                          "owning_organization_key", "project_type", "size_factor"],
      [p[:6] for p in projects])

# fact_project_cost
weights = [t[2] for t in type_pool]
facts = []
item_id = 900000
working_days = [dt for dt in dates if dt[8] == 1]
for p in projects:
    pk, org, size = p[0], p[4], p[6]
    n_lines = int(260 * size)
    for _ in range(n_lines):
        tk, cat, _ = random.choices(type_pool, weights=weights)[0]
        dd = random.choice(working_days)
        month_idx = (dd[2] - 2025) * 12 + dd[4]
        trend = 1 + 0.012 * month_idx
        season = 1.15 if dd[4] in (3, 4, 9, 10) else 0.92 if dd[4] in (12, 1) else 1.0
        base = {"Labor": 820, "Disposal": 1450, "Transportation": 640, "Supplies": 210,
                "Equipment": 520, "Subcontractors": 2300, "Travel & Expenses": 380,
                "Overhead": 300}[cat]
        raw = round(base * random.lognormvariate(0, 0.55) * trend * season * org_weight[org], 2)
        burden = 1.32 if cat == "Labor" else 1.08
        billable = "N" if (cat == "Overhead" or random.random() < 0.07) else "Y"
        qty = round(raw / (base / 8) if cat == "Labor" else random.randint(1, 20), 2)
        item_id += 1
        facts.append([item_id, 1, dd[0], pk, org, tk, billable, qty, raw, round(raw * burden, 2)])
write("fact_project_cost.csv", ["expenditure_item_id", "line_num", "gl_date_key", "project_key",
                                "organization_key", "expenditure_type_key", "billable_flag",
                                "quantity", "raw_cost", "burdened_cost"], facts)
