from pathlib import Path
from typing import Annotated

import bs4
import typer

app = typer.Typer()

VALUES_TO_VERSION = {
    "/statics/css/bundle.css",
    "/statics/js/bundle.js",
}

VERSIONING = [
    {"tag": "script", "attr": "src", "base": "/statics/js/bundle.js"},
    {"tag": "link", "attr": "href", "base": "/statics/css/bundle.css"},
]


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
        str,
        typer.Argument(
            help="The version to assign to the static files",
        ),
    ],
):
    print(f"Versioning static files in {directory} with version {version}.")

    for html_file in directory.rglob("*.html"):
        print(f"Versioning {html_file}")
        version_html_file(html_file, version)


if __name__ == "__main__":
    app()
