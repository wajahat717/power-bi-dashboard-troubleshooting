"""Render preview images of the two dashboard pages from the sample data.
These PNGs show the layout and numbers the Power BI report produces.
Run after generate_sample_data.py:  python render_dashboard_preview.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter, MaxNLocator

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "sample-data")
OUT = os.path.join(HERE, "..", "screenshots")
os.makedirs(OUT, exist_ok=True)

SURFACE, CANVAS = "#fcfcfb", "#f1f0ec"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3de"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
HEADER = "#1f3b57"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "text.color": INK,
                     "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})

f = pd.read_csv(os.path.join(DATA, "fact_project_cost.csv"))
dd = pd.read_csv(os.path.join(DATA, "dim_date.csv"))
org = pd.read_csv(os.path.join(DATA, "dim_organization.csv"))
et = pd.read_csv(os.path.join(DATA, "dim_expenditure_type.csv"))
pr = pd.read_csv(os.path.join(DATA, "dim_project.csv"))
f = (f.merge(dd, left_on="gl_date_key", right_on="date_key")
      .merge(org, on="organization_key")
      .merge(et, on="expenditure_type_key")
      .merge(pr, on="project_key"))

money = lambda v: f"${v/1e6:.2f}M" if abs(v) >= 1e6 else f"${v/1e3:.0f}K"
axfmt = FuncFormatter(lambda v, _: f"${v/1e6:.1f}M" if v >= 1e6 else f"${v/1e3:.0f}K")


def panel(fig, x, y, w, h, title=None):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.006",
                                      transform=fig.transFigure, facecolor=SURFACE,
                                      edgecolor=GRID, linewidth=0.8, zorder=-5))
    if title:
        fig.text(x + 0.012, y + h - 0.035, title, fontsize=10.5, fontweight="bold", color=INK)


def frame(title, subtitle):
    fig = plt.figure(figsize=(16, 9), dpi=110, facecolor=CANVAS)
    fig.patches.append(plt.Rectangle((0, 0.93), 1, 0.07, transform=fig.transFigure,
                                     facecolor=HEADER, zorder=-5))
    fig.text(0.015, 0.958, title, fontsize=17, fontweight="bold", color="white", va="center")
    fig.text(0.985, 0.958, subtitle, fontsize=10, color="#d6dde5", va="center", ha="right")
    slicers = [("Year", "2025, 2026"), ("Region", "All"), ("Category", "All"), ("Billable", "All")]
    for i, (k, v) in enumerate(slicers):
        x = 0.015 + i * 0.12
        panel(fig, x, 0.865, 0.11, 0.05)
        fig.text(x + 0.008, 0.897, k, fontsize=8, color=MUTED)
        fig.text(x + 0.008, 0.874, v + "  ▾", fontsize=9.5, color=INK)
    return fig


def style(ax, xgrid=False):
    ax.set_facecolor(SURFACE)
    (ax.xaxis if xgrid else ax.yaxis).set_major_locator(MaxNLocator(4))
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.grid(axis="x" if xgrid else "y", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def kpis(fig, items):
    w = 0.235
    for i, (label, value, note, good) in enumerate(items):
        x = 0.015 + i * (w + 0.0083)
        panel(fig, x, 0.725, w, 0.125)
        fig.text(x + 0.012, 0.818, label, fontsize=9.5, color=INK2)
        fig.text(x + 0.012, 0.763, value, fontsize=24, fontweight="bold", color=INK)
        if note:
            fig.text(x + 0.012, 0.738, note, fontsize=8.5, color=INK2)


# ---------------- Page 1: Overview ----------------
last = f["year_month"].max()
months = sorted(f["year_month"].unique())
prev = months[-2]
cur_cost = f.loc[f.year_month == last, "burdened_cost"].sum()
prev_cost = f.loc[f.year_month == prev, "burdened_cost"].sum()
mom = (cur_cost - prev_cost) / prev_cost
total = f["burdened_cost"].sum()
billable = f.loc[f.billable_flag == "Y", "burdened_cost"].sum() / total
burden = (f["burdened_cost"].sum() - f["raw_cost"].sum()) / f["raw_cost"].sum()

fig = frame("Project Cost Overview", f"Sample data · Jan 2025 – Sep 2026 · Data as of 30 Sep 2026")
kpis(fig, [
    ("Total burdened cost", money(total), f"Raw cost {money(f['raw_cost'].sum())}", True),
    (f"Cost this month ({pd.Period(last).strftime('%b %Y')})", money(cur_cost),
     f"{'▲' if mom >= 0 else '▼'} {abs(mom):.1%} vs last month", mom < 0),
    ("Billable %", f"{billable:.1%}", f"Non-billable {money(total * (1 - billable))}", True),
    ("Active projects", f"{f['project_key'].nunique()}", f"Burden rate {burden:.1%} on raw cost", True),
])

# trend
panel(fig, 0.015, 0.385, 0.595, 0.325, "Burdened cost by month")
ax = fig.add_axes([0.055, 0.425, 0.54, 0.235])
m = f.groupby("year_month")["burdened_cost"].sum()
xs = range(len(m))
ax.plot(xs, m.values, color=BLUE, linewidth=2)
ax.scatter([len(m) - 1], [m.values[-1]], s=40, color=BLUE, zorder=3, edgecolor=SURFACE, linewidth=2)
ax.annotate(money(m.values[-1]), (len(m) - 1, m.values[-1]), xytext=(-6, 10),
            textcoords="offset points", ha="right", fontsize=9, color=INK)
ax.set_xticks(list(xs)[::2])
ax.set_xticklabels([pd.Period(p).strftime("%b %y") for p in m.index][::2], fontsize=8)
ax.yaxis.set_major_formatter(axfmt)
ax.set_ylim(0, m.max() * 1.2)
style(ax)

# category
panel(fig, 0.618, 0.385, 0.367, 0.325, "Cost by expenditure category")
ax = fig.add_axes([0.715, 0.41, 0.25, 0.25])
c = f.groupby("expenditure_category_name")["burdened_cost"].sum().sort_values()
ax.barh(c.index, c.values, color=BLUE, height=0.62)
for i, v in enumerate(c.values):
    ax.text(v + c.max() * 0.01, i, money(v), va="center", fontsize=8, color=INK2)
ax.xaxis.set_major_formatter(axfmt)
ax.set_xlim(0, c.max() * 1.22)
style(ax, xgrid=True)

# region
panel(fig, 0.015, 0.03, 0.29, 0.34, "Cost by region")
ax = fig.add_axes([0.075, 0.065, 0.215, 0.24])
r = f.groupby("region_name")["burdened_cost"].sum().sort_values()
ax.barh(r.index, r.values, color=BLUE, height=0.55)
for i, v in enumerate(r.values):
    ax.text(v + r.max() * 0.01, i, f"{money(v)}  ({v/total:.0%})", va="center", fontsize=8, color=INK2)
ax.xaxis.set_major_formatter(axfmt)
ax.set_xlim(0, r.max() * 1.45)
style(ax, xgrid=True)

# top projects
panel(fig, 0.313, 0.03, 0.672, 0.34, "Top 10 projects by burdened cost")
ax = fig.add_axes([0.47, 0.055, 0.49, 0.255])
t = f.groupby(["project_number", "project_name"])["burdened_cost"].sum().nlargest(10).iloc[::-1]
labels = [f"{a}  {b}" for a, b in t.index]
ax.barh(labels, t.values, color=BLUE, height=0.62)
for i, v in enumerate(t.values):
    ax.text(v + t.max() * 0.01, i, money(v), va="center", fontsize=8, color=INK2)
ax.xaxis.set_major_formatter(axfmt)
ax.set_xlim(0, t.max() * 1.15)
ax.tick_params(axis="y", labelsize=8)
style(ax, xgrid=True)
fig.savefig(os.path.join(OUT, "page1_overview.png"), facecolor=CANVAS)
plt.close(fig)

# ---------------- Page 2: Project detail ----------------
fig = frame("Project Detail", "Sample data · click a project to filter every visual on the page")
panel(fig, 0.015, 0.385, 0.97, 0.465, "Billable vs non-billable cost by month")
ax = fig.add_axes([0.055, 0.425, 0.91, 0.36])
bm = f.pivot_table(index="year_month", columns="billable_flag", values="burdened_cost",
                   aggfunc="sum").fillna(0)
xs = range(len(bm))
ax.bar(xs, bm["Y"], color=BLUE, width=0.62, label="Billable")
ax.bar(xs, bm["N"], bottom=bm["Y"], color=ORANGE, width=0.62, label="Non-billable",
       edgecolor=SURFACE, linewidth=2)
ax.set_xticks(list(xs))
ax.set_xticklabels([pd.Period(p).strftime("%b %y") for p in bm.index], fontsize=8)
ax.yaxis.set_major_formatter(axfmt)
ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1, 1.02), ncol=2, fontsize=9)
ax.set_ylim(0, (bm["Y"] + bm["N"]).max() * 1.18)
style(ax)

panel(fig, 0.015, 0.03, 0.97, 0.34, "Project table (top 8 by cost)")
g = (f.groupby(["project_number", "project_name", "region_name", "industry"])
       .agg(cost=("burdened_cost", "sum"), raw=("raw_cost", "sum"),
            bill=("burdened_cost", lambda s: s[f.loc[s.index, "billable_flag"] == "Y"].sum()))
       .reset_index().nlargest(8, "cost"))
last_m = f[f.year_month == last].groupby("project_number")["burdened_cost"].sum()
prev_m = f[f.year_month == prev].groupby("project_number")["burdened_cost"].sum()
cols = ["Project", "Name", "Region", "Industry", "Burdened cost", "Raw cost", "Billable %", "MoM %"]
xpos = [0.03, 0.12, 0.33, 0.45, 0.58, 0.69, 0.79, 0.88]
y0 = 0.31
for x, cname in zip(xpos, cols):
    fig.text(x, y0, cname, fontsize=9, fontweight="bold", color=INK2)
fig.lines.append(plt.Line2D([0.025, 0.975], [y0 - 0.012, y0 - 0.012], transform=fig.transFigure,
                            color=GRID, linewidth=1))
for i, row in enumerate(g.itertuples()):
    y = y0 - 0.034 - i * 0.031
    lm, pm = last_m.get(row.project_number, 0), prev_m.get(row.project_number, 0)
    momp = (lm - pm) / pm if pm else 0
    vals = [row.project_number, row.project_name, row.region_name, row.industry,
            money(row.cost), money(row.raw), f"{row.bill/row.cost:.1%}",
            f"{'▲' if momp >= 0 else '▼'} {abs(momp):.1%}"]
    for x, v in zip(xpos, vals):
        fig.text(x, y, v, fontsize=9, color=INK)
fig.savefig(os.path.join(OUT, "page2_project_detail.png"), facecolor=CANVAS)
plt.close(fig)
print("saved", os.listdir(OUT))
