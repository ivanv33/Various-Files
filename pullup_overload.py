#!/usr/bin/env python3
"""
Pull-Up Progressive Overload Calculator
========================================
Tracks bodyweight and calculates sets/reps for hypertrophy.
Training frequency: 3x per week.

Data stored in pullup_log.csv

Hypertrophy principles:
- 10-20 hard sets per muscle group per week (3 sessions = ~4-6 sets/session)
- Rep range: 5-12 reps (pull-ups are harder, so 5+ counts)
- Progressive overload: add reps -> add sets -> add weight
- 1-2 RIR (reps in reserve) on most sets
"""

import csv
import os
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pullup_log.csv")
CSV_FIELDS = ["date", "bodyweight_kg", "set1", "set2", "set3", "set4", "set5", "total_reps", "volume_kg"]

# --- Program constants ---
SESSIONS_PER_WEEK = 3
MIN_REPS = 5
MAX_REPS = 12
START_SETS = 3
MAX_SETS = 5
REST_SECONDS = 90


def load_sessions():
    """Load all sessions from CSV. Returns list of dicts."""
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
                "bodyweight_kg": float(row["bodyweight_kg"]),
                "reps_per_set": reps,
                "total_reps": int(row["total_reps"]),
                "volume_kg": float(row["volume_kg"]),
            })
    return sessions


def save_session(session):
    """Append a single session to the CSV."""
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        row = {
            "date": session["date"],
            "bodyweight_kg": session["bodyweight_kg"],
            "total_reps": session["total_reps"],
            "volume_kg": session["volume_kg"],
        }
        for i, reps in enumerate(session["reps_per_set"], 1):
            row[f"set{i}"] = reps
        writer.writerow(row)


def get_last_session(sessions):
    return sessions[-1] if sessions else None


def calculate_workout(bodyweight, last_session):
    """Calculate today's sets and rep targets based on last session."""

    if last_session is None:
        return {
            "type": "FIRST SESSION - Rep Test",
            "sets": 3,
            "rep_target": "Do as many clean reps as you can per set (stop 1-2 before failure)",
            "rest": f"{REST_SECONDS}s between sets",
            "notes": "This session determines your starting point. Full range of motion!",
        }

    last_reps = last_session["reps_per_set"]
    last_sets = len(last_reps)
    avg_reps = sum(last_reps) / len(last_reps)
    total_reps_last = sum(last_reps)

    new_sets = last_sets
    progression_note = ""

    if avg_reps >= MAX_REPS:
        if last_sets < MAX_SETS:
            new_sets = last_sets + 1
            target_reps = max(round(avg_reps - 2), MIN_REPS)
            progression_note = f"You averaged {avg_reps:.0f} reps -- adding a set! Drop reps slightly."
        else:
            target_reps = MIN_REPS + 2
            progression_note = (
                f"You're at max sets with {avg_reps:.0f} avg reps. "
                "Time to add weight (+2.5-5kg vest/belt) and reset reps."
            )
    elif avg_reps < MIN_REPS:
        target_reps = None
        progression_note = f"Building up -- aim to beat last total of {total_reps_last} reps by 1-2."
    else:
        target_reps = None
        progression_note = f"Add 1 rep to each set vs last time (total was {total_reps_last})."

    if target_reps is not None:
        rep_targets = [target_reps] * new_sets
    else:
        rep_targets = [min(r + 1, MAX_REPS) for r in last_reps]
        while len(rep_targets) < new_sets:
            rep_targets.append(max(rep_targets[-1] - 1, MIN_REPS))

    total_target = sum(rep_targets)
    volume = bodyweight * total_target

    return {
        "type": "Progressive Overload",
        "sets": new_sets,
        "rep_targets": rep_targets,
        "total_rep_target": total_target,
        "volume_kg": round(volume, 1),
        "rest": f"{REST_SECONDS}s between sets",
        "progression": progression_note,
    }


def display_workout(workout, bodyweight):
    print("\n" + "=" * 50)
    print("  PULL-UP WORKOUT -- " + workout["type"])
    print("=" * 50)
    print(f"  Bodyweight: {bodyweight} kg")
    print(f"  Rest: {workout['rest']}")
    print()

    if "rep_targets" in workout:
        for i, reps in enumerate(workout["rep_targets"], 1):
            print(f"  Set {i}:  aim for {reps} reps")
        print(f"\n  Total rep target: {workout['total_rep_target']}")
        print(f"  Volume target: {workout['volume_kg']} kg")
        print(f"\n  >> {workout['progression']}")
    else:
        print(f"  Sets: {workout['sets']}")
        print(f"  Reps: {workout['rep_target']}")
        print(f"\n  >> {workout['notes']}")

    print("=" * 50)


def record_session(bodyweight, workout):
    """After the workout, record actual reps."""
    print("\n--- LOG YOUR RESULTS ---")
    num_sets = workout["sets"]
    reps = []
    for i in range(1, num_sets + 1):
        while True:
            try:
                r = int(input(f"  Set {i} actual reps: "))
                reps.append(r)
                break
            except ValueError:
                print("  Enter a number.")

    total = sum(reps)
    volume = bodyweight * total
    print(f"\n  Total reps: {total}")
    print(f"  Volume: {volume:.1f} kg")

    sessions = load_sessions()
    last = get_last_session(sessions)
    if last:
        last_total = last["total_reps"]
        diff = total - last_total
        vol_diff = volume - last["volume_kg"]
        arrow = "+" if diff >= 0 else ""
        print(f"  vs last session: {arrow}{diff} reps ({arrow}{vol_diff:.1f} kg volume)")

    session = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "bodyweight_kg": bodyweight,
        "reps_per_set": reps,
        "total_reps": total,
        "volume_kg": round(volume, 1),
    }
    save_session(session)
    print("\n  Session saved!\n")

    # Weekly volume check
    sessions.append(session)
    week_sessions = [
        s for s in sessions
        if datetime.strptime(s["date"], "%Y-%m-%d") >= datetime.now() - timedelta(days=7)
    ]
    week_sets = sum(len(s["reps_per_set"]) for s in week_sessions)
    print(f"  Weekly sets so far: {week_sets} (target: 10-20 for hypertrophy)")


def show_history(sessions):
    if not sessions:
        print("\n  No sessions logged yet.\n")
        return
    print("\n--- HISTORY ---")
    for s in sessions[-10:]:
        reps_str = " / ".join(str(r) for r in s["reps_per_set"])
        print(f"  {s['date']}  |  {s['bodyweight_kg']}kg  |  [{reps_str}]  |  vol: {s['volume_kg']}kg")
    print()


def main():
    print("\n  PULL-UP PROGRESSIVE OVERLOAD TRACKER")
    print("  3x / week  |  Hypertrophy focused\n")

    sessions = load_sessions()

    while True:
        print("  1) Get today's workout")
        print("  2) View history")
        print("  3) Quit")
        choice = input("\n  > ").strip()

        if choice == "1":
            while True:
                try:
                    bw = float(input("\n  Your bodyweight today (kg): "))
                    break
                except ValueError:
                    print("  Enter a number.")

            last = get_last_session(sessions)
            workout = calculate_workout(bw, last)
            display_workout(workout, bw)

            done = input("\n  Done with workout? Log results? (y/n): ").strip().lower()
            if done == "y":
                record_session(bw, workout)
                sessions = load_sessions()

        elif choice == "2":
            show_history(sessions)

        elif choice == "3":
            print("\n  Keep pulling!\n")
            break


if __name__ == "__main__":
    main()
