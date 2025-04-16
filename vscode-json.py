#!/usr/bin/env python3
"""
Auto-generates c_cpp_properties.json from a Makefile-based C/C++ project.
"""

import os
import re
import subprocess
import json

def get_build_output():
    """Runs `make` in dry-run mode and returns its output lines."""
    result = subprocess.run(["make", "-n"], stdout=subprocess.PIPE, text=True, check=True)
    return result.stdout.splitlines()

def add_one_include_path_or_define(option, result_dict):
    """Extracts and appends include path or define from compiler option."""
    if option.startswith("-I"):
        path = option[2:]
        if path and path not in result_dict["includePath"]:
            result_dict["includePath"].append(path)
    elif option.startswith("-D"):
        define = option[2:]
        if define and define not in result_dict["defines"]:
            result_dict["defines"].append(define)

def get_standard_version(line):
    """Extracts standard version (c++11, c11, etc.) from compiler flags."""
    match = re.search(r'-std=(c\+\+|c)(\d+)', line)
    if match:
        return match.group(0)
    return None

def parse_compile_options(lines):
    """Parses lines for include paths, defines, and standard version."""
    result = {
        "includePath": [],
        "defines": [],
        "compilerPath": "",
        "standard": "c++17"
    }

    for line in lines:
        if "gcc" in line or "g++" in line:
            tokens = line.split()
            result["compilerPath"] = tokens[0]
            for token in tokens:
                add_one_include_path_or_define(token, result)
                std = get_standard_version(token)
                if std:
                    result["standard"] = std

    return result

def write_json_file(data, output_path):
    """Writes the given dictionary to the JSON file at output_path."""
    config = {
        "configurations": [
            {
                "name": "Linux",
                "includePath": data["includePath"],
                "defines": data["defines"],
                "compilerPath": data["compilerPath"],
                "cStandard": "c11" if "c" in data["standard"] else "gnu11",
                "cppStandard": data["standard"],
                "intelliSenseMode": "linux-gcc-x64"
            }
        ],
        "version": 4
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(config, outfile, indent=4)
    print(f"✅ Generated {output_path}")

if __name__ == "__main__":
    build_lines = get_build_output()
    options = parse_compile_options(build_lines)
    output_file = ".vscode/c_cpp_properties.json"
    write_json_file(options, output_file)
