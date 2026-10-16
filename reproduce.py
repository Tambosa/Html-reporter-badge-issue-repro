"""Generate a two-result report using unmodified html-reporter 11.17.2 assets.

Requires Python 3.11+, curl and internet access. No Node.js or test runner is needed.
Run: python3 reproduce.py
Then: python3 -m http.server 8765 --bind 127.0.0.1 --directory report
Open: http://127.0.0.1:8765/new-ui.html
"""
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "report"
REPORT.mkdir(exist_ok=True)


def copy_package_files(url, prefix, suffixes):
    archive = subprocess.check_output(
        ["curl", "--fail", "--location", "--silent", "--show-error", url])
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
        for member in package.getmembers():
            if not member.isfile() or not member.name.startswith(prefix):
                continue
            relative = member.name[len(prefix):]
            if ".." in Path(relative).parts or not relative.endswith(suffixes):
                continue
            if relative == "new-ui-report.html":
                relative = "new-ui.html"
            destination = REPORT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(package.extractfile(member).read())


copy_package_files(
    "https://registry.npmjs.org/html-reporter/-/html-reporter-11.17.2.tgz",
    "package/build/lib/static/", (".js", ".css", ".html", ".png", ".svg"))
copy_package_files(
    "https://registry.npmjs.org/@gemini-testing/sql.js/-/sql.js-3.0.0.tgz",
    "package/dist/", ("sql-wasm.js", "sql-wasm.wasm"))

config = {
    "uiMode": "new", "defaultView": "all", "diffMode": "3-up",
    "baseHost": "", "errorPatterns": [], "metaInfoBaseUrls": {},
    "customScripts": [], "pluginsEnabled": False, "plugins": [],
    "yandexMetrika": {"enabled": False},
    "staticImageAccepter": {"enabled": False},
}
data = {"skips": [], "config": config, "apiValues": {},
        "timestamp": 1700000000000, "date": "2023-11-14T22:13:20Z"}
(REPORT / "data.js").write_text("var data = " + json.dumps(data) + ";\n")
(REPORT / "databaseUrls.json").write_text(
    json.dumps({"dbUrls": ["sqlite.db"], "jsonUrls": []}))

columns = [
    ("suitePath", "TEXT"), ("suiteName", "TEXT"), ("name", "TEXT"),
    ("suiteUrl", "TEXT"), ("metaInfo", "TEXT"), ("history", "TEXT"),
    ("description", "TEXT"), ("error", "TEXT"), ("skipReason", "TEXT"),
    ("imagesInfo", "TEXT"), ("screenshot", "INT"), ("multipleTabs", "INT"),
    ("status", "TEXT"), ("timestamp", "INT"), ("duration", "INT"),
    ("attachments", "TEXT"),
]
with sqlite3.connect(REPORT / "sqlite.db") as db:
    db.execute("DROP TABLE IF EXISTS suites")
    db.execute("DROP TABLE IF EXISTS version")
    db.execute("CREATE TABLE version (version_number INT)")
    db.execute("INSERT INTO version VALUES (1)")
    db.execute("CREATE TABLE suites (" + ", ".join(
        name + " " + kind for name, kind in columns) + ")")
    for index, case in enumerate(("A", "B")):
        url = "https://example.com/" + case.lower()
        row = [json.dumps(["Example suite", "Test " + case]), "Test " + case,
               "chrome", "", json.dumps({"expectedBadgeUrl": url}), "[]",
               "", None, None, "[]", 0, 0, "success",
               1700000000000 + index, 100,
               json.dumps([{"type": 1, "list": [
                   {"title": "External link", "url": url}]}])]
        db.execute("INSERT INTO suites VALUES (" + ",".join(
            "?" for _ in columns) + ")", row)
print("Created report with Test A -> example.com/a and Test B -> example.com/b")
