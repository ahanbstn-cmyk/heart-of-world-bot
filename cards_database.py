"""
Heart Of World — Collectible Card Story (CCS) Database Engine
Designed by NukeCell
"THE WORLD HIDES SECRETS."

Categories:
1. 👻 PARANORMAL (Documented paranormal cases, unexplained mysteries)
2. 📻 FREQUENCY / FREKANS (Historic figures, iconic leaders, dark figures, mythology)
3. 💥 ANOMALY / ANOMALİ (World catastrophes, great disasters, reality shifts)

File Access Levels:
- 🗂️ Public File
- 📁 Classified File
- ⬛ BLACK FILE (Ultra-Secret continuation files)
"""

import json
import os

STATE_FILE = "card_state.json"

CATEGORIES = [
    ("👻 PARANORMAL", "Documented Unexplained Phenomena", 0x8e44ad),
    ("📻 FREQUENCY", "Historical Figures, Icons & Myths", 0xd35400),
    ("💥 ANOMALY", "Great Catastrophes & Reality Shifts", 0xc0392b)
]

FILE_LEVELS = [
    ("🗂️ PUBLIC FILE", "Accessible to all collectors"),
    ("📁 CLASSIFIED DOSSIER", "Requires investigator clearance"),
    ("⬛ BLACK FILE", "Top Secret • Multi-card investigation piece")
]

RARITIES = [
    ("⬛ BLACK FILE • Serialized First Edition", 0x111111),
    ("👑 Secret Dossier • Mythic", 0x9b59b6),
    ("🌟 Classified • Legendary", 0xf1c40f),
    ("🔥 Restricted • Epic", 0xe67e22),
    ("💎 Documented • Rare", 0x3498db),
    ("🛡️ Public Record • Common", 0x95a5a6)
]

SAMPLE_MYSTERIES = [
    {
        "name": "The Dyatlov Incident: Final Transmission",
        "category": "👻 PARANORMAL",
        "file_level": "⬛ BLACK FILE",
        "case_no": "HW-CASE-1959-01",
        "continuation": "Part 1 of 3 (Requires #042 & #043 to decode full Black File)",
        "lore": {
            "en": "February 1959. Nine experienced hikers perished under inexplicable circumstances on Kholat Syakhl. The tent was ripped from the inside. High levels of radiation were detected. The official file was sealed under Soviet archives until now.",
            "fr": "Février 1959. Neuf randonneurs expérimentés ont péri dans des circonstances inexplicables. La tente a été déchirée de l'intérieur. Des niveaux anormaux de radiations ont été détectés. Le dossier était scellé jusqu'à aujourd'hui.",
            "it": "Febbraio 1959. Nove escursionisti esperti morirono in circostanze inspiegabili. La tenda fu tagliata dall'interno. Furono rilevati alti livelli di radiazioni. Il fascicolo è rimasto segreto fino ad ora.",
            "de": "Februar 1959. Neun erfahrene Wanderer starben unter unerklärlichen Umständen. Das Zelt wurde von innen aufgeschlitzt. Hohe Strahlungswerte wurden gemessen.",
            "es": "Febrero de 1959. Nueve excursionistas experimentados perecieron en circunstancias inexplicables. La tienda fue rasgada desde el interior. Se detectaron altos niveles de radiación."
        }
    },
    {
        "name": "Tunguska Event: The Sky Shatterer",
        "category": "💥 ANOMALY",
        "file_level": "📁 CLASSIFIED DOSSIER",
        "case_no": "HW-CASE-1908-77",
        "continuation": "Standalone Incident Dossier",
        "lore": {
            "en": "June 1908. A colossal explosion flattened 80 million trees across 2,150 square kilometers in Siberia. No impact crater was ever discovered. Witness accounts spoke of a blinding pillar of light splitting the sky.",
            "fr": "Juin 1908. Une explosion colossale a rasé 80 millions d'arbres sur 2 150 km² en Sibérie. Aucun cratère d'impact n'a jamais été trouvé. Les témoins ont décrit un pilier de lumière aveuglant.",
            "it": "Giugno 1908. Una colossale esplosione ha raso al suolo 80 milioni di alberi in Siberia. Nessun cratere da impatto è mai stato trovato. I testimoni parlarono di una colonna di luce accecante.",
            "de": "Juni 1908. Eine gewaltige Explosion vernichtete 80 Millionen Bäume in Sibirien. Es wurde nie ein Einschlagkrater entdeckt.",
            "es": "Junio de 1908. Una colosal explosión derribó 80 millones de árboles en Siberia. Nunca se encontró ningún cráter de impacto."
        }
    },
    {
        "name": "Nikola Tesla: Wardenclyffe Frequency 369",
        "category": "📻 FREQUENCY",
        "file_level": "⬛ BLACK FILE",
        "case_no": "HW-CASE-1901-369",
        "continuation": "Part 2 of 4 (Mastery of the Universal Frequency)",
        "lore": {
            "en": "\"If you only knew the magnificence of the 3, 6 and 9, then you would have a key to the universe.\" Following Tesla's passing in Room 3327, FBI agents seized trunks of unreleased research on wireless power and scalar resonance.",
            "fr": "\"Si vous connaissiez la magnificence des chiffres 3, 6 et 9, vous auriez la clé de l'univers.\" Après sa disparition, des malles de recherches secrètes sur l'énergie sans fil ont été saisies par le FBI.",
            "it": "\"Se solo conosceste la magnificenza del 3, 6 e 9, avreste la chiave dell'universo.\" Dopo la sua morte, bauli di ricerche segrete furono confiscati.",
            "de": "„Wenn Sie nur die Pracht der 3, 6 und 9 kennen würden, hätten Sie den Schlüssel zum Universum.“ Nach Teslas Tod beschlagnahmte das FBI unveröffentlichte Forschungen.",
            "es": "\"Si supieras la magnificencia del 3, 6 y 9, tendrías la llave del universo.\" Tras su muerte, el FBI incautó baúles con investigaciones secretas."
        }
    }
]

