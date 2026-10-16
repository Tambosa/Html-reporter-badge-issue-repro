
# Stale badge links in html-reporter 11.17.2

This standalone example generates a report with two synthetic test results.
It downloads unmodified static assets from the official npm packages
`html-reporter@11.17.2` and `@gemini-testing/sql.js@3.0.0`.
No application, test runner, private service or Node.js installation is needed.

Requirements: Python 3.11+, curl, internet access, and a browser.

```bash
python3 reproduce.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory report

```

Open <http://127.0.0.1:8765/new-ui.html>.

1. Click the `chrome` result below `Test A`. Its `External link` badge points to `https://example.com/a`.
2. Click the `chrome` result below `Test B` without reloading. Its badge still points to `/a`, although `expectedBadgeUrl` in Metadata shows `/b`.
3. Reload the page while Test B is selected. The badge now points to `/b`.
4. Switch back to Test A. The badge still points to `/b`.

Inspect the badge's `href` or use the browser's Copy Link Address action.
Do not click the similarly named URL in Metadata: that URL updates correctly.

Both results have an empty `suiteUrl`, omit `metaInfo.url`, and use the same
`baseHost`. The `attachments` values contain distinct, correct badge URLs.
The report uses separate test paths, `Example suite / Test A` and
`Example suite / Test B`, with the same browser ID `chrome`.

The fixture writes the reporter's existing SQLite schema directly to isolate
the report UI; it does not run testplane or modify the reporter's JavaScript.

Verified behavior on the released 11.17.2 client:

| Action | Selected test | Expected badge URL | Actual badge URL |
| --- | --- | --- | --- |
| Open A | A | `/a` | `/a` |
| Switch to B | B | `/b` | `/a` |
| Reload B | B | `/b` | `/b` |
| Switch to A | A | `/a` | `/b` |

