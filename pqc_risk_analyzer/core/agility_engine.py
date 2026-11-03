def calculate_agility_score(no_hardcoded, modular, central, docs, key_mgmt, auto_val):
    """
    Calculates agility score out of 100 based on 6 factors (0-5 scale each).
    """
    total_points = no_hardcoded + modular + central + docs + key_mgmt + auto_val
    agility = round((total_points / 30.0) * 100.0, 2)
    return agility