import random
import string
from pathlib import Path
from typing import Annotated, Optional

import bs4
import typer

app = typer.Typer()

VERSIONING = [
    {"tag": "script", "attr": "src", "base": "/statics/js/bundle.js"},
    {"tag": "link", "attr": "href", "base": "/statics/css/bundle.css"},
]


def generate_random_string(length=10):
    """Generates a random string of specified length."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


random_string = generate_random_string()


def version_html_file(file: Path, version: str) -> None:
    soup = bs4.BeautifulSoup(file.read_text(), "html.parser")

    # Inside the head tag, find <scripts> that point to VALUES_TO_VERSION
    if soup.head is None:
        print(f"File {file} has no <head> tag")
        return

    for versioning in VERSIONING:
        for tag in soup.head.find_all(versioning["tag"]):
            if (
                isinstance(tag, bs4.Tag)
                and (attr := tag.get(versioning["attr"]))
                and isinstance(attr, str)
                and attr.startswith(versioning["base"])
            ):
                tag[versioning["attr"]] = f"{versioning['base']}?v={version}"

    # Write the modified HTML back to the file
    file.write_text(str(soup.prettify()))


@app.command()
def version_static(
    directory: Annotated[
        Path,
        typer.Argument(
            help="The directory to version static files",
            exists=True,
            file_okay=True,
            dir_okay=True,
            writable=True,
        ),
    ],
    version: Annotated[
        Optional[str],
        typer.Argument(
            help="The version to assign to the static files",
        ),
    ] = None,
):
    if version is None:
        version = generate_random_string()

    print(f"Versioning static files in {directory} with version {version}.")

    for html_file in directory.rglob("*.html"):
        print(f"Versioning {html_file}")
        version_html_file(html_file, version)

    print("Versioning completed.")


if __name__ == "__main__":
    app()
