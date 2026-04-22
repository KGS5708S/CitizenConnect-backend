def classify_complaint(text: str):
    text = text.lower()

    rules = [

    # 1️⃣ MEDICAL EMERGENCY (CRITICAL)
    {
        "keywords": [
            "hospital", "health", "ambulance", "medical",
            "emergency", "injury", "unconscious", "bleeding"
        ],
        "department": "Health Services",
        "category": "Medical Emergency",
        "priority": "Critical"
    },

    # 2️⃣ PUBLIC SAFETY / POLICE (CRITICAL)
    {
        "keywords": [
            "theft", "crime", "attack", "harassment",
            "assault", "robbery", "violence", "fight"
        ],
        "department": "Police",
        "category": "Public Safety",
        "priority": "Critical"
    },
    # 4️⃣ ROAD & INFRASTRUCTURE (HIGH)
    {
        "keywords": [
            "pothole", "road damage", "broken road",
            "street damage", "bridge", "crack", "uneven road"
        ],
        "department": "Roads & Infrastructure",
        "category": "Road Damage",
        "priority": "High"
    },

    # 5️⃣ ELECTRICITY ISSUES (HIGH)
    {
        "keywords": [
            "electricity", "power cut", "power failure",
            "current", "transformer", "voltage",
            "electric pole", "wire"
        ],
        "department": "Electricity Board",
        "category": "Power Failure",
        "priority": "High"
    },

    # 6️⃣ WATER SUPPLY & DRAINAGE (MEDIUM)
    {
        "keywords": [
            "water leak", "pipe burst", "drain",
            "sewage", "overflow", "dirty water",
            "water supply", "no water"
        ],
        "department": "Water Supply",
        "category": "Water Leakage",
        "priority": "Medium"
    },

    # 7️⃣ SANITATION & WASTE (MEDIUM)
    {
        "keywords": [
            "garbage", "waste", "trash",
            "sanitation", "dump", "bad smell",
            "unclean", "overflowing bin"
        ],
        "department": "Sanitation",
        "category": "Waste Management",
        "priority": "Medium"
    },

    # 8️⃣ FALLBACK (LOW)
    {
        "keywords": [],
        "department": "General Administration",
        "category": "General Grievance",
        "priority": "Low"
    }
]

    for rule in rules:
        if any(word in text for word in rule["keywords"]):
            return {
                "department": rule["department"],
                "category": rule["category"],
                "priority": rule["priority"]
            }

    # fallback
    return {
        "department": "General Administration",
        "category": "General Grievance",
        "priority": "Low"
    }

def simple_ai_response(question: str):
    """
    Placeholder AI logic.
    Replace later with IBM Granite / OpenAI / HuggingFace.
    """
    return f"AI Response: Your question '{question}' has been received and will be processed."


def analyze_sentiment(text: str):
    """
    Very simple sentiment logic (for now).
    Replace with ML model later.
    """
    text = text.lower()

    if any(word in text for word in ["good", "great", "excellent", "happy"]):
        return {"sentiment": "positive", "score": 0.9}
    elif any(word in text for word in ["bad", "poor", "delay", "angry"]):
        return {"sentiment": "negative", "score": -0.8}
    else:
        return {"sentiment": "neutral", "score": 0.0}
