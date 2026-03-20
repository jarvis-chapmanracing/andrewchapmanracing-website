#!/usr/bin/env python3
"""Generate a simple HTML file that renders a centered square."""
from pathlib import Path

html = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Square Render</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      background: #0f172a;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .square {
      width: 220px;
      height: 220px;
      background: linear-gradient(135deg, #38bdf8, #0ea5e9);
      border-radius: 20px;
      box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
    }
  </style>
</head>
<body>
  <div class=\"square\"></div>
</body>
</html>
"""

output_path = Path("output/square.html")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(html, encoding="utf-8")
print(f"Wrote square HTML to {output_path.resolve()}")
