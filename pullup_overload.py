#!/usr/bin/env python3
"""
Pull-Up Progressive Overload Calculator
========================================
Agent-operated: Claude runs this script with CLI args, not the user.

Program design based on:
- Renaissance Periodization (RP) mesocycle structure
- r/bodyweightfitness Recommended Routine progression
- StrongFirst triple progression method

Bodyweight-only pull-ups, 3x/week:
  - 3 sets, 5-8 rep range, 2-3 min rest
  - Add 1 total rep per session (to one set, not all)
  - When all sets hit top of range (8), add a set (up to 5)
  - When 5x8 is hit, suggest harder variation or adding weight
  - Deload every 5 weeks: half volume, easy effort
  - Volume = bodyweight_lbs × total_reps

Data stored in pullup_log.csv
"""

import csv
import os
import sys
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pullup_log.csv")
CSV_FIELDS = [
    "date", "week", "bodyweight_lbs",
    "set1", "set2", "set3", "set4", "set5",
    "total_reps", "volume_lbs", "notes",
]

# Program constants
START_SETS = 4
MAX_SETS = 5  # max columns in CSV
REST_SECONDS = 150  # 2.5 min
DELOAD_EVERY_WEEKS = 5
SESSIONS_PER_WEEK = 3
VOLUME_INCREMENT_PCT = 0.015  # 1.5% volume increase per session


def load_sessions():
    sessions = []
    if not os.path.exists(DATA_FILE):
        return sessions
    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reps = []
            for i in range(1, MAX_SETS + 1):
                val = row.get(f"set{i}", "")
                if val:
                    reps.append(int(val))
            sessions.append({
                "date": row["date"],
                "week": int(row["week"]),
                "bodyweight_lbs": float(row["bodyweight_lbs"]),
                "reps_per_set": reps,
                "total_reps": int(row["total_reps"]),
                "volume_lbs": float(row["volume_lbs"]),
                "notes": row.get("notes", ""),
            })
    return sessions


def save_session(session):
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        row = {
            "date": session["date"],
            "week": session["week"],
            "bodyweight_lbs": session["bodyweight_lbs"],
            "total_reps": session["total_reps"],
            "volume_lbs": session["volume_lbs"],
            "notes": session.get("notes", ""),
        }
        for i, reps in enumerate(session["reps_per_set"], 1):
            row[f"set{i}"] = reps
        writer.writerow(row)


def get_current_week(sessions):
    if not sessions:
        return 1
    return sessions[-1]["week"]


def determine_week(sessions):
    """Figure out which week we're in based on sessions logged."""
    if not sessions:
        return 1
    current_week = sessions[-1]["week"]
    week_sessions = [s for s in sessions if s["week"] == current_week]
    if len(week_sessions) >= SESSIONS_PER_WEEK:
        return current_week + 1
    return current_week


def is_deload_week(week_num):
    return week_num > 1 and (week_num - 1) % DELOAD_EVERY_WEEKS == 0


def add_one_rep(reps):
    """Add 1 rep to the lowest set (distribute evenly). Returns new list."""
    result = list(reps)
    min_idx = result.index(min(result))
    result[min_idx] += 1
    return result


