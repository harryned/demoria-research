"""
Run this after editing dhi_sowhat.html to update dhi_combined.html.
Usage: python3 rebuild_sowhat.py

IMPORTANT: Edit dhi_sowhat.html in a CODE EDITOR only (BBEdit, VSCode, etc.).
Do NOT use TextEdit — it silently rewrites HTML into its own broken format on save.
"""
import base64, re

FILES = {
    "source":   "dhi_sowhat.html",
    "combined": "dhi_combined.html",
}

with open(FILES["source"], "r", encoding="utf-8") as f:
    html = f.read()

new_b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")

with open(FILES["combined"], "r", encoding="utf-8") as f:
    combined = f.read()

pattern = r'(<textarea id="d-sowhat"\s+style="display:none">)(.*?)(</textarea>)'
m = re.search(pattern, combined, re.DOTALL)
if not m:
    raise RuntimeError("d-sowhat textarea not found in dhi_combined.html")

combined = combined[:m.start(2)] + new_b64 + combined[m.end(2):]

with open(FILES["combined"], "w", encoding="utf-8") as f:
    f.write(combined)

print("Done — dhi_combined.html updated from dhi_sowhat.html")
