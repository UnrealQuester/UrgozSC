import argparse
import json
import sys
import os
import datetime
import xml.etree.cElementTree as ET

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
    segments = {}
    best_run = None

    for run in runs:
        attempts += 1

        for segment in run["objectives"]:
            if run["objectives"][-1]["duration"] == 0:
                continue
            if segment["status"] != 2:
                continue
            if segment["name"] not in segments:
                segments[segment["name"]] = {
                    "name": segment["name"],
                    "duration": segment["duration"]
                }
            elif segment["duration"] < segments[segment["name"]]["duration"]:
                segments[segment["name"]]["duration"] = segment["duration"]

        if run["objectives"][-1]["status"] == 2:
            successes += 1
            if best_run is None or run["objectives"][-1]["done"] < best_run["objectives"][-1]["done"]:
                best_run = run

        for segment in best_run["objectives"]:
            segments[segment["name"]]["best_time"] = segment["done"]

    time_to_complete = best_run["objectives"][-1]["done"]
    sum_of_bests = sum(segment["duration"] for segment in segments.values())

    print(f"Total Attempts: {attempts}")
    print(f"Successful Runs: {successes}")
    print(f"Best run: {time_to_complete // 60000}m {(time_to_complete % 60000) // 1000}s on {datetime.datetime.fromtimestamp(best_run['utc_start'], datetime.timezone.utc).strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"Sum of best segments: {sum_of_bests // 60000}m {(sum_of_bests % 60000) // 1000}s")

    root = ET.Element("Run", {"version": "1.8.0"})
    ET.SubElement(root, "GameIcon")
    ET.SubElement(root, "GameName").text = "Guild Wars 1"
    ET.SubElement(root, "CategoryName").text = run_type
    metadata = ET.SubElement(root, "Metadata")
    ET.SubElement(metadata, "Run", {"id":""})
    ET.SubElement(metadata, "Platform", {"usesEmulator":"False"})
    ET.SubElement(metadata, "Region")
    ET.SubElement(metadata, "SpeedrunComVariables")
    ET.SubElement(metadata, "CustomVariables")
    ET.SubElement(root, "LayoutPath")
    ET.SubElement(root, "Offset").text = "00:00:00.000000000"
    ET.SubElement(root, "AttemptCount").text = str(attempts)
    attempt_history = ET.SubElement(root, "AttemptHistory")
    el_segments = ET.SubElement(root, "Segments")
    for segment in segments.values():
        segment_time = datetime.timedelta(milliseconds=segment["duration"])
        personal_best_time = datetime.timedelta(milliseconds=segment["best_time"])
        seg_elem = ET.SubElement(el_segments, "Segment")
        ET.SubElement(seg_elem, "Name").text = segment["name"]
        ET.SubElement(seg_elem, "Icon")
        split_times = ET.SubElement(seg_elem, "SplitTimes")
        split_time = ET.SubElement(split_times, "SplitTime", {"name":"Personal Best"})
        ET.SubElement(split_time, "RealTime").text = str(personal_best_time)
        best_segment_time = ET.SubElement(seg_elem, "BestSegmentTime")
        ET.SubElement(best_segment_time, "RealTime").text = str(segment_time)
        segment_history = ET.SubElement(seg_elem, "SegmentHistory")
    ET.SubElement(root, "AutoSplitterSettings")
    ET.ElementTree(root).write(run_type + ".lss")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to the runs directory")
    parser.add_argument("--type", help="Type of run to analyze")
    args = parser.parse_args()

    if not args.path or not args.type:
        print("Please provide both --path and --type arguments.")
        sys.exit(1)

    analyze_runs(args.path, args.type)