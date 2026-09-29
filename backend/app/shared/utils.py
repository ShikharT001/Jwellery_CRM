"""
Shared utility functions used across the application.
"""

import math
import re
import uuid
from typing import Any


def generate_uuid() -> str:
    """Generate a new UUID v4 string."""
    return str(uuid.uuid4())


def slugify(text: str) -> str:
    """
    Convert a string to a URL-safe slug.

    Example: "Golden Star Jewellers" -> "golden-star-jewellers"
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate the total number of pages for pagination."""
    if total == 0:
        return 1
    return math.ceil(total / page_size)


def mask_email(email: str) -> str:
    """
    Mask an email for display in logs (privacy protection).

    Example: "user@example.com" -> "us**@example.com"
    """
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    masked_local = local[:2] + "*" * max(0, len(local) - 2)
    return f"{masked_local}@{domain}"
