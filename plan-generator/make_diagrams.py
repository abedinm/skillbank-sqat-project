#!/usr/bin/env python3
"""
make_diagrams.py - the two drawings the template asks for.

The template says, under System Interface: "Draw the system interface where the users
will interact with the system's functionality." A table listing interfaces does not
answer that. This produces:

  fig_screen_flow.png   how a user moves between the ten interfaces, and where the
                        authorisation boundaries sit
  fig_architecture.png  the MVC request path, 5 controllers over 7 models over 7 tables

Both are drawn from the actual code in F:/outputs/aiub-webtech/skillbank.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = os.path.dirname(os.path.abspath(__file__))
INK, BLUE, GREEN, RED, PURPLE, GREY, LGREY = (
    "#1a202c", "#2b6cb0", "#2f855a", "#c53030", "#6b46c1", "#4a5568", "#edf2f7")


def box(ax, x, y, w, h, text, fc="white", ec=INK, fs=8.2, bold=False, lw=1.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.010,rounding_size=0.02",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=INK, zorder=3, fontweight="bold" if bold else "normal",
            linespacing=1.45)


def arrow(ax, p1, p2, color=GREY, lw=1.0, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=10,
                                 color=color, lw=lw, shrinkA=3, shrinkB=3, zorder=1,
                                 connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- screen flow
fig, ax = plt.subplots(figsize=(10.6, 5.4))
ax.set_xlim(0, 11.2); ax.set_ylim(0, 5.8); ax.axis("off")

box(ax, 0.15, 4.55, 1.75, 0.62, "Browse offers\n(public)", fc=LGREY)
box(ax, 0.15, 3.45, 1.75, 0.62, "Register", fc=LGREY)
box(ax, 0.15, 2.35, 1.75, 0.62, "Log in", fc=LGREY)

box(ax, 2.85, 3.45, 1.9, 0.72, "Member\ndashboard", fc="#e8f0fb", ec=BLUE, bold=True)

box(ax, 5.55, 4.75, 1.95, 0.62, "Offer detail", ec=BLUE)
box(ax, 5.55, 3.80, 1.95, 0.62, "Create / edit\noffer", ec=BLUE)
box(ax, 5.55, 2.85, 1.95, 0.62, "My sessions", ec=BLUE)
box(ax, 5.55, 1.90, 1.95, 0.62, "Wishlist", ec=BLUE)

box(ax, 8.55, 4.75, 2.3, 0.62, "Request a session", ec=GREEN)
box(ax, 8.55, 3.10, 2.3, 0.72, "Accept, complete\n(1 credit moves)", ec=GREEN, bold=True)
box(ax, 8.55, 2.05, 2.3, 0.62, "Leave a review", ec=GREEN)

box(ax, 2.85, 0.75, 1.9, 0.62, "Admin\ndashboard", fc="#fdecea", ec=RED, bold=True)
box(ax, 5.55, 0.75, 1.95, 0.62, "Manage skills", ec=RED)

for a, b in [((1.90, 3.76), (2.85, 3.81)), ((1.90, 2.66), (2.85, 3.60))]:
    arrow(ax, a, b, color=BLUE)
arrow(ax, (1.90, 4.86), (5.55, 5.06), color=GREY, rad=-0.12)
for y in (5.06, 4.11, 3.16, 2.21):
    arrow(ax, (4.75, 3.81), (5.55, y), color=BLUE, rad=0.05)
arrow(ax, (7.50, 5.06), (8.55, 5.06), color=GREEN)
arrow(ax, (7.50, 3.16), (8.55, 3.46), color=GREEN)
arrow(ax, (8.55, 3.10), (8.55, 2.67), color=GREEN, rad=0.0)
arrow(ax, (3.80, 3.45), (3.80, 1.37), color=RED, rad=0.0)
arrow(ax, (4.75, 1.06), (5.55, 1.06), color=RED)

ax.plot([2.55, 2.55], [0.45, 5.55], ls="--", lw=1.1, color=RED, zorder=0)
ax.text(2.60, 5.62, "authentication boundary", fontsize=7.8, color=RED, va="bottom")
ax.plot([2.60, 11.0], [1.62, 1.62], ls=":", lw=1.1, color=RED, zorder=0)
ax.text(10.95, 1.70, "administrator role required below", fontsize=7.8,
        color=RED, va="bottom", ha="right")

ax.text(5.6, 0.18, "Public screens are reachable without an account. Everything right of "
                   "the dashed line requires an authenticated session;\neverything below "
                   "the dotted line additionally requires the administrator role.",
        ha="center", fontsize=8.0, color=INK)
fig.tight_layout()
p1 = os.path.join(OUT, "fig_screen_flow.png")
fig.savefig(p1, dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- architecture
fig, ax = plt.subplots(figsize=(10.2, 4.3))
ax.set_xlim(0, 10.6); ax.set_ylim(0, 4.5); ax.axis("off")

box(ax, 0.15, 1.85, 1.5, 0.75, "Browser\n(any device)", fc=LGREY)
box(ax, 2.10, 1.85, 1.35, 0.75, "index.php\nfront controller", bold=True)

ctrls = ["Auth", "Offer", "Session", "Admin", "Dashboard"]
for i, c in enumerate(ctrls):
    box(ax, 3.95, 3.62 - i * 0.72, 1.65, 0.58, f"{c}Controller", ec=BLUE, fs=7.9)

models = ["User", "Skill", "Offer", "SessionModel", "Transaction", "Review", "Wish"]
for i, m in enumerate(models):
    box(ax, 6.15, 3.86 - i * 0.52, 1.75, 0.42, m, ec=GREEN, fs=7.6)

box(ax, 8.45, 1.55, 2.0, 1.35, "MySQL\n\n7 tables", fc="#eef6f0", ec=GREEN, bold=True)

arrow(ax, (1.65, 2.22), (2.10, 2.22))
for i in range(len(ctrls)):
    arrow(ax, (3.45, 2.22), (3.95, 3.91 - i * 0.72), color=BLUE, rad=0.08)
arrow(ax, (5.60, 2.20), (6.15, 2.20), color=GREEN)
arrow(ax, (7.90, 2.20), (8.45, 2.20), color=GREEN)

ax.text(4.78, 4.32, "Controllers", fontsize=8.4, ha="center", color=BLUE, fontweight="bold")
ax.text(7.02, 4.32, "Models", fontsize=8.4, ha="center", color=GREEN, fontweight="bold")
ax.text(5.3, 0.28, "Server-rendered PHP 8. No JavaScript framework, no build step, no "
                   "third-party service.\nEvery authorisation check runs in the controller, "
                   "on the request, not in the view.",
        ha="center", fontsize=8.0, color=INK)
fig.tight_layout()
p2 = os.path.join(OUT, "fig_architecture.png")
fig.savefig(p2, dpi=170, bbox_inches="tight"); plt.close(fig)

print("diagrams written:")
for p in (p1, p2):
    print(f"   {os.path.basename(p)}  ({os.path.getsize(p)/1024:.0f} KB)")
