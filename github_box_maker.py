import argparse
from os import getenv
from pathlib import Path
from string import Template
from sys import exit, stderr

import requests

TEMPLATE_FILE = Path(__file__).with_name("template.html")
assert TEMPLATE_FILE.is_file()
TEMPLATE = Template(TEMPLATE_FILE.read_text())

GITHUB_TOKEN = getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("Please set GITHUB_TOKEN", file=stderr)
    exit(1)


def main():
    parser = argparse.ArgumentParser()

    # Add arguments for input and output files
    parser.add_argument("input_file", type=str, help="The path to the input text file.")
    parser.add_argument(
        "output_file", type=str, help="The path to the output html file."
    )

    args = parser.parse_args()

    input_file = Path(args.input_file)

    if not input_file.is_file():
        raise RuntimeError(f"{input_file} is not a file")

    output_file = Path(args.output_file)

    md = input_file.read_text()
    html = make_github_box(md)
    output_file.write_text(html)


def make_github_box(text: str) -> str:
    return apply_style(md_to_html(text))


def apply_style(html: str) -> str:
    return TEMPLATE.substitute({"content": html})


def md_to_html(md: str) -> str:
    headers = {
        "Authorization": GITHUB_TOKEN,
        "X-GitHub-Api-Version": "2022-11-28",
    }

    data = {"text": md}

    response = requests.post(
        "https://api.github.com/markdown", headers=headers, json=data
    )

    if response.status_code != 200:
        raise RuntimeError(response.text)

    return response.text


if __name__ == "__main__":
    main()
