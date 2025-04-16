"""
This script automates the creation of the c_cpp_properties.json file for
VS Code when using the Make build system. It extracts necessary information
from the build output and generates a JSON file with the correct include paths,
defines, and compiler information.
"""

def get_build_output(build_output):
    """
    Parses the build output to extract relevant information.

    Args:
        build_output (str): The output of the build process.
    
    Returns:
        list: A list of parsed lines.
    """
    out_string = []
    with open(build_output, 'r', encoding='utf-8') as file:
        for line in file:
            out_string.append(line.strip())
    return out_string


def add_one_include_path_or_defines(line_sliced):
    """
    Adds one include path or define to the project settings.

    Args:
        line_sliced (str): The line extracted from the build output containing
                           either an include path or a define.
    """
    line_str = line_sliced.strip()
    start_index = line_str.find("-I")
    end_index = line_str.find(" ", start_index + 2)

    if start_index != -1:
        start_index += 2
        include_path = line_str[start_index:end_index]
        return include_path
    else:
        start_index = line_str.find("-D")
        if start_index != -1:
            start_index += 2
            define_value = line_str[start_index:end_index]
            return define_value


def get_standard_version(line_sliced):
    """
    Extracts the standard version of the C or C++ compiler from the build output.

    Args:
        line_sliced (str): The line from the build output containing the compiler version.
    
    Returns:
        str: The standard version (e.g., C++17, C++14, etc.).
    """
    start_index = line_sliced.find("-std=")
    end_index = line_sliced.find(" ", start_index + 5)
    std_ver_str = line_sliced[start_index+5:end_index]
    return std_ver_str


def parse_compile_options(gcc_cmd):
    """
    Parses the compile options from the GCC command.

    Args:
        gcc_cmd (str): The GCC command line that includes the compile options.
    
    Returns:
        list: A list of parsed compile options.
    """
    compile_options = []
    with open(gcc_cmd, 'r', encoding='utf-8') as file:
        for line in file:
            compile_options.append(line.strip())
    return compile_options


def parse_build_output(build_output):
    """
    Parses the build output and extracts relevant information.

    Args:
        build_output (str): The output of the build process.
    
    Returns:
        dict: A dictionary containing parsed information from the build output.
    """
    built_line_num = 0
    build_data = {}

    with open(build_output, 'r', encoding='utf-8') as file:
        for line in file:
            line_cmd = line.strip()
            built_line_num += 1
            if '-I' in line_cmd or '-D' in line_cmd:
                build_data[built_line_num] = add_one_include_path_or_defines(line_cmd)
            elif "-std=" in line_cmd:
                build_data["standard_version"] = get_standard_version(line_cmd)

    return build_data


def get_standard_c_version(toolchain_path):
    """
    Gets the standard C version from the toolchain path.

    Args:
        toolchain_path (str): The path to the GCC toolchain.
    
    Returns:
        tuple: A tuple containing the C and C++ standard versions.
    """
    with open(toolchain_path, 'r', encoding='utf-8') as file:
        toolchain_info = file.read()
        std_c_version = "C11"  # Example, actual parsing needed
        std_cpp_version = "C++14"  # Example, actual parsing needed
    return std_c_version, std_cpp_version


def write_json_file(json_file_name, config_dict):
    """
    Writes the parsed configuration to a JSON file.

    Args:
        json_file_name (str): The name of the JSON file to write.
        config_dict (dict): The dictionary containing the configuration data.
    """
    with open(json_file_name, 'w', encoding='utf-8') as out_file:
        json.dump(config_dict, out_file, indent=4)
