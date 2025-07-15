import string
import random

def generate_slug(length: int = 7) -> str:
    """Generate a random slug."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))
