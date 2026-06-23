# Used to construct a list of scenario dictionaries to loop over in ansible.
# See params.json and baseline_params.json for input format.
# See scenarios.txt and baseline_scenarios.txt for corresponding output. 
# Paste contents of the output files under "scenarios:" in ../clients/defaults/main.yml

import itertools
import json
import sys
from pprint import pprint

def build_ping_args(scenario):
    # Construct command-line arguments for ping based on parameter values
    args = []
    if "ping_rate" in scenario:
        args.append(f"-i {scenario["ping_rate"]}")
    if "ping_size" in scenario:
        args.append(f"-s {int(scenario["ping_size"])-8}")
    return " ".join(args)

def build_iperf_args(scenario):
    # Construct command-line arguments for iperf based on parameter values
    args = []
    bg_label = []
    # Protocol
    if "iperf_protocol" in scenario:
        val = scenario["iperf_protocol"].upper()
        bg_label.append(val)
        if val == "UDP":
            args.append("-u")
    else:
        scenario["iperf_protocol"] = "None"

    # Rate
    if "iperf_rate" in scenario:
        args.append(f"-b {scenario["iperf_rate"]}")
        bg_label.append(scenario["iperf_rate"])
    else:
        scenario["iperf_rate"] = "None"

    # Direction
    if "iperf_dir" in scenario:
        val = scenario["iperf_dir"].lower()
        bg_label.append(val)
        if val == "down":
            args.append("-R")
    else:
        scenario["iperf_dir"] = "None"
    
    # Build a label combining all values relating to background traffic, to simplify plotting
    # iPerf will only be run when this value is not "None"
    if len(bg_label) > 0:
        scenario["bg_traffic"] = "_".join(bg_label)
    else:
        scenario["bg_traffic"] = "None"

    return " ".join(args)

def build(infile, outfile):
    # Read parameters
    param_file = infile
    with open(param_file, "r") as f:
        params = json.load(f)

    # Get all permutations
    keys, values = zip(*params.items())
    scenarios = [dict(zip(keys, v)) for v in itertools.product(*values)]

    # Write scenarios
    with open(outfile, "w") as f:
        for i in scenarios:
            ping_args = build_ping_args(i)
            iperf_args = build_iperf_args(i)
            i["ping_args"] = ping_args
            i["iperf_args"] = iperf_args
            s = []
            for k, v in i.items():
                # If the value is non-numeric, wrap it in quotes when writing to file
                try:
                    _ = float(v)
                except:
                    v = f'"{v}"'
                s.append(f"{k}: {v}")
            f.write("  - " + "{" + ", ".join(s) + "}\n")

def main():
    build("params.json", "scenarios.txt")
    build("baseline_params.json", "baseline_scenarios.txt")

if __name__ == "__main__":
    main()
