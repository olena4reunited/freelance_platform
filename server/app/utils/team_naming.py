import random
import hashlib
import time


prefixes = ["Hyper", "Elite", "Shadow", "Quantum", "NoName", "Hype", "Chaos", "Stealth", "Underground"]

category_names = {
    "development": ["Coders", "Hackers", "Engineers", "Byte_Warriors", "Script_Lords"],
    "automation": ["Automators", "BotMasters", "Process_Hackers"],
    "design": ["Pixel_Pushers", "UI_Ninjas", "Creative_Minds"],
    "UX/UI": ["Experience_Wizards", "Interface_Gurus", "UX_Architects"],
    "writing": ["Wordsmiths", "Content_Ninjas", "Text_Hackers"],
    "marketing": ["Brand_Boosters", "Hype_Lords", "Engagement_Warriors"],
    "random shit": ["Wildcard_Crew", "Chaos_Team", "No_Rules_Gang"]
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