def calculate_workout(sessions, bodyweight):
    """Calculate today's prescription."""
    current_week = determine_week(sessions)
    deload = is_deload_week(current_week)
    last = sessions[-1] if sessions else None

    result = {
        "week": current_week,
        "rest": REST_SECONDS,
        "deload": deload,
    }

    if deload:
        last_reps = last["reps_per_set"] if last else [5] * START_SETS
        num_sets = max(2, len(last_reps) // 2)
        deload_reps = [max(3, r // 2) for r in last_reps[:num_sets]]
        result.update({
            "sets": num_sets,
            "rep_targets": deload_reps,
            "note": "DELOAD WEEK: half volume, stay 4+ reps from failure. Recovery week!",
        })
        return result

    if last is None:
        # First ever session: baseline test
        result.update({
            "sets": START_SETS,
            "rep_targets": None,
            "note": "FIRST SESSION: Do max clean reps each set, stop 1-2 before failure. Full ROM!",
        })
        return result

    # --- Progression logic: constant work increase each session ---
    last_reps = last["reps_per_set"]
    num_sets = len(last_reps)
    last_volume = last["volume_lbs"]
    last_bw = last["bodyweight_lbs"]

    # Target: add 1.5% of last session's volume
    target_volume = last_volume * (1 + VOLUME_INCREMENT_PCT)
    target_total_reps = round(target_volume / bodyweight)
    last_total = sum(last_reps)
    reps_diff = target_total_reps - last_total

    # Distribute reps across sets, starting from last session's distribution
    rep_targets = list(last_reps)
    remaining = target_total_reps - sum(rep_targets)
    while remaining > 0:
        min_idx = rep_targets.index(min(rep_targets))
        rep_targets[min_idx] += 1
        remaining -= 1
    while remaining < 0:
        max_idx = rep_targets.index(max(rep_targets))
        rep_targets[max_idx] = max(1, rep_targets[max_idx] - 1)
        remaining += 1

    actual_volume = bodyweight * target_total_reps
    vol_increase = actual_volume - last_volume
    pct = (vol_increase / last_volume) * 100
    note = f"Work: {actual_volume:.0f} lbs (+{vol_increase:.0f}, {pct:.1f}%)."
    if bodyweight != last_bw:
        note += f" BW {bodyweight:.0f} vs {last_bw:.0f}."

    # RIR guidance based on position in mesocycle
    block_week = ((current_week - 1) % DELOAD_EVERY_WEEKS) + 1
    if block_week <= 2:
        rir = "3 RIR (early in block)"
    elif block_week <= 3:
        rir = "2 RIR (mid block)"
    else:
        rir = "0-1 RIR (end of block — push it)"

    result.update({
        "sets": num_sets,
        "rep_targets": rep_targets,
        "note": note,
        "rir": rir,
    })
    return result


def format_workout(workout, bodyweight, date_str=None):
    """Return a formatted string of the workout prescription."""
    lines = []
    lines.append("=" * 55)
    header = f"  PULL-UP WORKOUT — Week {workout['week']}"
    if date_str:
        header += f"  ({date_str})"
    lines.append(header)
    if workout["deload"]:
        lines.append("  *** DELOAD WEEK ***")
    lines.append("=" * 55)
    lines.append(f"  Bodyweight: {bodyweight} lbs")
    lines.append(f"  Rest: {workout['rest']}s between sets")
    if "rir" in workout:
        lines.append(f"  Effort: {workout['rir']}")
    lines.append("")

    if workout["rep_targets"] is None:
        lines.append(f"  Sets: {workout['sets']}")
        lines.append(f"  Reps: MAX (clean reps, stop 1-2 before failure)")
    else:
        for i, reps in enumerate(workout["rep_targets"], 1):
            lines.append(f"  Set {i}:  aim for {reps} reps")
        total_reps = sum(workout["rep_targets"])
        vol = bodyweight * total_reps
        lines.append(f"  Total: {total_reps} reps | Volume: {vol:.0f} lbs")

    lines.append(f"\n  >> {workout['note']}")
    lines.append("=" * 55)
    return "\n".join(lines)


def format_log_entry(session):
    """Return formatted string of a logged session."""
    lines = []
    reps_str = " / ".join(str(r) for r in session["reps_per_set"])
    lines.append(f"  Date: {session['date']}")
    lines.append(f"  Week {session['week']}")
    lines.append(f"  BW: {session['bodyweight_lbs']} lbs")
    lines.append(f"  Reps: [{reps_str}] = {session['total_reps']} total")
    lines.append(f"  Volume: {session['volume_lbs']:.0f} lbs")
    if session.get("notes"):
        lines.append(f"  Notes: {session['notes']}")
    return "\n".join(lines)


def format_history(sessions, last_n=10):
    """Return formatted history of recent sessions."""
    if not sessions:
        return "  No sessions logged yet."
    lines = ["--- HISTORY (last {}) ---".format(min(last_n, len(sessions)))]
    for s in sessions[-last_n:]:
        reps_str = "/".join(str(r) for r in s["reps_per_set"])
        lines.append(
            f"  {s['date']}  W{s['week']}  "
            f"{s['bodyweight_lbs']}lb  [{reps_str}]  "
            f"vol:{s['volume_lbs']:.0f}lb"
        )

    if sessions:
        current_week = sessions[-1]["week"]
        week_sessions = [s for s in sessions if s["week"] == current_week]
        week_sets = sum(len(s["reps_per_set"]) for s in week_sessions)
        week_vol = sum(s["volume_lbs"] for s in week_sessions)
        lines.append(f"\n  This week (W{current_week}): {len(week_sessions)}/{SESSIONS_PER_WEEK} sessions, "
                      f"{week_sets} sets, {week_vol:.0f} lbs volume")
    return "\n".join(lines)


def parse_args(args):
    """Extract --date and --notes from args. Returns (remaining_args, date_str, notes)."""
    remaining = []
    date_str = datetime.now().strftime("%Y-%m-%d")
    notes = ""
    i = 0
    while i < len(args):
        if args[i] == "--date":
            date_str = args[i + 1]
            i += 2
        elif args[i] == "--notes":
            notes = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1
    return remaining, date_str, notes


def cmd_workout(args):
    """Pre-workout: show today's prescription."""
    if len(args) < 1:
        print("Usage: pullup_overload.py workout <bodyweight_lbs> [--date YYYY-MM-DD]")
        sys.exit(1)

    args, date_str, _ = parse_args(args)
    bodyweight = float(args[0])
    sessions = load_sessions()
    workout = calculate_workout(sessions, bodyweight)
    print(format_workout(workout, bodyweight, date_str))


def cmd_log(args):
    """Post-workout: log completed session."""
    if len(args) < 2:
        print("Usage: pullup_overload.py log <bodyweight_lbs> <rep1> <rep2> ... [--date YYYY-MM-DD] [--notes '...']")
        sys.exit(1)

    args, date_str, notes = parse_args(args)
    bodyweight = float(args[0])
    reps = [int(r) for r in args[1:]]

    if not reps:
        print("Error: provide at least one rep count.")
        sys.exit(1)

    sessions = load_sessions()
    current_week = determine_week(sessions)

    total = sum(reps)
    volume = bodyweight * total

    session = {
        "date": date_str,
        "week": current_week,
        "bodyweight_lbs": bodyweight,
        "reps_per_set": reps,
        "total_reps": total,
        "volume_lbs": round(volume, 1),
        "notes": notes,
    }
    save_session(session)

    print("\n  SESSION LOGGED!")
    print(format_log_entry(session))

    # Compare to last session
    if sessions:
        last = sessions[-1]
        diff = total - last["total_reps"]
        vol_diff = volume - last["volume_lbs"]
        arrow = "+" if diff >= 0 else ""
        print(f"\n  vs last: {arrow}{diff} reps ({arrow}{vol_diff:.0f} lbs volume)")

    # Weekly check
    sessions.append(session)
    week_sessions = [s for s in sessions if s["week"] == current_week]
    week_sets = sum(len(s["reps_per_set"]) for s in week_sessions)
    print(f"  This week: {len(week_sessions)}/{SESSIONS_PER_WEEK} sessions, {week_sets} total sets")


def cmd_history(args):
    """Show session history."""
    sessions = load_sessions()
    n = int(args[0]) if args else 10
    print(format_history(sessions, n))


def cmd_status(args):
    """Show current program status."""
    sessions = load_sessions()
    if not sessions:
        print("  No sessions yet. Start with: workout <bodyweight_lbs>")
        return

    current_week = get_current_week(sessions)
    this_week = [s for s in sessions if s["week"] == current_week]
    last = sessions[-1]

    print(f"\n  Program Status:")
    print(f"  Total sessions: {len(sessions)}")
    print(f"  Current week: {current_week}")
    print(f"  Sessions this week: {len(this_week)}/{SESSIONS_PER_WEEK}")

    reps_str = "/".join(str(r) for r in last["reps_per_set"])
    print(f"  Last session: [{reps_str}] at {last['bodyweight_lbs']} lbs ({last['date']})")

    if is_deload_week(current_week):
        print(f"  ** This is a DELOAD week **")
    else:
        next_deload = DELOAD_EVERY_WEEKS - ((current_week - 1) % DELOAD_EVERY_WEEKS)
        print(f"  Next deload in: {next_deload} week(s)")


COMMANDS = {
    "workout": cmd_workout,
    "log": cmd_log,
    "history": cmd_history,
    "status": cmd_status,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("\n  Pull-Up Progressive Overload Tracker")
        print("  =====================================")
        print("  Commands:")
        print("    workout <bodyweight_lbs> [--date YYYY-MM-DD]        — Pre-workout prescription")
        print("    log <bodyweight_lbs> <r1> <r2> ... [--date] [--notes]  — Post-workout log")
        print("    history [N]                                         — Show last N sessions")
        print("    status                                              — Program status")
        sys.exit(0)

    cmd = sys.argv[1]
    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
