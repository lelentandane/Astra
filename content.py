"""Interpretation content, seeded into the database on startup.

Each entry has a keyword (a short label), a sentence of text, and optional
topics. Readings are assembled from these pieces by interpret.py, so the
meanings can be edited here without touching any logic.
"""

TOPICS = [
    "Identity", "Emotions", "Relationships", "Career", "Creativity",
    "Communication", "Home", "Money", "Spirituality", "Growth", "Transformation",
]

# kind "body": what the planet or point represents.
BODIES = {
    "Sun": ("core identity and vitality",
            "The Sun is your core self: what you are here to express, where you shine, and what makes you feel most alive.",
            ["Identity", "Creativity"]),
    "Moon": ("emotional needs and instincts",
             "The Moon is your inner weather: what makes you feel safe, how you respond to feelings, and what you need to feel at home in yourself.",
             ["Emotions", "Home"]),
    "Mercury": ("mind and communication",
                "Mercury is how you think, learn, speak, and make sense of the world around you.",
                ["Communication"]),
    "Venus": ("love, beauty and values",
              "Venus is how you love, what you find beautiful, and what you value in relationships and in life.",
              ["Relationships", "Creativity", "Money"]),
    "Mars": ("drive and action",
             "Mars is your drive: how you go after what you want, handle conflict, and use your energy.",
             ["Identity", "Career"]),
    "Jupiter": ("growth and meaning",
                "Jupiter is where life tends to expand: your optimism, your beliefs, and the places you grow through generosity and learning.",
                ["Growth", "Spirituality"]),
    "Saturn": ("structure and mastery",
               "Saturn is where you build structure and earn mastery through patience, responsibility, and time.",
               ["Career", "Growth"]),
    "Uranus": ("change and originality",
               "Uranus is where you break from convention: your need for freedom, sudden change, and an original way of doing things.",
               ["Identity", "Transformation"]),
    "Neptune": ("imagination and intuition",
                "Neptune is your imagination and intuition, the place where boundaries soften and ideals, dreams, and compassion live.",
                ["Spirituality", "Creativity"]),
    "Pluto": ("depth and transformation",
              "Pluto is where you meet intensity and rebirth: what you release, rebuild, and reclaim at a deep level.",
              ["Transformation"]),
    "North Node": ("direction of growth",
                   "The North Node points toward growth: the qualities and experiences you are learning to move toward.",
                   ["Growth"]),
    "Ascendant": ("approach and first impression",
                  "The Ascendant is how you meet the world: your first impression, your approach to new situations, and the doorway into your chart.",
                  ["Identity"]),
}

# kind "sign": the style or manner. Signs carry no topics.
SIGNS = {
    "Aries": ("bold and direct", "This is expressed in a bold, direct, start-first way, with courage and a taste for beginnings."),
    "Taurus": ("steady and sensual", "This is expressed in a steady, sensual, patient way, valuing comfort, loyalty, and things that last."),
    "Gemini": ("curious and quick", "This is expressed in a curious, quick, talkative way, drawn to variety, ideas, and connection."),
    "Cancer": ("protective and feeling-led", "This is expressed in a protective, feeling-led way, with deep loyalty to home, family, and the people you care for."),
    "Leo": ("warm and expressive", "This is expressed in a warm, generous, expressive way, with a need to create, be seen, and give from the heart."),
    "Virgo": ("precise and helpful", "This is expressed in a careful, practical, service-minded way, with an eye for detail and improvement."),
    "Libra": ("balanced and relational", "This is expressed in a graceful, fair-minded way, seeking harmony, partnership, and beauty."),
    "Scorpio": ("intense and private", "This is expressed in an intense, private, perceptive way, drawn to depth, truth, and emotional honesty."),
    "Sagittarius": ("free and exploratory", "This is expressed in an adventurous, honest, big-picture way, with a hunger for freedom and meaning."),
    "Capricorn": ("ambitious and disciplined", "This is expressed in a disciplined, ambitious, long-term way, with respect for craft, structure, and achievement."),
    "Aquarius": ("independent and inventive", "This is expressed in an independent, inventive, future-minded way, with loyalty to ideas and community."),
    "Pisces": ("dreamy and compassionate", "This is expressed in an imaginative, compassionate, porous way, guided by intuition and feeling."),
}

# kind "house": the area of life. Keys are the house numbers as text.
HOUSES = {
    "1": ("self and appearance", "This shows up in how you present yourself and begin things.", ["Identity"]),
    "2": ("money and values", "This shows up in your money, your possessions, and what you value.", ["Money"]),
    "3": ("communication and learning", "This shows up in everyday communication, learning, siblings, and your local surroundings.", ["Communication"]),
    "4": ("home and roots", "This shows up in your home, your family, and your sense of roots.", ["Home", "Emotions"]),
    "5": ("creativity and romance", "This shows up in creativity, romance, play, and self-expression.", ["Creativity", "Relationships"]),
    "6": ("work and routine", "This shows up in daily work, routines, and the way you look after your health.", ["Career"]),
    "7": ("partnership", "This shows up in committed partnerships and one-to-one relationships.", ["Relationships"]),
    "8": ("shared resources and change", "This shows up in intimacy, shared resources, and deep change.", ["Transformation", "Money"]),
    "9": ("belief and exploration", "This shows up in higher learning, travel, belief, and the search for meaning.", ["Spirituality", "Growth"]),
    "10": ("career and reputation", "This shows up in your career, your public role, and your reputation.", ["Career"]),
    "11": ("community and hopes", "This shows up in friendships, groups, and your long-term hopes.", ["Growth", "Relationships"]),
    "12": ("the inner world", "This shows up in your inner world: rest, solitude, intuition, and what happens out of sight.", ["Spirituality", "Emotions"]),
}

# kind "aspect": {a} and {b} are replaced with the two body names.
ASPECTS = {
    "Conjunction": ("blends and intensifies", "{a} and {b} are fused, so their qualities blend and work as one force."),
    "Sextile": ("supportive opportunity", "{a} and {b} support each other when you act on the opening they offer."),
    "Square": ("friction that drives growth", "{a} and {b} pull in different directions, and the friction pushes you to grow."),
    "Trine": ("natural flow", "{a} and {b} flow together easily, a natural talent that can be simple to overlook."),
    "Opposition": ("tension and balance", "{a} and {b} sit across from each other, asking you to hold both and find a balance."),
}


def all_entries():
    """Flat list of dicts ready to insert: kind, key, keyword, text, topics."""
    entries = []
    for key, (keyword, text, topics) in BODIES.items():
        entries.append({"kind": "body", "key": key, "keyword": keyword, "text": text, "topics": topics})
    for key, (keyword, text) in SIGNS.items():
        entries.append({"kind": "sign", "key": key, "keyword": keyword, "text": text, "topics": []})
    for key, (keyword, text, topics) in HOUSES.items():
        entries.append({"kind": "house", "key": key, "keyword": keyword, "text": text, "topics": topics})
    for key, (keyword, text) in ASPECTS.items():
        entries.append({"kind": "aspect", "key": key, "keyword": keyword, "text": text, "topics": []})
    return entries
