from typing import Any
from jinja2 import Template

def render_template(template_str: str, context: dict[str, Any]) -> str:
    return Template(template_str).render(context)
