#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Set, Tuple

includePath: Set[str] = set()
defines: Set[str] = set()
cStandard: Set[str] = set()
cppStandard: Set[str] = set()
gccPath: str = ""

def getBuildOutput(command: List[str]) -> List[str]:
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    outString, _ = proc.communicate()
    if proc.returncode != 0:
        print("Failed to build.")
        return [""]
    return outString.decode('utf-8').splitlines()

def addOneIncludePathOrDefines(lineSliced: str, include_define: Set[str]) -> str:
    lineStr = lineSliced[2:].lstrip()
    if lineStr.startswith("'"):
        startIndex, endIndex = 1, lineStr[1:].find("'") + 1
    elif lineStr.startswith('"'):
        startIndex, endIndex = 1, lineStr[1:].find('"') + 1
    else:
        startIndex, endIndex = 0, lineStr.find(" ")
        if endIndex == -1:
            endIndex = len(lineStr)

    token = lineStr[startIndex:endIndex]
    if lineSliced.startswith("-I"):
        try:
            out = subprocess.check_output(["readlink", "-e", "-n", token], text=True).strip()
            include_define.add(out)
        except subprocess.CalledProcessError:
            pass
    else:
        include_define.add(token)

    return lineStr[endIndex:]

def getStandardVersion(lineSliced: str) -> str:
    endIndex = lineSliced.find(" ")
    if endIndex == -1:
        endIndex = len(lineSliced)
    stdVerStr = lineSliced[5:endIndex]

    if "++" in stdVerStr:
        cppStandard.add(stdVerStr)
    else:
        cStandard.add(stdVerStr)

    return lineSliced[endIndex:]

def parseCompileOptions(line: str) -> None:
    global gccPath
    index = line.find(" ")
    if index == -1:
        return
    gccCmd = line[:index]
    if gccCmd.startswith("/"):
        gccPath = gccCmd
    else:
        gccPath = os.popen("which " + gccCmd).read().strip('\n')
    lineOptionStr = line[index+1:]

    while lineOptionStr != "":
        lineOptionStr = lineOptionStr.strip()
        if lineOptionStr.startswith("-I"):
            lineOptionStr = addOneIncludePathOrDefines(lineOptionStr, includePath)
        elif lineOptionStr.startswith("-D"):
            lineOptionStr = addOneIncludePathOrDefines(lineOptionStr, defines)
        elif lineOptionStr.startswith("-std="):
            lineOptionStr = getStandardVersion(lineOptionStr)
        else:
            startIndex = lineOptionStr.find(" ")
            if startIndex == -1:
                break
            lineOptionStr = lineOptionStr[startIndex:]

def parseBuildOutput(lines: List[str]) -> int:
    builtLineNum = 0
    for line in lines:
        index = line.find(" ")
        if index == -1:
            continue
        lineCmd = line[:index]
        if lineCmd.endswith("gcc") or lineCmd.endswith("g++"):
            if "-M" in line:
                continue
            builtLineNum += 1
            parseCompileOptions(line)
    return builtLineNum

def getStandardCVersion(toolchainPath: str) -> Tuple[str, str]:
    StdCVersion, StdCppVersion = "", ""

    if cStandard:
        StdCVersion = list(cStandard)[0]
    if cppStandard:
        StdCppVersion = list(cppStandard)[0]
    if StdCVersion and StdCppVersion:
        return StdCVersion, StdCppVersion

    if not (toolchainPath.endswith("gcc") or toolchainPath.endswith("g++")):
        return StdCVersion, StdCppVersion

    # Detect missing C standard
    if StdCVersion == "":
        with open("tmp_build_test.c", "w") as f:
            f.write("int main(){return 0;}\n")
        for option in ["-std=c17", "-std=c11", "-std=c99", "-std=c89"]:
            command = [toolchainPath, option, "tmp_build_test.c", "-o", "tmp_build_test"]
            proc = subprocess.Popen(command, stderr=subprocess.DEVNULL)
            proc.communicate()
            if proc.returncode == 0:
                StdCVersion = option[5:]
                break

    # Detect missing C++ standard
    if StdCppVersion == "":
        with open("tmp_build_test.cpp", "w") as f:
            f.write("int main(){return 0;}\n")
        for option in ["-std=c++17", "-std=c++14", "-std=c++11", "-std=c++03", "-std=c++98"]:
            command = [toolchainPath, option, "tmp_build_test.cpp", "-o", "tmp_build_test"]
            proc = subprocess.Popen(command, stderr=subprocess.DEVNULL)
            proc.communicate()
            if proc.returncode == 0:
                StdCppVersion = option[5:]
                break

    # Cleanup
    for f in ["tmp_build_test", "tmp_build_test.c", "tmp_build_test.cpp"]:
        if os.path.exists(f):
            os.remove(f)

    return StdCVersion, StdCppVersion

def writeJsonFile(jsonFileName: str) -> None:
    stdCVer, stdCppVer = getStandardCVersion(gccPath)

    configDict: Dict[str, Any] = {
        "name": "Linux",
        "includePath": sorted(includePath),
        "defines": sorted(defines),
        "compilerPath": gccPath,
        "cStandard": stdCVer,
        "cppStandard": stdCppVer,
    }

    outputJson = {
        "configurations": [configDict],
        "version": 4
    }

    try:
        with open(jsonFileName, "w") as outFile:
            json.dump(outputJson, outFile, indent=4)
    except IOError:
        print("Failed to open " + jsonFileName + " file.")
        sys.exit(1)

if __name__ == '__main__':
    commands = ["make", "-n"]
    curPath = os.getcwd()
    projectPath = os.path.dirname(os.path.abspath(__file__))
    if curPath == projectPath:
        jsonFileName = ".vscode/c_cpp_properties.json"
    else:
        jsonFileName = projectPath + "/" + ".vscode/c_cpp_properties.json"
        commands.append("-C")
        commands.append(projectPath)

    for arg in sys.argv[1:]:
        commands.append(arg)

    print("Running dry-run...")
    makeOutputLines = getBuildOutput(commands)
    if makeOutputLines[0] == "":
        print("No build output.")
        sys.exit(1)

    print("Parsing output...")
    parsedLineNum = parseBuildOutput(makeOutputLines)
    if parsedLineNum == 0:
        print("Nothing built in dry-run.")
    else:
        print(f"Parsed {parsedLineNum} build lines.")

    if not os.path.exists(".vscode"):
        os.mkdir(".vscode")
    writeJsonFile(jsonFileName)
    os.system("ls -l " + jsonFileName)

