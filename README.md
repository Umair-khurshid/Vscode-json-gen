# Vscode Json Generator
[![Pylint](https://github.com/Umair-khurshid/Vscode-json-gen/actions/workflows/pylint.yml/badge.svg)](https://github.com/Umair-khurshid/Vscode-json-gen/actions/workflows/pylint.yml) 

A simple tool to automatically generate `c_cpp_properties.json` for C/C++ projects in Visual Studio Code by parsing your Makefile-based build.

This helps developers avoid the tedious process of manually specifying paths and flags like `"includePath"`, `"defines"`, and `"compilerPath"` in VS Code settings.

## Features

- Parses `make` output to extract `-I`, `-D`, and `-std` flags
- Detects the appropriate `compilerPath`
- Outputs a VS Code-compatible `c_cpp_properties.json`
- Dockerized for easy and consistent usage
- Supports projects with multiple source files and configurations

## Usage
1. Build the Docker image

`docker build -t vscode-json-gen .`

2. Run the tool
Run it inside a C/C++ project that uses a Makefile:
`docker run --rm -v $(pwd):/app vscode-json-gen`
This will output `.vscode/c_cpp_properties.json` in your current project directory.

Your project must have a working Makefile at the root directory.
