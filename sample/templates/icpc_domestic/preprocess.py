import re
import sys


def preprocess(markdown_lines):
    md_data = ""
    first_line = True
    for line in markdown_lines:
        if first_line:
            first_line = False
            while line[0] != "#":
                line = line[1:]

        if line.startswith("### Problem Statement"):
            continue

        md_data += line
    md_data += "\n"

    md_data = re.sub("’", "'", md_data)
    md_data = re.sub("”", '"', md_data)
    md_data = re.sub(r"\\<", r"&lt;", md_data)
    md_data = re.sub(r"\\>", r"&gt;", md_data)
    return md_data


def main():
    markdown_lines = sys.stdin.readlines()
    print(preprocess(markdown_lines))


if __name__ == "__main__":
    main()
