import re
from typing import Optional

COUNTRY_NAME_TO_ID = {
    "nigeria": "NG", "ghana": "GH", "kenya": "KE", "angola": "AO",
    "benin": "BJ", "south africa": "ZA", "ethiopia": "ET", "tanzania": "TZ",
    "uganda": "UG", "senegal": "SN", "cameroon": "CM", "ivory coast": "CI",
    "cote d'ivoire": "CI", "côte d'ivoire": "CI", "zimbabwe": "ZW",
    "zambia": "ZM", "mozambique": "MZ", "madagascar": "MG", "mali": "ML",
    "niger": "NE", "burkina faso": "BF", "guinea": "GN", "rwanda": "RW",
    "somalia": "SO", "chad": "TD", "south sudan": "SS", "togo": "TG",
    "sierra leone": "SL", "liberia": "LR", "central african republic": "CF",
    "mauritania": "MR", "eritrea": "ER", "gambia": "GM", "botswana": "BW",
    "namibia": "NA", "gabon": "GA", "lesotho": "LS", "guinea-bissau": "GW",
    "equatorial guinea": "GQ", "mauritius": "MU", "djibouti": "DJ",
    "comoros": "KM", "cape verde": "CV", "seychelles": "SC", "egypt": "EG",
    "morocco": "MA", "algeria": "DZ", "tunisia": "TN", "libya": "LY",
    "sudan": "SD", "congo": "CG", "democratic republic of congo": "CD",
    "dr congo": "CD", "drc": "CD", "malawi": "MW", "burundi": "BI",
    "sao tome and principe": "ST", "eswatini": "SZ", "swaziland": "SZ",
    "cabo verde": "CV",
    "usa": "US", "united states": "US", "america": "US",
    "uk": "GB", "united kingdom": "GB", "britain": "GB", "england": "GB",
    "france": "FR", "germany": "DE", "italy": "IT", "spain": "ES",
    "portugal": "PT", "brazil": "BR", "india": "IN", "china": "CN",
    "japan": "JP", "canada": "CA", "australia": "AU", "mexico": "MX",
    "argentina": "AR", "colombia": "CO", "pakistan": "PK",
    "indonesia": "ID", "russia": "RU", "turkey": "TR",
}

AGE_GROUP_WORDS = {
    "child": "child", "children": "child", "kid": "child", "kids": "child",
    "teenager": "teenager", "teenagers": "teenager",
    "teen": "teenager", "teens": "teenager", "adolescent": "teenager",
    "adult": "adult", "adults": "adult",
    "senior": "senior", "seniors": "senior",
    "elderly": "senior", "elder": "senior",
}


def parse_natural_language(query: str) -> Optional[dict]:
    if not query or not query.strip():
        return None

    q = query.lower().strip()
    filters = {}

    has_male = bool(re.search(r"\b(male|males|man|men)\b", q))
    has_female = bool(re.search(r"\b(female|females|woman|women)\b", q))

    if has_male and not has_female:
        filters["gender"] = "male"
    elif has_female and not has_male:
        filters["gender"] = "female"

    if re.search(r"\byoung\b", q):
        filters["min_age"] = 16
        filters["max_age"] = 24

    for word, group in AGE_GROUP_WORDS.items():
        if re.search(rf"\b{re.escape(word)}\b", q):
            filters["age_group"] = group
            break

    above_match = re.search(
        r"\b(?:above|over|older than|greater than|at least)\s+(\d+)", q
    )
    if above_match:
        filters["min_age"] = int(above_match.group(1))

    below_match = re.search(
        r"\b(?:below|under|younger than|less than|at most)\s+(\d+)", q
    )
    if below_match:
        filters["max_age"] = int(below_match.group(1))

    from_match = re.search(
        r"\bfrom\s+(.+?)(?:\s*$|\s+(?:above|below|over|under|aged|who|with|between|and\s+\d))",
        q,
    )
    if from_match:
        possible_country = from_match.group(1).strip()
        country_id = _resolve_country(possible_country)
        if country_id:
            filters["country_id"] = country_id

    if not filters:
        return None

    return filters


def _resolve_country(text: str) -> Optional[str]:
    text = text.strip().lower()
    for country_name, code in sorted(
        COUNTRY_NAME_TO_ID.items(), key=lambda x: -len(x[0])
    ):
        if text == country_name or text.startswith(country_name):
            return code
    return None