def generate_card(card_id: int):
    # If it's one of the featured curated mysteries
    if card_id <= len(SAMPLE_MYSTERIES):
        mystery = SAMPLE_MYSTERIES[card_id - 1]
        name = mystery["name"]
        category = mystery["category"]
        file_level = mystery["file_level"]
        case_no = mystery["case_no"]
        continuation = mystery["continuation"]
        lore = mystery["lore"]
    else:
        # Procedural generation for the 600-card universe across 25 seasons
        season = ((card_id - 1) // 24) + 1
        sub_season = ((card_id - 1) // 8) + 1
        cat_info = CATEGORIES[(card_id * 3) % len(CATEGORIES)]
        category = cat_info[0]
        file_level = FILE_LEVELS[(card_id * 7) % len(FILE_LEVELS)][0]
        case_no = f"HW-S{season:02d}-SS{sub_season:02d}-#{card_id:03d}"
        
        subjects = [
            "The Roswell Debris Protocol", "The Oak Island Cipher", "The Mary Celeste Abandonment",
            "The Philadelphia Resonance", "Voynich Manuscript Page 42", "The Chernobyl Blue Flash",
            "Bermuda Triangle Flight 19", "The Taos Hum Frequency", "Hollow Earth Agartha Expedition",
            "The Antikythera Celestial Engine", "Black Knight Satellite Signal", "The Wow! Signal Origin"
        ]
        name = f"{subjects[(card_id) % len(subjects)]} (Vol. {((card_id % 3) + 1)})"
        continuation = f"Season {season}/25 • Sub-Season {sub_season}/75 (Dossier File #{card_id:03d})"
        
        lore = {
            "en": f"Case File {case_no}. Documented event classified under Heart Of World archives. Unlocks investigative lore for Season {season}. Assemble continuation cards to solve this dossier.",
            "fr": f"Dossier {case_no}. Événement classifié sous les archives Heart Of World. Débloque des indices pour la Saison {season}.",
            "it": f"Fascicolo {case_no}. Evento documentato classificato negli archivi Heart Of World. Sblocca indizi per la Stagione {season}.",
            "de": f"Fallakte {case_no}. Dokumentiertes Ereignis, klassifiziert unter Heart Of World-Archiven.",
            "es": f"Archivo de Caso {case_no}. Evento documentado clasificado bajo los archivos de Heart Of World."
        }

    # Rarity calculation
    if "BLACK FILE" in file_level or card_id == 1 or card_id % 50 == 0:
        rarity_info = RARITIES[0]
    elif card_id % 20 == 0:
        rarity_info = RARITIES[1]
    elif card_id % 10 == 0:
        rarity_info = RARITIES[2]
    elif card_id % 5 == 0:
        rarity_info = RARITIES[3]
    elif card_id % 2 == 0:
        rarity_info = RARITIES[4]
    else:
        rarity_info = RARITIES[5]

    season_no = ((card_id - 1) // 24) + 1
    image_url = f"https://picsum.photos/seed/heartofworld_mystery_{card_id}/600/850"

    return {
        "id": card_id,
        "name": name,
        "category": category,
        "file_level": file_level,
        "case_no": case_no,
        "rarity": rarity_info[0],
        "color": rarity_info[1],
        "continuation": continuation,
        "season": f"Season {season_no}/25 (75 Sub-Seasons)",
        "edition": f"First Edition #{card_id:03d}/600 • NukeCell CCS",
        "lore": lore,
        "image_url": image_url
    }

def get_current_card_index() -> int:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("current_card_id", 1)
        except Exception:
            return 1
    return 1

def advance_card_index() -> int:
    current = get_current_card_index()
    next_idx = current + 1
    if next_idx > 600:
        next_idx = 1
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_card_id": next_idx}, f, indent=2)
    return current

def set_card_index(index: int):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_card_id": index}, f, indent=2)
