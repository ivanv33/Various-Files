#!/usr/bin/env python3
"""
Pull-Up Progressive Overload Calculator
========================================
Agent-operated: Claude runs this script with CLI args, not the user.

Program design based on:
- Renaissance Periodization (RP) mesocycle volume progression
- Double progression method (reps first, then load)
- Daily Undulating Periodization (DUP) across 3 weekly sessions
- Deload every 4-6 weeks

3-day split per week:
  Day 1 (Heavy)   — weighted pull-ups, 4x 4-6 reps, 3 min rest
  Day 2 (Volume)  — bodyweight pull-ups, 4x 8-12 reps, 2 min rest
  Day 3 (Density) — bodyweight pull-ups, 3x 12-15+ reps, 90s rest

Progression rules (double progression):
  1. Add reps within the target range until hitting top of range for all sets
  2. When top of range hit across 2 sessions, add weight (2.5-5 lbs) & reset reps
  3. If plateaued on load+reps, add 1 set (up to weekly max ~20 hard sets)
  4. Deload week every 4-6 weeks: 50% volume, stay far from failure

Data stored in pullup_log.csv
"""

import csv
import os
import sys
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pullup_log.csv")
CSV_FIELDS = [
    "date", "week", "day_type", "bodyweight_lbs",
    "added_weight_lbs", "set1", "set2", "set3", "set4", "set5",
    "total_reps", "volume_lbs", "notes",
]

# Day type configurations: (name, target_sets, rep_low, rep_high, rest_seconds)
DAY_TYPES = {
    "heavy":   {"label": "Heavy (Strength-Hypertrophy)", "sets": 4, "rep_low": 4, "rep_high": 6, "rest": 180},
    "volume":  {"label": "Volume (Hypertrophy)",         "sets": 4, "rep_low": 8, "rep_high": 12, "rest": 120},
    "density": {"label": "Density (Endurance-Hyper)",    "sets": 3, "rep_low": 12, "rep_high": 15, "rest": 90},
}

MAX_SETS = 5
DELOAD_EVERY_WEEKS = 5
WEIGHT_INCREMENT_LBS = 2.5


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
                "day_type": row["day_type"],
                "bodyweight_lbs": float(row["bodyweight_lbs"]),
                "added_weight_lbs": float(row.get("added_weight_lbs", 0) or 0),
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
            "day_type": session["day_type"],
            "bodyweight_lbs": session["bodyweight_lbs"],
            "added_weight_lbs": session["added_weight_lbs"],
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


def get_last_session_of_type(sessions, day_type):
    for s in reversed(sessions):
        if s["day_type"] == day_type:
            return s
    return None


def determine_day_type(sessions):
    """Figure out which day type is next based on the weekly rotation."""
    week_order = ["heavy", "volume", "density"]
    if not sessions:
        return week_order[0]

    current_week = get_current_week(sessions)
    this_week_sessions = [s for s in sessions if s["week"] == current_week]
    done_types = [s["day_type"] for s in this_week_sessions]

    for dt in week_order:
        if dt not in done_types:
            return dt

    # All 3 done this week — start new week
    return week_order[0]


def is_deload_week(week_num):
    return week_num > 1 and (week_num - 1) % DELOAD_EVERY_WEEKS == 0


