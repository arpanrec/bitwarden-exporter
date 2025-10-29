#!/usr/bin/env python

import os

import jinja2

# Read the environment variable
version_next = os.getenv("README_VERSION_NEXT", "VERSION")

# Read the template
with open(".github/files/templates/README.md", "r", encoding="utf-8") as f:
    template = jinja2.Template(f.read())

# Render the template with the version
rendered = template.render(README_VERSION_NEXT=version_next)

# Write to README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(rendered)

print(f"README.md generated successfully with version: {version_next}")
