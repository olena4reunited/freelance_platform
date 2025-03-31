import random
import hashlib
import time


prefixes = ["Hyper", "Elite", "Shadow", "Quantum", "NoName", "Hype", "Chaos", "Stealth", "Underground"]

category_names = {
    "development": ["Coders", "Hackers", "Engineers", "Byte Warriors", "Script Lords"],
    "automation": ["Automators", "BotMasters", "Process Hackers"],
    "design": ["Pixel Pushers", "UI Ninjas", "Creative Minds"],
    "UX/UI": ["Experience Wizards", "Interface Gurus", "UX Architects"],
    "writing": ["Wordsmiths", "Content Ninjas", "Text Hackers"],
    "marketing": ["Brand Boosters", "Hype Lords", "Engagement Warriors"],
    "random shit": ["Wildcard Crew", "Chaos Team", "No Rules Gang"]
}


def generate_numeric_identifier():
    raw_string = str(time.time()) + str(random.randint(100, 999))
    return hashlib.md5(raw_string.encode()).hexdigest()[:3].upper()


def generate_team_name(tags: list[str]):
    prefix = random.choice(prefixes)
    
    selected_categories = [category_names[tag] for tag in tags if tag in category_names]
    
    if not selected_categories:
        selected_categories = [category_names["random shit"]]
    
    category_name = random.choice(random.choice(selected_categories))
    numeric_id = generate_numeric_identifier()

    return f"{prefix}_{category_name}_{numeric_id}"
