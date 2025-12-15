import argparse
import json
import sys
import os
import datetime

def analyze_runs(path, run_type):
    runs = []
    for file in os.listdir(path):
        with open(os.path.join(path, file), 'r') as f:
            data = json.load(f)
            for run in data:
                if run["name"] != run_type: continue
                runs.append(run)

    attempts = 0
    successes = 0
    segments = [None] * 11
    best_run = None

    for run in runs:
        attempts += 1

        for idx, segment in enumerate(run["objectives"]):
            if run["objectives"][10]["duration"] == 0:
                continue
            if segment["status"] != 2:
                continue
            if segments[idx] is None or segment["duration"] < segments[idx]:
                segments[idx] = segment["duration"]

        if run["objectives"][10]["status"] == 2:
            successes += 1
            if best_run is None or run["objectives"][10]["done"] < best_run["objectives"][10]["done"]:
                best_run = run

    time_to_complete = best_run["objectives"][10]["done"]
    sum_of_bests = sum(filter(None, segments))

    print(f"Total Attempts: {attempts}")
    print(f"Successful Runs: {successes}")
    print(f"Best run: {time_to_complete // 60000}m {(time_to_complete % 60000) // 1000}s on {datetime.datetime.fromtimestamp(best_run['utc_start'], datetime.timezone.utc).strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"Sum of best segments: {sum_of_bests // 60000}m {(sum_of_bests % 60000) // 1000}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to the runs directory")
    parser.add_argument("--type", help="Type of run to analyze")
    args = parser.parse_args()

    if not args.path or not args.type:
        print("Please provide both --path and --type arguments.")
        sys.exit(1)

    analyze_runs(args.path, args.type)