def calculate_workout(sessions, bodyweight, day_type):
    """Calculate today's prescription."""
    config = DAY_TYPES[day_type]
    current_week = get_current_week(sessions)

    # Check if we're starting a new week
    this_week_sessions = [s for s in sessions if s["week"] == current_week]
    done_types = [s["day_type"] for s in this_week_sessions]
    if day_type in done_types or (len(done_types) >= 3):
        current_week += 1

    deload = is_deload_week(current_week)
    last = get_last_session_of_type(sessions, day_type)

    result = {
        "week": current_week,
        "day_type": day_type,
        "label": config["label"],
        "rest": config["rest"],
        "deload": deload,
    }

    if deload:
        # Deload: 50% volume, use week 1 weights, stay far from failure (4+ RIR)
        num_sets = max(2, config["sets"] // 2)
        target_reps = config["rep_low"]
        added_weight = last["added_weight_lbs"] if last else 0
        # Use lighter weight on deload
        added_weight = max(0, added_weight - WEIGHT_INCREMENT_LBS * 2)

        result.update({
            "sets": num_sets,
            "rep_targets": [target_reps] * num_sets,
            "added_weight_lbs": added_weight,
            "note": "DELOAD WEEK: 50% volume, stay 4+ reps from failure. Recovery week!",
        })
        return result

    if last is None:
        # First session of this type: rep test
        result.update({
            "sets": config["sets"],
            "rep_targets": None,  # max effort test
            "added_weight_lbs": 0,
            "note": f"FIRST {day_type.upper()} SESSION: Do max clean reps each set, stop 1-2 before failure. "
                    f"Target range is {config['rep_low']}-{config['rep_high']} reps. Full ROM!",
        })
        return result

    # --- Double progression logic ---
    last_reps = last["reps_per_set"]
    last_sets = len(last_reps)
    added_weight = last["added_weight_lbs"]
    avg_reps = sum(last_reps) / len(last_reps)
    all_hit_top = all(r >= config["rep_high"] for r in last_reps)

    # Account for bodyweight changes as effective load changes
    bw_delta = bodyweight - last["bodyweight_lbs"]
    last_total_load = last["bodyweight_lbs"] + last["added_weight_lbs"]
    bw_note = ""

    if abs(bw_delta) >= WEIGHT_INCREMENT_LBS:
        if bw_delta > 0:
            # BW went up — treat as implicit load increase, reduce added weight to compensate
            compensate = min(added_weight, bw_delta)
            added_weight -= compensate
            added_weight = round(added_weight / WEIGHT_INCREMENT_LBS) * WEIGHT_INCREMENT_LBS
            added_weight = max(0, added_weight)
            new_total = bodyweight + added_weight
            bw_note = (f"BW up {bw_delta:+.1f} lbs since last {day_type}. "
                       f"Adjusted belt weight to keep total load ~{new_total:.0f} lbs. ")
        else:
            # BW went down — effective load decreased, keep added weight (free progression room)
            new_total = bodyweight + added_weight
            bw_note = (f"BW down {bw_delta:+.1f} lbs since last {day_type} "
                       f"(total load {new_total:.0f} vs {last_total_load:.0f} lbs). ")

    # Check if top of range was hit in last TWO sessions of this type (2-for-2 rule)
    same_type_sessions = [s for s in sessions if s["day_type"] == day_type]
    hit_top_twice = False
    if len(same_type_sessions) >= 2:
        prev_two = same_type_sessions[-2:]
        hit_top_twice = all(
            all(r >= config["rep_high"] for r in s["reps_per_set"])
            for s in prev_two
        )

    num_sets = config["sets"]
    note = ""

    if hit_top_twice and bw_delta >= WEIGHT_INCREMENT_LBS:
        # 2-for-2 hit but BW already went up — skip adding belt weight
        rep_targets = [config["rep_low"]] * num_sets
        note = (f"2-for-2 hit, but BW already increased {bw_delta:+.1f} lbs — "
                f"no extra belt weight needed. Reset to {config['rep_low']} reps.")
    elif hit_top_twice:
        # 2-for-2 rule: add weight, reset to bottom of rep range
        added_weight += WEIGHT_INCREMENT_LBS
        rep_targets = [config["rep_low"]] * num_sets
        note = (f"2-for-2 hit! Adding {WEIGHT_INCREMENT_LBS} lbs "
                f"(now +{added_weight} lbs). Reset to {config['rep_low']} reps.")
    elif all_hit_top:
        # Hit top once — repeat at top, one more session to confirm
        rep_targets = [config["rep_high"]] * num_sets
        note = (f"You hit {config['rep_high']} across all sets last time. "
                f"Do it again to trigger a weight increase!")
    elif avg_reps < config["rep_low"]:
        # Below range — keep weight, aim to match or beat last total by 1-2 reps
        rep_targets = [min(r + 1, config["rep_high"]) for r in last_reps]
        note = (f"Building up. Last avg was {avg_reps:.1f} (target: {config['rep_low']}-{config['rep_high']}). "
                f"Beat last total of {sum(last_reps)} reps.")
    else:
        # Normal: +1 rep per set
        rep_targets = [min(r + 1, config["rep_high"]) for r in last_reps]
        while len(rep_targets) < num_sets:
            rep_targets.append(config["rep_low"])
        note = f"+1 rep per set vs last time. Last total: {sum(last_reps)}."

    if bw_note:
        note = bw_note + note

    # RIR guidance based on mesocycle position (weeks within block)
    block_week = ((current_week - 1) % DELOAD_EVERY_WEEKS) + 1
    if block_week <= 2:
        rir = "3 RIR (start of block — leave gas in the tank)"
    elif block_week <= 3:
        rir = "2 RIR (mid block — push a bit harder)"
    else:
        rir = "0-1 RIR (end of block — push close to failure)"

    result.update({
        "sets": num_sets,
        "rep_targets": rep_targets,
        "added_weight_lbs": added_weight,
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
    lines.append(f"  {workout['label']}")
    lines.append("=" * 55)
    total_load = bodyweight + workout["added_weight_lbs"]
    lines.append(f"  Bodyweight: {bodyweight} lbs | Total load: {total_load} lbs")
    if workout["added_weight_lbs"] > 0:
        lines.append(f"  Added weight: +{workout['added_weight_lbs']} lbs")
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
        lines.append(f"  Total rep target: {sum(workout['rep_targets'])}")
        effective_weight = bodyweight + workout["added_weight_lbs"]
        vol = effective_weight * sum(workout["rep_targets"])
        lines.append(f"  Volume target: {vol:.0f} lbs")

    lines.append(f"\n  >> {workout['note']}")
    lines.append("=" * 55)
    return "\n".join(lines)


def format_log_entry(session):
    """Return formatted string of a logged session."""
    lines = []
    reps_str = " / ".join(str(r) for r in session["reps_per_set"])
    lines.append(f"  Date: {session['date']}")
    lines.append(f"  Week {session['week']} | {session['day_type'].upper()}")
    lines.append(f"  Bodyweight: {session['bodyweight_lbs']} lbs | Added: +{session['added_weight_lbs']} lbs")
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
        added = f"+{s['added_weight_lbs']}lb " if s["added_weight_lbs"] > 0 else ""
        lines.append(
            f"  {s['date']}  W{s['week']} {s['day_type']:7s}  "
            f"{s['bodyweight_lbs']}lb {added}[{reps_str}]  "
            f"vol:{s['volume_lbs']:.0f}lb"
        )

    # Weekly summary
    if sessions:
        current_week = sessions[-1]["week"]
        week_sessions = [s for s in sessions if s["week"] == current_week]
        week_sets = sum(len(s["reps_per_set"]) for s in week_sessions)
        week_vol = sum(s["volume_lbs"] for s in week_sessions)
        lines.append(f"\n  This week (W{current_week}): {len(week_sessions)}/3 sessions, "
                      f"{week_sets} sets, {week_vol:.0f} lbs total volume")
    return "\n".join(lines)


def parse_common_args(args):
    """Extract --date and other common flags from args. Returns (remaining_args, date_str)."""
    remaining = []
    date_str = datetime.now().strftime("%Y-%m-%d")
    i = 0
    while i < len(args):
        if args[i] == "--date":
            date_str = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1
    return remaining, date_str


def cmd_workout(args):
    """Get today's workout (pre-workout). Usage: workout <bodyweight_lbs> [day_type] [--date YYYY-MM-DD]"""
    if len(args) < 1:
        print("Usage: pullup_overload.py workout <bodyweight_lbs> [heavy|volume|density] [--date YYYY-MM-DD]")
        sys.exit(1)

    args, date_str = parse_common_args(args)
    bodyweight = float(args[0])
    sessions = load_sessions()

    if len(args) >= 2 and args[1] in DAY_TYPES:
        day_type = args[1]
    else:
        day_type = determine_day_type(sessions)

    workout = calculate_workout(sessions, bodyweight, day_type)
    print(format_workout(workout, bodyweight, date_str))


def cmd_log(args):
    """Log a completed session (post-workout). Usage: log <bodyweight_lbs> <day_type> <rep1> <rep2> ... [--weight X] [--notes "..."] [--date YYYY-MM-DD]"""
    if len(args) < 3:
        print("Usage: pullup_overload.py log <bodyweight_lbs> <day_type> <rep1> <rep2> ... [--weight X] [--notes '...'] [--date YYYY-MM-DD]")
        sys.exit(1)

    # Extract --date first before other parsing
    date_str = datetime.now().strftime("%Y-%m-%d")
    filtered_args = []
    i = 0
    while i < len(args):
        if args[i] == "--date":
            date_str = args[i + 1]
            i += 2
        else:
            filtered_args.append(args[i])
            i += 1
    args = filtered_args

    bodyweight = float(args[0])
    day_type = args[1]
    if day_type not in DAY_TYPES:
        print(f"Invalid day type: {day_type}. Must be one of: {', '.join(DAY_TYPES.keys())}")
        sys.exit(1)

    # Parse reps and optional flags
    reps = []
    added_weight = 0.0
    notes = ""
    i = 2
    while i < len(args):
        if args[i] == "--weight":
            added_weight = float(args[i + 1])
            i += 2
        elif args[i] == "--notes":
            notes = args[i + 1]
            i += 2
        else:
            reps.append(int(args[i]))
            i += 1

    if not reps:
        print("Error: provide at least one rep count.")
        sys.exit(1)

    sessions = load_sessions()
    current_week = get_current_week(sessions)

    # Determine if we should bump the week
    this_week_sessions = [s for s in sessions if s["week"] == current_week]
    done_types = [s["day_type"] for s in this_week_sessions]
    if day_type in done_types or len(done_types) >= 3:
        current_week += 1

    total = sum(reps)
    effective_weight = bodyweight + added_weight
    volume = effective_weight * total

    session = {
        "date": date_str,
        "week": current_week,
        "day_type": day_type,
        "bodyweight_lbs": bodyweight,
        "added_weight_lbs": added_weight,
        "reps_per_set": reps,
        "total_reps": total,
        "volume_lbs": round(volume, 1),
        "notes": notes,
    }
    save_session(session)

    print("\n  SESSION LOGGED!")
    print(format_log_entry(session))

    # Compare to last session of same type
    last = get_last_session_of_type(sessions, day_type)
    if last:
        diff = total - last["total_reps"]
        vol_diff = volume - last["volume_lbs"]
        arrow = "+" if diff >= 0 else ""
        print(f"\n  vs last {day_type}: {arrow}{diff} reps ({arrow}{vol_diff:.0f} lbs volume)")

    # Weekly check
    sessions.append(session)
    week_sessions = [s for s in sessions if s["week"] == current_week]
    week_sets = sum(len(s["reps_per_set"]) for s in week_sessions)
    print(f"  Weekly sets: {week_sets} (target: 10-20 for hypertrophy)")


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
    total_sessions = len(sessions)
    this_week = [s for s in sessions if s["week"] == current_week]

    print(f"\n  Program Status:")
    print(f"  Total sessions: {total_sessions}")
    print(f"  Current week: {current_week}")
    print(f"  Sessions this week: {len(this_week)}/3")

    if is_deload_week(current_week):
        print(f"  ** This is a DELOAD week **")
    else:
        next_deload = DELOAD_EVERY_WEEKS - ((current_week - 1) % DELOAD_EVERY_WEEKS)
        print(f"  Next deload in: {next_deload} week(s)")

    # Per day-type progress
    print(f"\n  Progress by day type:")
    for dt in ["heavy", "volume", "density"]:
        last = get_last_session_of_type(sessions, dt)
        if last:
            reps_str = "/".join(str(r) for r in last["reps_per_set"])
            added = f" +{last['added_weight_lbs']}lb" if last["added_weight_lbs"] > 0 else ""
            print(f"    {dt:8s}: [{reps_str}]{added}  (W{last['week']})")
        else:
            print(f"    {dt:8s}: not started")


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
        print("    workout <bodyweight_lbs> [heavy|volume|density] [--date YYYY-MM-DD]  — Pre-workout prescription")
        print("    log <bodyweight_lbs> <day_type> <r1> <r2> ... [--weight X] [--notes '...'] [--date YYYY-MM-DD]  — Post-workout log")
        print("    history [N]  — Show last N sessions")
        print("    status  — Show program status")
        sys.exit(0)

    cmd = sys.argv[1]
    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
