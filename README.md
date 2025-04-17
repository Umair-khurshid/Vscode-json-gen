# Vscode Json Generator
[![Pylint](https://github.com/Umair-khurshid/Vscode-json-gen/actions/workflows/pylint.yml/badge.svg)](https://github.com/Umair-khurshid/Vscode-json-gen/actions/workflows/pylint.yml) 

A simple tool to automatically generate `c_cpp_properties.json` for C/C++ projects in Visual Studio Code by parsing your Makefile-based build. This helps developers avoid the tedious process of manually specifying paths and flags like `"includePath"`, `"defines"`, and `"compilerPath"` in VS Code settings.

---
## Features
- Extracts -I, -D, and -std flags from make output

- Automatically detects the appropriate compilerPath

- Generates a VS Code-compatible .vscode/c_cpp_properties.json

- Dockerized for consistent environment and easy usage

- Supports complex projects with multiple source files and configurations

## Usage
- Build the Docker image
```docker build -t vscode-json-gen .```

- Run the tool in a C/C++ project with a Makefile
```docker run --rm -v "$(pwd)":/app vscode-json-gen```
- This will generate the file:
```.vscode/c_cpp_properties.json in your current project directory.```
---
For this to work your project must have a valid Makefile at the root directory.
