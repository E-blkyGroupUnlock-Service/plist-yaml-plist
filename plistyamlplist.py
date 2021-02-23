#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""If this script is run directly, it takes an input file and an output file
from the command line. It detects if the input file is a YAML or a PLIST file,
and converts to the other format:

plistyamlplist.py <input-file> <output-file>

The output file can be omitted. In this case, the name of the output file is
taken from the input file, with .yaml added to or taken off the end.
"""

import sys
import os
import glob


from plistyamlplist_lib.plist_yaml import plist_yaml
from plistyamlplist_lib.yaml_plist import yaml_plist
from plistyamlplist_lib.json_plist import json_plist
from plistyamlplist_lib.yaml_tidy import tidy_yaml


def usage():
    """print help."""
    print("Usage: plistyamlplist.py <input-file> <output-file>\n")
    print(
        "If <input-file> is a PLIST and <output-file> is omitted,\n"
        "<input-file> is converted to <input-file>.yaml\n"
    )
    print(
        "If <input-file> ends in .yaml or .yml and <output-file> is omitted,\n"
        "<input-file>.yaml is converted to PLIST format with name <input-file>\n"
    )
    print(
        "If <output-file> is --tidy,\n" "<input-file>.yaml is tidied up for AutoPkg.\n"
    )


def check_if_plist(in_path):
    """rather than restrict by filename, check if the file is a plist by
    reading the second line of the file for the PLIST declaration."""
    with open(in_path) as fp:
        for i, line in enumerate(fp):
            if i == 1:
                # print line
                if line.find("PLIST 1.0") == -1:
                    is_plist = False
                else:
                    is_plist = True
            elif i > 2:
                break
    return is_plist


def check_for_yaml_folder(check_path):
    """Check folder hierarchy for a YAML or _YAML folder. Output to same folder structure outwith YAML
    folder if it exists,
    e.g. /path/to/YAML/folder/subfolder/my.plist.yaml ==> /path/to/folder/subfolder/my.plist
    Note there is no reverse option at this time"""
    check_abspath = os.path.abspath(check_path)
    yaml_folders = ["_YAML", "YAML"]
    for yf in yaml_folders:
        if yf in check_abspath:
            print("{} folder exists : {}".format(yf, check_abspath))
            top_path, base_path = check_abspath.split("{}/".format(yf))
            out_path = os.path.dirname(os.path.join(top_path, base_path))
            if os.path.exists(out_path):
                print("Path exists : {}".format(out_path))
                return out_path
            else:
                print("Path does not exist : {}".format(out_path))
                print("Please create this folder and try again")
                exit(1)


def check_for_json_folder(check_path):
    """Check folder hierarchy for a JSON or _JSON folder. Output to same folder structure outwith JSON
    folder if it exists,
    e.g. /path/to/JSON/folder/subfolder/my.plist.json ==> /path/to/folder/subfolder/my.plist
    Note there is no reverse option at this time"""
    check_abspath = os.path.abspath(check_path)
    json_folders = ["_JSON", "JSON"]
    for jf in json_folders:
        if jf in check_abspath:
            print("{} folder exists : {}".format(jf, check_abspath))
            top_path, base_path = check_abspath.split("{}/".format(jf))
            out_path = os.path.dirname(os.path.join(top_path, base_path))
            if os.path.exists(out_path):
                print("Path exists : {}".format(out_path))
                return out_path
            else:
                print("Path does not exist : {}".format(out_path))
                print("Please create this folder and try again")
                exit(1)


def get_out_path(in_path, filetype):
    """determine the out_path when none given"""
    if filetype == "yaml":
        out_dir = check_for_yaml_folder(in_path)
        if out_dir:
            filename, _ = os.path.splitext(os.path.basename(in_path))
            out_path = os.path.join(out_dir, filename)
        else:
            filename, _ = os.path.splitext(os.path.abspath(in_path))
            out_path = filename
    elif filetype == "json":
        out_dir = check_for_json_folder(in_path)
        if out_dir:
            filename, _ = os.path.splitext(os.path.basename(in_path))
            out_path = os.path.join(out_dir, filename)
        else:
            filename, _ = os.path.splitext(os.path.abspath(in_path))
            out_path = filename
    else:
        if check_if_plist(in_path):
            out_path = "{}.yaml".format(in_path)
        else:
            print("\nERROR: File is not PLIST, JSON or YAML format.\n")
            usage()
            exit(1)
    return out_path


def main():
    """get the command line inputs if running this script directly."""
    if len(sys.argv) < 2:
        usage()
        exit(1)

    in_path = sys.argv[1]

    # auto-determine which direction the conversion should go
    if in_path.endswith(".yaml") or in_path.endswith(".yaml"):
        filetype = "yaml"
    elif in_path.endswith(".json"):
        filetype = "json"
    elif in_path.endswith(".plist"):
        filetype = "plist"
    else:
        filetype = "other"

    if filetype == "yaml" or filetype == "json":
        # allow for converting whole folders if a glob is provided
        _, glob_files = os.path.split(in_path)
        if "*" in glob_files:
            glob_files = glob.glob(in_path)
            for glob_file in glob_files:
                out_path = get_out_path(glob_file, filetype)
                if filetype == "yaml":
                    print("Processing YAML folder with globs...")
                    yaml_plist(glob_file, out_path)
                elif filetype == "json":
                    print("Processing JSON folder with globs...")
                    json_plist(glob_file, out_path)
        else:
            try:
                sys.argv[2]
            except IndexError:
                out_path = get_out_path(in_path, filetype)
            else:
                out_path = sys.argv[2]
            if filetype == "yaml":
                print("Processing yaml file...")
                if out_path == "--tidy":
                    tidy_yaml(in_path)
                else:
                    yaml_plist(in_path, out_path)
            elif filetype == "json":
                print("Processing json file...")
                json_plist(in_path, out_path)
    # allow for converting whole folders if 'YAML' or 'JSON' is in the path
    # and the path supplied is a folder
    elif os.path.isdir(in_path) and "YAML" in in_path:
        print("Processing YAML folder...")
        filetype = "yaml"
        if sys.argv[2] == "--tidy":
            print("WARNING! Processing all subfolders...\n")
            for root, dirs, files in os.walk(in_path):
                for name in files:
                    tidy_yaml(os.path.join(root, name))
                for name in dirs:
                    tidy_yaml(os.path.join(root, name))
        else:
            for in_file in os.listdir(in_path):
                in_file_path = os.path.join(in_path, in_file)
                out_path = get_out_path(in_file_path, filetype)
                yaml_plist(in_file_path, out_path)
    elif os.path.isdir(in_path) and "JSON" in in_path:
        print("Processing JSON folder...")
        filetype = "json"
        for in_file in os.listdir(in_path):
            in_file_path = os.path.join(in_path, in_file)
            out_path = get_out_path(in_file_path, filetype)
            json_plist(in_file_path, out_path)
    else:
        if check_if_plist(in_path):
            try:
                sys.argv[2]
            except IndexError:
                out_path = get_out_path(in_path, filetype)
            else:
                out_path = sys.argv[2]
            print("Processing plist file...")
            plist_yaml(in_path, out_path)
        else:
            print("\nERROR: Input File is not PLIST, JSON or YAML format.\n")
            usage()
            exit(1)


if __name__ == "__main__":
    main()
