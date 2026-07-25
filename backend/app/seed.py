"""Synthetic data generator for KSP Crime Intelligence demo.

Generates ~15-20 realistic investigation scenarios with interconnected
records across FIR, intelligence, and forensic layers.  Run directly:

    python -m app.seed

Or import and call ``seed_database()`` from application code.
"""

from __future__ import annotations

import asyncio
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory

# ── Karnataka geography constants ──────────────────────────────────────────

KARNATAKA_STATE_ID = 29

DISTRICTS = [
    (1, "Bengaluru Urban"), (2, "Bengaluru Rural"), (3, "Mysuru"),
    (4, "Mangaluru"), (5, "Hubballi-Dharwad"), (6, "Belagavi"),
    (7, "Kalaburagi"), (8, "Davangere"), (9, "Ballari"),
    (10, "Tumakuru"), (11, "Shivamogga"), (12, "Raichur"),
    (13, "Hassan"), (14, "Mandya"), (15, "Udupi"),
]

UNIT_TYPES = [
    (1, "Police Station", "City", 1),
    (2, "Circle Office", "City", 2),
    (3, "Sub Division", "District", 3),
    (4, "District SP Office", "District", 4),
    (5, "Range IGP Office", "State", 5),
    (6, "Cyber Crime Station", "City", 1),
]

POLICE_STATIONS: list[tuple[int, str, int]] = [
    (101, "Cubbon Park PS", 1), (102, "Whitefield PS", 1), (103, "Koramangala PS", 1),
    (104, "HSR Layout PS", 1), (105, "Indiranagar PS", 1), (106, "Electronic City PS", 1),
    (107, "Yelahanka PS", 1), (108, "Jayanagar PS", 1), (109, "JP Nagar PS", 1),
    (110, "Marathahalli PS", 1),
    (201, "Devanahalli PS", 2), (202, "Nelamangala PS", 2),
    (301, "Nazarbad PS", 3), (302, "Jayalakshmipuram PS", 3),
    (303, "Kuvempunagar PS", 3), (304, "VV Puram PS", 3),
    (401, "Mangaluru North PS", 4), (402, "Mangaluru South PS", 4),
    (403, "Surathkal PS", 4),
    (501, "Hubballi PS", 5), (502, "Dharwad PS", 5),
    (601, "Belagavi City PS", 6), (602, "Khanapur PS", 6),
    (701, "Kalaburagi City PS", 7), (702, "Sedam PS", 7),
    (801, "Davangere City PS", 8),
    (901, "Ballari City PS", 9),
    (1001, "Tumakuru City PS", 10),
    (1101, "Shivamogga City PS", 11),
    (1201, "Raichur City PS", 12),
    (1501, "Cyber Crime PS", 1),
]

RANKS = [
    (1, "Director General of Police", 1),
    (2, "Additional Director General", 2),
    (3, "Inspector General", 3),
    (4, "Deputy Inspector General", 4),
    (5, "Superintendent of Police", 5),
    (6, "Deputy Superintendent of Police", 6),
    (7, "Inspector", 7),
    (8, "Sub Inspector", 8),
    (9, "Assistant Sub Inspector", 9),
    (10, "Head Constable", 10),
    (11, "Constable", 11),
]

DESIGNATIONS = [
    (1, "Station House Officer"), (2, "Investigating Officer"),
    (3, "Circle Inspector"), (4, "Deputy SP"),
    (5, "Additional SP"), (6, "SP"),
    (7, "Beat Constable"), (8, "Writer Constable"),
]

CASE_CATEGORIES = [
    (1, "FIR"), (2, "NCR"), (3, "UDR"),
]

GRAVITY_OFFENCES = [
    (1, "Heinous"), (2, "Non-Heinous"), (3, "IPC Special"),
]

CASE_STATUSES = [
    (1, "Under Investigation"), (2, "Chargesheeted"),
    (3, "Undetected"), (4, "Final Report Filed"),
    (5, "Convicted"), (6, "Acquitted"),
    (7, "Pending Trial"), (8, "Closed"),
]

CRIME_HEADS = [
    (1, "Murder"), (2, "Robbery"), (3, "Theft"),
    (4, "Fraud"), (5, "Cybercrime"), (6, "Narcotics"),
    (7, "Kidnapping"), (8, "Assault"),
    (9, "Sexual Offences"), (10, "Property Crime"),
    (11, "Domestic Violence"), (12, "Missing Persons"),
    (13, "Economic Offences"), (14, "Arms Act"),
    (15, "Motor Vehicle Theft"),
]

CRIME_SUB_HEADS: list[tuple[int, int, str, int]] = [
    (1, 1, "Murder with intent", 1),
    (2, 1, "Culpable homicide", 2),
    (3, 2, "Armed robbery", 1),
    (4, 2, "Highway robbery", 2),
    (5, 3, "House breaking theft", 1),
    (6, 3, "Pickpocketing", 2),
    (7, 3, "Vehicle theft", 3),
    (8, 4, "Cheating", 1),
    (9, 4, "Forgery", 2),
    (10, 4, "Criminal breach of trust", 3),
    (11, 5, "Online fraud", 1),
    (12, 5, "Identity theft", 2),
    (13, 5, "Hacking", 3),
    (14, 5, "Cyber stalking", 4),
    (15, 6, "NDPS possession", 1),
    (16, 6, "Drug trafficking", 2),
    (17, 7, "Kidnapping for ransom", 1),
    (18, 7, "Abduction", 2),
    (19, 8, "Grievous hurt", 1),
    (20, 8, "Simple hurt", 2),
    (21, 9, "POCSO", 1),
    (22, 10, "Land grab", 1),
    (23, 11, "Dowry harassment", 1),
    (24, 12, "Missing person", 1),
    (25, 13, "Money laundering", 1),
    (26, 14, "Illegal arms possession", 1),
    (27, 15, "Two-wheeler theft", 1),
    (28, 15, "Four-wheeler theft", 2),
]

RELIGIONS = [(1, "Hindu"), (2, "Muslim"), (3, "Christian"), (4, "Jain"), (5, "Buddhist"), (6, "Sikh")]
CASTES = [(1, "General"), (2, "OBC"), (3, "SC"), (4, "ST")]
OCCUPATIONS = [
    (1, "Agriculture"), (2, "Business"), (3, "Government Service"),
    (4, "Private Service"), (5, "Student"), (6, "Unemployed"),
    (7, "Labourer"), (8, "Professional"), (9, "Retired"), (10, "Homemaker"),
]

COURTS: list[tuple[int, str, int, int]] = [
    (1, "1st ACMM Court Bengaluru", 1, KARNATAKA_STATE_ID),
    (2, "2nd ACMM Court Bengaluru", 1, KARNATAKA_STATE_ID),
    (3, "Sessions Court Bengaluru", 1, KARNATAKA_STATE_ID),
    (4, "District Court Mysuru", 3, KARNATAKA_STATE_ID),
    (5, "District Court Mangaluru", 4, KARNATAKA_STATE_ID),
    (6, "District Court Hubballi", 5, KARNATAKA_STATE_ID),
    (7, "District Court Belagavi", 6, KARNATAKA_STATE_ID),
    (8, "District Court Kalaburagi", 7, KARNATAKA_STATE_ID),
    (9, "High Court of Karnataka", 1, KARNATAKA_STATE_ID),
    (10, "Fast Track Court Bengaluru", 1, KARNATAKA_STATE_ID),
]

ACTS = [
    ("IPC", "Indian Penal Code 1860", "IPC"),
    ("CRPC", "Code of Criminal Procedure 1973", "CrPC"),
    ("BNS", "Bharatiya Nyaya Sanhita 2023", "BNS"),
    ("BNSS", "Bharatiya Nagarik Suraksha Sanhita 2023", "BNSS"),
    ("BSA", "Bharatiya Sakshya Adhiniyam 2023", "BSA"),
    ("NDPS", "Narcotic Drugs and Psychotropic Substances Act 1985", "NDPS"),
    ("POCSO", "Protection of Children from Sexual Offences Act 2012", "POCSO"),
    ("ITA", "Information Technology Act 2000", "IT Act"),
    ("ARMS", "Arms Act 1959", "Arms"),
    ("DVA", "Protection of Women from Domestic Violence Act 2005", "DVA"),
]

SECTIONS = [
    ("IPC302", "IPC", "302 - Murder"),
    ("IPC304", "IPC", "304 - Culpable homicide not amounting to murder"),
    ("IPC376", "IPC", "376 - Rape"),
    ("IPC392", "IPC", "392 - Robbery"),
    ("IPC379", "IPC", "379 - Theft"),
    ("IPC420", "IPC", "420 - Cheating"),
    ("IPC406", "IPC", "406 - Criminal breach of trust"),
    ("IPC354", "IPC", "354 - Assault with intent to outrage modesty"),
    ("IPC323", "IPC", "323 - Voluntarily causing hurt"),
    ("IPC324", "IPC", "324 - Voluntarily causing hurt by dangerous weapons"),
    ("IPC307", "IPC", "307 - Attempt to murder"),
    ("IPC364", "IPC", "364 - Kidnapping"),
    ("IPC498A", "IPC", "498A - Cruelty by husband or relatives"),
    ("IPC506", "IPC", "506 - Criminal intimidation"),
    ("BNS103", "BNS", "103 - Murder"),
    ("BNS105", "BNS", "105 - Culpable homicide"),
    ("BNS309", "BNS", "309 - Robbery"),
    ("BNS316", "BNS", "316 - Criminal breach of trust"),
    ("BNS318", "BNS", "318 - Cheating"),
    ("NDPS20", "NDPS", "20 - Punishment for contravention of cannabis"),
    ("NDPS22", "NDPS", "22 - Punishment for contravention of psychotropic substances"),
    ("POCSO4", "POCSO", "4 - Penetrative sexual assault"),
    ("POCSO6", "POCSO", "6 - Aggravated penetrative sexual assault"),
    ("ITA66", "ITA", "66 - Computer related offences"),
    ("ITA66C", "ITA", "66C - Identity theft"),
    ("ITA66D", "ITA", "66D - Cheating by personation"),
    ("ARMS25", "ARMS", "25 - Punishment for possessing arms"),
]

# ── Name pools ──────────────────────────────────────────────────────────────

FIRST_NAMES_M = [
    "Rajesh", "Suresh", "Mahesh", "Ramesh", "Anil", "Vijay", "Naveen",
    "Manjunath", "Shivaraj", "Basavaraj", "Venkatesh", "Srinivas",
    "Harish", "Girish", "Prasad", "Sanjay", "Deepak", "Ravi", "Kumar",
    "Ashok", "Manoj", "Prakash", "Dinesh", "Ganesh", "Yogesh",
    "Santosh", "Kiran", "Madan", "Nagesh", "Chandrashekar",
]

FIRST_NAMES_F = [
    "Lakshmi", "Savitri", "Anitha", "Pushpa", "Meena", "Sunita",
    "Shobha", "Rekha", "Padma", "Kavitha", "Bharathi", "Suma",
    "Vidya", "Asha", "Nandini", "Priya", "Deepa", "Geetha",
    "Radha", "Sarala", "Mamatha", "Shwetha", "Pooja", "Divya",
]

LAST_NAMES = [
    "Gowda", "Reddy", "Shetty", "Nayak", "Patil", "Hegde",
    "Kumar", "Rao", "Swamy", "Murthy", "Babu", "Naik",
    "Deshpande", "Kulkarni", "Joshi", "Acharya", "Bhat",
    "Shettar", "Madar", "Hosamani", "Kamble", "Jadhav",
]

VEHICLE_MAKES = [
    ("Maruti Suzuki", ["Swift", "Baleno", "WagonR", "Alto", "Dzire", "Brezza", "Ertiga"]),
    ("Hyundai", ["i20", "Creta", "Venue", "Grand i10", "Verna"]),
    ("Tata", ["Nexon", "Punch", "Harrier", "Tiago", "Safari"]),
    ("Mahindra", ["XUV700", "Scorpio", "Thar", "Bolero", "XUV300"]),
    ("Honda", ["City", "Amaze", "Elevate"]),
    ("Toyota", ["Fortuner", "Innova Crysta", "Glanza"]),
    ("Kia", ["Seltos", "Sonet", "Carens"]),
]

VEHICLE_COLORS = ["White", "Silver", "Black", "Red", "Blue", "Grey", "Brown", "Green"]

BENGALURU_LOCATIONS: list[tuple[str, Decimal, Decimal]] = [
    ("MG Road", Decimal("12.9716"), Decimal("77.5946")),
    ("Koramangala", Decimal("12.9279"), Decimal("77.6271")),
    ("Whitefield", Decimal("12.9698"), Decimal("77.7500")),
    ("Electronic City", Decimal("12.8399"), Decimal("77.6770")),
    ("Indiranagar", Decimal("12.9784"), Decimal("77.6408")),
    ("HSR Layout", Decimal("12.9116"), Decimal("77.6474")),
    ("Jayanagar", Decimal("12.9308"), Decimal("77.5839")),
    ("Marathahalli", Decimal("12.9591"), Decimal("77.7009")),
    ("Yelahanka", Decimal("13.1005"), Decimal("77.5963")),
    ("Banashankari", Decimal("12.9255"), Decimal("77.5468")),
    ("Rajajinagar", Decimal("12.9900"), Decimal("77.5522")),
    ("Malleshwaram", Decimal("13.0035"), Decimal("77.5710")),
    ("Hebbal", Decimal("13.0358"), Decimal("77.5970")),
    ("KR Puram", Decimal("13.0059"), Decimal("77.6979")),
    ("Peenya", Decimal("13.0275"), Decimal("77.5179")),
]

# ── Helper functions ───────────────────────────────────────────────────────

_rng = random.Random(42)  # deterministic seed for reproducibility


def _rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=_rng.randint(0, max(delta, 1)))


def _rand_datetime(start: date, end: date) -> datetime:
    d = _rand_date(start, end)
    return datetime(d.year, d.month, d.day, _rng.randint(0, 23), _rng.randint(0, 59))


def _rand_name(gender_id: int = 1) -> str:
    first = _rng.choice(FIRST_NAMES_M if gender_id == 1 else FIRST_NAMES_F)
    last = _rng.choice(LAST_NAMES)
    return f"{first} {last}"


def _rand_phone() -> str:
    return f"+919{_rng.randint(100000000, 999999999)}"


def _rand_ka_plate() -> str:
    dist = _rng.choice(["01", "02", "03", "04", "05", "09", "10", "12", "19", "50", "51", "53"])
    letters = "".join(_rng.choices("ABCDEFGHJKLMNPRSTUVWXYZ", k=2))
    num = _rng.randint(1000, 9999)
    return f"KA{dist}{letters}{num}"


def _rand_location() -> tuple[str, Decimal, Decimal]:
    return _rng.choice(BENGALURU_LOCATIONS)


def _crime_no(station_id: int, year: int, seq: int) -> str:
    return f"{station_id:05d}{year}{seq:04d}0000"


def _case_no(station_id: int, seq: int) -> str:
    return f"{station_id:05d}{seq:04d}"


# ── Investigation Scenario Definitions ─────────────────────────────────────

SCENARIOS: list[dict[str, Any]] = [
    {
        "title": "Serial Chain Snatcher in Koramangala",
        "crime_head": 2, "crime_sub_head": 3,
        "acts_sections": [("IPC", "IPC392")],
        "station": 103, "district": 1, "gravity": 1,
        "victims_count": 5, "accused_count": 2,
        "brief": "Serial chain snatching incidents reported in Koramangala area. Two suspects on motorcycle targeted elderly women walking alone. CCTV footage from multiple locations and ANPR hits on the suspect vehicle helped trace the accused.",
        "vehicles": 1, "has_chargesheet": True,
    },
    {
        "title": "Cyber Fraud Ring Operating from Bengaluru",
        "crime_head": 5, "crime_sub_head": 11,
        "acts_sections": [("IPC", "IPC420"), ("ITA", "ITA66"), ("ITA", "ITA66D")],
        "station": 1501, "district": 1, "gravity": 2,
        "victims_count": 8, "accused_count": 4,
        "brief": "Organized cyber fraud ring operating fake loan apps. Victims across Karnataka defrauded of total Rs 2.3 crore. CDR analysis revealed common phone numbers linking all accused. Digital evidence seized from rented apartment in Electronic City.",
        "vehicles": 2, "has_chargesheet": True,
    },
    {
        "title": "Murder at Indiranagar Pub",
        "crime_head": 1, "crime_sub_head": 1,
        "acts_sections": [("IPC", "IPC302"), ("IPC", "IPC506")],
        "station": 105, "district": 1, "gravity": 1,
        "victims_count": 1, "accused_count": 3,
        "brief": "Victim stabbed outside pub after argument over parking. Three accused identified through CCTV footage. Weapon recovered from scene. Witnesses gave statements. One accused had previous assault cases.",
        "vehicles": 2, "has_chargesheet": True,
    },
    {
        "title": "Drug Trafficking via Dark Web — Whitefield",
        "crime_head": 6, "crime_sub_head": 16,
        "acts_sections": [("NDPS", "NDPS22")],
        "station": 102, "district": 1, "gravity": 1,
        "victims_count": 0, "accused_count": 5,
        "brief": "Major NDPS bust — synthetic drugs worth Rs 5 crore seized from Whitefield apartment. Accused were operating through dark web marketplaces using cryptocurrency. Phone surveillance and CDR analysis led to network identification. Interstate connections found.",
        "vehicles": 3, "has_chargesheet": True,
    },
    {
        "title": "Kidnapping for Ransom — Yelahanka",
        "crime_head": 7, "crime_sub_head": 17,
        "acts_sections": [("IPC", "IPC364"), ("IPC", "IPC506")],
        "station": 107, "district": 1, "gravity": 1,
        "victims_count": 1, "accused_count": 4,
        "brief": "Businessman kidnapped from near residence in Yelahanka. Ransom demand of Rs 50 lakh made via encrypted messaging. Phone triangulation and ANPR tracking of suspect vehicle led to location. Victim rescued within 48 hours.",
        "vehicles": 2, "has_chargesheet": True,
    },
    {
        "title": "ATM Robbery Spree — South Bengaluru",
        "crime_head": 2, "crime_sub_head": 3,
        "acts_sections": [("IPC", "IPC392"), ("IPC", "IPC324")],
        "station": 108, "district": 1, "gravity": 1,
        "victims_count": 3, "accused_count": 3,
        "brief": "Gang of three robbing ATM users at knifepoint across Jayanagar, JP Nagar, and Banashankari. Same vehicle spotted on ANPR cameras near all incidents. CDR analysis showed suspects communicating before each crime. One accused identified from fingerprints.",
        "vehicles": 1, "has_chargesheet": False,
    },
    {
        "title": "Domestic Violence & Dowry Death — Mysuru",
        "crime_head": 11, "crime_sub_head": 23,
        "acts_sections": [("IPC", "IPC498A"), ("IPC", "IPC304")],
        "station": 301, "district": 3, "gravity": 1,
        "victims_count": 1, "accused_count": 3,
        "brief": "Young woman found dead in marital home in Nazarbad, Mysuru. Family alleges dowry harassment by husband and in-laws. Phone records show threatening messages. Medical report indicates injuries inconsistent with suicide claim.",
        "vehicles": 0, "has_chargesheet": True,
    },
    {
        "title": "Real Estate Fraud — Electronic City",
        "crime_head": 4, "crime_sub_head": 8,
        "acts_sections": [("IPC", "IPC420"), ("IPC", "IPC406")],
        "station": 106, "district": 1, "gravity": 2,
        "victims_count": 12, "accused_count": 2,
        "brief": "Fake property developer sold same plot to multiple buyers using forged documents. Total fraud amount exceeds Rs 8 crore. 12 victims filed complaints. Accused used shell companies and fake identities.",
        "vehicles": 2, "has_chargesheet": True,
    },
    {
        "title": "Vehicle Theft Syndicate — Cross-District",
        "crime_head": 15, "crime_sub_head": 28,
        "acts_sections": [("IPC", "IPC379")],
        "station": 110, "district": 1, "gravity": 2,
        "victims_count": 6, "accused_count": 5,
        "brief": "Organized vehicle theft ring operating across Bengaluru and Mysuru. Stolen vehicles repainted and sold with forged documents. ANPR hits on highway cameras tracked movement patterns. Workshop in Mandya used for modifications.",
        "vehicles": 6, "has_chargesheet": False,
    },
    {
        "title": "Assault on Traffic Constable — MG Road",
        "crime_head": 8, "crime_sub_head": 19,
        "acts_sections": [("IPC", "IPC323"), ("IPC", "IPC506")],
        "station": 101, "district": 1, "gravity": 2,
        "victims_count": 1, "accused_count": 2,
        "brief": "Two individuals assaulted traffic police constable during routine checking on MG Road. Incident captured on traffic camera. Accused identified through vehicle registration and CCTV footage from nearby shops.",
        "vehicles": 1, "has_chargesheet": True,
    },
    {
        "title": "Online Stalking & Harassment — HSR Layout",
        "crime_head": 5, "crime_sub_head": 14,
        "acts_sections": [("ITA", "ITA66"), ("IPC", "IPC354"), ("IPC", "IPC506")],
        "station": 104, "district": 1, "gravity": 2,
        "victims_count": 1, "accused_count": 1,
        "brief": "Software engineer stalked online by former colleague. Multiple fake social media accounts created. Threatening messages sent from different numbers. Digital forensics traced all accounts to accused through IP and device analysis.",
        "vehicles": 0, "has_chargesheet": True,
    },
    {
        "title": "Gold Heist from Jewellery Shop — Mangaluru",
        "crime_head": 2, "crime_sub_head": 3,
        "acts_sections": [("IPC", "IPC392"), ("IPC", "IPC307")],
        "station": 401, "district": 4, "gravity": 1,
        "victims_count": 2, "accused_count": 4,
        "brief": "Armed robbery at prominent jewellery shop in Mangaluru. 3 kg gold ornaments stolen. Shop owner and security guard injured. Getaway vehicle captured on ANPR. Accused tracked to Kerala border through phone surveillance.",
        "vehicles": 2, "has_chargesheet": False,
    },
    {
        "title": "Missing Person Case — College Student — Hubballi",
        "crime_head": 12, "crime_sub_head": 24,
        "acts_sections": [("IPC", "IPC364")],
        "station": 501, "district": 5, "gravity": 1,
        "victims_count": 1, "accused_count": 0,
        "brief": "Engineering student reported missing from hostel in Hubballi. Last seen leaving hostel at 10 PM. Phone last active near railway station. CCTV shows student boarding auto-rickshaw. Investigation ongoing.",
        "vehicles": 0, "has_chargesheet": False,
    },
    {
        "title": "Land Grabbing & Intimidation — Tumakuru",
        "crime_head": 10, "crime_sub_head": 22,
        "acts_sections": [("IPC", "IPC420"), ("IPC", "IPC506")],
        "station": 1001, "district": 10, "gravity": 2,
        "victims_count": 3, "accused_count": 4,
        "brief": "Local strongman and associates threatening farmers to sell agricultural land below market rate. Forged documents used to claim ownership. Multiple victims. Connection to a local politician under investigation.",
        "vehicles": 2, "has_chargesheet": True,
    },
    {
        "title": "Attempt to Murder — Gang Rivalry — Davangere",
        "crime_head": 1, "crime_sub_head": 2,
        "acts_sections": [("IPC", "IPC307"), ("IPC", "IPC324"), ("ARMS", "ARMS25")],
        "station": 801, "district": 8, "gravity": 1,
        "victims_count": 2, "accused_count": 6,
        "brief": "Gang clash in Davangere market area. Two persons hacked with machetes. Rivalry between two groups over extortion territory. Multiple previous cases against accused. Weapons recovered. CCTV footage from market captures the assault.",
        "vehicles": 3, "has_chargesheet": True,
    },
    {
        "title": "Investment Fraud — Ponzi Scheme — Belagavi",
        "crime_head": 13, "crime_sub_head": 25,
        "acts_sections": [("IPC", "IPC420"), ("IPC", "IPC406")],
        "station": 601, "district": 6, "gravity": 2,
        "victims_count": 15, "accused_count": 3,
        "brief": "Ponzi scheme operated from Belagavi promising 30% monthly returns on cryptocurrency investment. Over 200 investors defrauded, total loss estimated at Rs 15 crore. Main accused fled to Dubai. Properties attached.",
        "vehicles": 1, "has_chargesheet": True,
    },
    {
        "title": "Child Trafficking Network — Kalaburagi",
        "crime_head": 7, "crime_sub_head": 18,
        "acts_sections": [("IPC", "IPC364"), ("POCSO", "POCSO4")],
        "station": 701, "district": 7, "gravity": 1,
        "victims_count": 4, "accused_count": 5,
        "brief": "Child trafficking network busted in Kalaburagi district. Children from migrant families exploited for labor. Five accused arrested including two from neighboring state. CDR analysis revealed coordination network across 3 states.",
        "vehicles": 2, "has_chargesheet": True,
    },
    {
        "title": "Hit and Run — Fatal — JP Nagar",
        "crime_head": 1, "crime_sub_head": 2,
        "acts_sections": [("IPC", "IPC304")],
        "station": 109, "district": 1, "gravity": 1,
        "victims_count": 1, "accused_count": 1,
        "brief": "Pedestrian killed in hit-and-run on JP Nagar 6th Phase main road. Vehicle identified through ANPR camera at next junction. Driver traced and arrested within 6 hours. Vehicle had no insurance.",
        "vehicles": 1, "has_chargesheet": True,
    },
    {
        "title": "Bank Robbery — Shivamogga",
        "crime_head": 2, "crime_sub_head": 3,
        "acts_sections": [("IPC", "IPC392"), ("ARMS", "ARMS25")],
        "station": 1101, "district": 11, "gravity": 1,
        "victims_count": 2, "accused_count": 4,
        "brief": "Armed robbery at SBI branch in Shivamogga. Rs 23 lakh looted. Security guard held at gunpoint. Getaway car abandoned near bus stand. Fingerprints matched with known offender. CCTV footage from bank and road cameras used for identification.",
        "vehicles": 2, "has_chargesheet": False,
    },
    {
        "title": "Illegal Arms Manufacturing — Raichur",
        "crime_head": 14, "crime_sub_head": 26,
        "acts_sections": [("ARMS", "ARMS25")],
        "station": 1201, "district": 12, "gravity": 1,
        "victims_count": 0, "accused_count": 3,
        "brief": "Illegal arms manufacturing unit discovered in rural Raichur. Three country-made pistols and ammunition seized. Workshop hidden in agricultural shed. Accused supplying weapons to criminal gangs across north Karnataka.",
        "vehicles": 1, "has_chargesheet": True,
    },
]

# ── Seed execution ─────────────────────────────────────────────────────────


async def _insert_if_empty(session: AsyncSession, model: type, rows: list[dict[str, Any]]) -> None:
    """Insert rows only if the table is empty."""
    from sqlalchemy import func, select
    count = (await session.execute(select(func.count()).select_from(model))).scalar_one()
    if count > 0:
        return
    session.add_all([model(**row) for row in rows])
    await session.flush()


async def seed_database() -> None:
    """Generate the full interconnected demo dataset."""

    from app.models.fir import (
        Accused as AccusedModel,
        Act as ActModel,
        ActSectionAssociation as ActSectionModel,
        ANPRSighting as ANPRSightModel,
        ArrestSurrender as ArrestModel,
        AssociationEdge as AssocEdgeModel,
        BiometricMatch as BioModel,
        CaseCategory as CaseCatModel,
        CaseMaster as CaseModel,
        CaseStatusMaster as CaseStatusModel,
        CasteMaster as CasteModel,
        CDRRecord as CDRRecModel,
        CellTower as CellTowerModel,
        ChargesheetDetails as CSModel,
        ComplainantDetails as CompModel,
        Court as CourtModel,
        CrimeHead as CrimeHeadModel,
        CrimeSubHead as CrimeSubModel,
        Designation as DesigModel,
        District as DistModel,
        Employee as EmpModel,
        FinancialTransaction as FinTxModel,
        GravityOffence as GravModel,
        OccupationMaster as OccModel,
        Rank as RankModel,
        RelationshipTypeMaster as RelTypeModel,
        ReligionMaster as RelModel,
        Section as SectModel,
        State as StateModel,
        Unit as UnitModel,
        UnitType as UTModel,
        Vehicle as FIRVehicleModel,
        Victim as VictimModel,
    )
    from app.models.intelligence import (
        ANPRHit as ANPRModel,
        CallDetailRecord as CDRModel,
        CCTVEvent as CCTVModel,
        CriminalRelationship as CrimRelModel,
        Evidence as EvidModel,
        PhoneNumber as PhoneModel,
        TimelineEvent as TLModel,
        IntelVehicle as VehModel,
        VehicleOwnership as VehOwnModel,
    )

    async with async_session_factory() as session:
        async with session.begin():
            # ── 1. Master data ──────────────────────────────────────

            await _insert_if_empty(session, StateModel, [
                {"state_id": KARNATAKA_STATE_ID, "state_name": "Karnataka", "nationality_id": 1, "active": True},
                {"state_id": 30, "state_name": "Goa", "nationality_id": 1, "active": True},
                {"state_id": 32, "state_name": "Kerala", "nationality_id": 1, "active": True},
                {"state_id": 33, "state_name": "Tamil Nadu", "nationality_id": 1, "active": True},
                {"state_id": 28, "state_name": "Andhra Pradesh", "nationality_id": 1, "active": True},
                {"state_id": 27, "state_name": "Maharashtra", "nationality_id": 1, "active": True},
                {"state_id": 36, "state_name": "Telangana", "nationality_id": 1, "active": True},
            ])

            await _insert_if_empty(session, DistModel, [
                {"district_id": d[0], "district_name": d[1], "state_id": KARNATAKA_STATE_ID, "active": True}
                for d in DISTRICTS
            ])

            await _insert_if_empty(session, UTModel, [
                {"unit_type_id": u[0], "unit_type_name": u[1], "city_dist_state": u[2], "hierarchy": u[3], "active": True}
                for u in UNIT_TYPES
            ])

            await _insert_if_empty(session, UnitModel, [
                {"unit_id": ps[0], "unit_name": ps[1], "type_id": 1, "state_id": KARNATAKA_STATE_ID, "district_id": ps[2], "active": True}
                for ps in POLICE_STATIONS
            ])

            await _insert_if_empty(session, RankModel, [
                {"rank_id": r[0], "rank_name": r[1], "hierarchy": r[2], "active": True}
                for r in RANKS
            ])

            await _insert_if_empty(session, DesigModel, [
                {"designation_id": d[0], "designation_name": d[1], "active": True, "sort_order": d[0]}
                for d in DESIGNATIONS
            ])

            await _insert_if_empty(session, CaseCatModel, [
                {"case_category_id": c[0], "lookup_value": c[1]}
                for c in CASE_CATEGORIES
            ])

            await _insert_if_empty(session, GravModel, [
                {"gravity_offence_id": g[0], "lookup_value": g[1]}
                for g in GRAVITY_OFFENCES
            ])

            await _insert_if_empty(session, CaseStatusModel, [
                {"case_status_id": s[0], "case_status_name": s[1]}
                for s in CASE_STATUSES
            ])

            await _insert_if_empty(session, CrimeHeadModel, [
                {"crime_head_id": ch[0], "crime_group_name": ch[1], "active": True}
                for ch in CRIME_HEADS
            ])

            await _insert_if_empty(session, CrimeSubModel, [
                {"crime_sub_head_id": cs[0], "crime_head_id": cs[1], "crime_head_name": cs[2], "seq_id": cs[3]}
                for cs in CRIME_SUB_HEADS
            ])

            await _insert_if_empty(session, RelModel, [
                {"religion_id": r[0], "religion_name": r[1]}
                for r in RELIGIONS
            ])

            await _insert_if_empty(session, CasteModel, [
                {"caste_master_id": c[0], "caste_master_name": c[1]}
                for c in CASTES
            ])

            await _insert_if_empty(session, OccModel, [
                {"occupation_id": o[0], "occupation_name": o[1]}
                for o in OCCUPATIONS
            ])

            await _insert_if_empty(session, CourtModel, [
                {"court_id": c[0], "court_name": c[1], "district_id": c[2], "state_id": c[3], "active": True}
                for c in COURTS
            ])

            await _insert_if_empty(session, ActModel, [
                {"act_code": a[0], "act_description": a[1], "short_name": a[2], "active": True}
                for a in ACTS
            ])

            await _insert_if_empty(session, SectModel, [
                {"section_code": s[0], "act_code": s[1], "section_description": s[2], "active": True}
                for s in SECTIONS
            ])

            # ── 2. Generate officers ────────────────────────────────

            employees: list[dict[str, Any]] = []
            emp_id = 1000
            station_ids = [ps[0] for ps in POLICE_STATIONS]
            for sid in station_ids:
                district_id = next(ps[2] for ps in POLICE_STATIONS if ps[0] == sid)
                for i in range(10):  # ~10 officers per station
                    emp_id += 1
                    rank_id = _rng.choice([7, 8, 9, 10, 11])
                    desig_id = _rng.choice([1, 2, 3, 7, 8])
                    gender = _rng.choice([1, 2])
                    employees.append({
                        "employee_id": emp_id,
                        "district_id": district_id,
                        "unit_id": sid,
                        "rank_id": rank_id,
                        "designation_id": desig_id,
                        "kgid": f"KG{emp_id:06d}",
                        "first_name": _rand_name(gender),
                        "employee_dob": _rand_date(date(1970, 1, 1), date(1998, 12, 31)),
                        "gender_id": gender,
                        "appointment_date": _rand_date(date(2000, 1, 1), date(2023, 6, 30)),
                    })
            await _insert_if_empty(session, EmpModel, employees)

            # ── 3. Generate scenarios ───────────────────────────────

            case_id = 10000
            victim_id = 20000
            accused_id = 30000
            complainant_id = 40000
            arrest_id = 50000
            cs_id = 60000
            vehicle_db_id = 0  # autoincrement

            # Shared accused pool — some suspects appear in multiple cases
            shared_accused: list[dict[str, Any]] = []
            for _ in range(30):
                accused_id += 1
                gender = _rng.choice([1, 1, 1, 2])  # male-heavy
                shared_accused.append({
                    "accused_master_id": accused_id,
                    "accused_name": _rand_name(gender),
                    "age_year": _rng.randint(18, 55),
                    "gender_id": gender,
                    "person_id": f"A{accused_id}",
                })

            # Shared vehicle pool
            shared_vehicles: list[dict[str, Any]] = []
            for _ in range(50):
                make_data = _rng.choice(VEHICLE_MAKES)
                shared_vehicles.append({
                    "registration_no": _rand_ka_plate(),
                    "vehicle_type": "Four Wheeler",
                    "make": make_data[0],
                    "model": _rng.choice(make_data[1]),
                    "color": _rng.choice(VEHICLE_COLORS),
                    "year": _rng.randint(2015, 2025),
                    "flagged": False,
                })
            # Add two-wheelers
            for _ in range(30):
                shared_vehicles.append({
                    "registration_no": _rand_ka_plate(),
                    "vehicle_type": "Two Wheeler",
                    "make": _rng.choice(["Honda", "TVS", "Bajaj", "Hero", "Royal Enfield", "Yamaha"]),
                    "model": _rng.choice(["Activa", "Jupiter", "Pulsar", "Splendor", "Classic 350", "FZ"]),
                    "color": _rng.choice(VEHICLE_COLORS),
                    "year": _rng.randint(2018, 2025),
                    "flagged": False,
                })

            # Phone number pool
            phone_numbers: list[dict[str, Any]] = []
            for i, acc in enumerate(shared_accused):
                phone_numbers.append({
                    "number": _rand_phone(),
                    "owner_name": acc["accused_name"],
                    "service_provider": _rng.choice(["Jio", "Airtel", "Vi", "BSNL"]),
                    "flagged": False,
                })
            # Additional phones for non-accused contacts
            for _ in range(50):
                phone_numbers.append({
                    "number": _rand_phone(),
                    "owner_name": _rand_name(_rng.choice([1, 2])),
                    "service_provider": _rng.choice(["Jio", "Airtel", "Vi", "BSNL"]),
                    "flagged": False,
                })

            # All scenario-generated records
            all_cases: list[dict[str, Any]] = []
            all_victims: list[dict[str, Any]] = []
            all_accused_records: list[dict[str, Any]] = []
            all_complainants: list[dict[str, Any]] = []
            all_arrests: list[dict[str, Any]] = []
            all_chargesheets: list[dict[str, Any]] = []
            all_act_sections: list[dict[str, Any]] = []
            all_timeline: list[dict[str, Any]] = []
            all_evidence: list[dict[str, Any]] = []
            all_cctv: list[dict[str, Any]] = []
            all_anpr: list[dict[str, Any]] = []
            all_cdr: list[dict[str, Any]] = []
            all_crim_rel: list[dict[str, Any]] = []
            all_veh_own: list[dict[str, Any]] = []

            scenario_vehicle_indices: list[list[int]] = []

            for sc_idx, scenario in enumerate(SCENARIOS):
                case_id += 1
                year = _rng.choice([2024, 2025, 2026])
                reg_date = _rand_date(date(year, 1, 1), date(year, 6, 30))
                incident_dt = _rand_datetime(reg_date - timedelta(days=_rng.randint(0, 3)), reg_date)

                station_id = scenario["station"]
                district_id = scenario["district"]
                io_emp = _rng.choice([e for e in employees if e["unit_id"] == station_id]) if any(e["unit_id"] == station_id for e in employees) else _rng.choice(employees)
                status_id = 2 if scenario["has_chargesheet"] else _rng.choice([1, 3])
                court_id = _rng.choice([c[0] for c in COURTS])

                loc_name, lat, lng = _rand_location()

                case_data = {
                    "case_master_id": case_id,
                    "crime_no": _crime_no(station_id, year, sc_idx + 1),
                    "case_no": _case_no(station_id, sc_idx + 1),
                    "crime_registered_date": reg_date,
                    "police_person_id": io_emp["employee_id"],
                    "police_station_id": station_id,
                    "case_category_id": 1,  # FIR
                    "gravity_offence_id": scenario["gravity"],
                    "crime_major_head_id": scenario["crime_head"],
                    "crime_minor_head_id": scenario["crime_sub_head"],
                    "case_status_id": status_id,
                    "court_id": court_id,
                    "incident_from_date": incident_dt,
                    "incident_to_date": incident_dt + timedelta(hours=_rng.randint(1, 6)),
                    "info_received_ps_date": _rand_datetime(reg_date, reg_date),
                    "latitude": lat,
                    "longitude": lng,
                    "brief_facts": scenario["brief"],
                }
                all_cases.append(case_data)

                # Acts & Sections for this case
                for order_idx, (act_code, section_code) in enumerate(scenario["acts_sections"]):
                    all_act_sections.append({
                        "case_master_id": case_id,
                        "act_id": act_code,
                        "section_id": section_code,
                        "act_order_id": order_idx + 1,
                        "section_order_id": order_idx + 1,
                    })

                # Victims
                for v_i in range(scenario["victims_count"]):
                    victim_id += 1
                    gender = _rng.choice([1, 2])
                    all_victims.append({
                        "victim_master_id": victim_id,
                        "case_master_id": case_id,
                        "victim_name": _rand_name(gender),
                        "age_year": _rng.randint(5, 75),
                        "gender_id": gender,
                        "victim_police": "0",
                    })

                # Accused — mix of shared (repeat offenders) and unique
                scenario_accused_ids: list[int] = []
                acc_count = scenario["accused_count"]
                shared_pick = min(acc_count, _rng.randint(0, min(2, acc_count)))
                if shared_pick > 0:
                    picks = _rng.sample(shared_accused, shared_pick)
                    for pick in picks:
                        # Link shared accused to this case
                        accused_id += 1
                        all_accused_records.append({
                            "accused_master_id": accused_id,
                            "case_master_id": case_id,
                            "accused_name": pick["accused_name"],
                            "age_year": pick["age_year"],
                            "gender_id": pick["gender_id"],
                            "person_id": pick["person_id"],  # same person_id = repeat offender
                        })
                        scenario_accused_ids.append(accused_id)
                for _ in range(acc_count - shared_pick):
                    accused_id += 1
                    gender = _rng.choice([1, 1, 1, 2])
                    all_accused_records.append({
                        "accused_master_id": accused_id,
                        "case_master_id": case_id,
                        "accused_name": _rand_name(gender),
                        "age_year": _rng.randint(18, 55),
                        "gender_id": gender,
                        "person_id": f"A{accused_id}",
                    })
                    scenario_accused_ids.append(accused_id)

                # Complainant
                complainant_id += 1
                gender = _rng.choice([1, 2])
                all_complainants.append({
                    "complainant_id": complainant_id,
                    "case_master_id": case_id,
                    "complainant_name": _rand_name(gender),
                    "age_year": _rng.randint(20, 65),
                    "occupation_id": _rng.choice([o[0] for o in OCCUPATIONS]),
                    "religion_id": _rng.choice([r[0] for r in RELIGIONS]),
                    "caste_id": _rng.choice([c[0] for c in CASTES]),
                    "gender_id": gender,
                })

                # Arrests
                for acc_id in scenario_accused_ids:
                    if _rng.random() < 0.7:  # 70% chance of arrest
                        arrest_id += 1
                        all_arrests.append({
                            "arrest_surrender_id": arrest_id,
                            "case_master_id": case_id,
                            "arrest_surrender_type_id": 1,
                            "arrest_surrender_date": reg_date + timedelta(days=_rng.randint(0, 30)),
                            "arrest_surrender_state_id": KARNATAKA_STATE_ID,
                            "arrest_surrender_district_id": district_id,
                            "police_station_id": station_id,
                            "io_id": io_emp["employee_id"],
                            "court_id": court_id,
                            "accused_master_id": acc_id,
                            "is_accused": True,
                            "is_complainant_accused": False,
                        })

                # Chargesheet
                if scenario["has_chargesheet"]:
                    cs_id += 1
                    all_chargesheets.append({
                        "cs_id": cs_id,
                        "case_master_id": case_id,
                        "cs_date": datetime.combine(reg_date + timedelta(days=_rng.randint(30, 90)), datetime.min.time()),
                        "cs_type": _rng.choice(["A", "B"]),
                        "police_person_id": io_emp["employee_id"],
                    })

                # Vehicles for this scenario
                sc_vehicle_indices: list[int] = []
                for _ in range(scenario["vehicles"]):
                    v_idx = _rng.randint(0, len(shared_vehicles) - 1)
                    sc_vehicle_indices.append(v_idx)
                    shared_vehicles[v_idx]["flagged"] = True
                    # Ownership link
                    if scenario_accused_ids:
                        all_veh_own.append({
                            "_vehicle_idx": v_idx,
                            "owner_name": _rng.choice([a["accused_name"] for a in all_accused_records if a["case_master_id"] == case_id]),
                            "owner_accused_id": _rng.choice(scenario_accused_ids) if scenario_accused_ids else None,
                            "ownership_from": _rand_date(date(2020, 1, 1), reg_date),
                        })
                scenario_vehicle_indices.append(sc_vehicle_indices)

                # ── Timeline events ─────────────────────────────────
                base_ts = incident_dt
                timeline_entries = [
                    ("incident", "Incident Reported", f"Crime incident: {scenario['title']}", "FIR"),
                    ("fir_registered", "FIR Registered", f"FIR registered at {next((ps[1] for ps in POLICE_STATIONS if ps[0] == station_id), 'PS')}", "System"),
                ]
                if scenario["accused_count"] > 0:
                    timeline_entries.append(("investigation", "Investigation Started", "IO assigned and investigation commenced", "Investigation"))
                if scenario["vehicles"] > 0:
                    timeline_entries.append(("anpr_hit", "Vehicle Identified", "Suspect vehicle identified through ANPR camera", "ANPR"))
                if acc_count > 0:
                    timeline_entries.append(("suspect_identified", "Suspect Identified", "Primary suspect identified through evidence", "Investigation"))
                if any(a["case_master_id"] == case_id for a in all_arrests):
                    timeline_entries.append(("arrest", "Arrest Made", "Accused arrested by investigating team", "Arrest"))
                if scenario["has_chargesheet"]:
                    timeline_entries.append(("chargesheet", "Chargesheet Filed", "Chargesheet filed in court", "Legal"))

                for t_idx, (etype, title, desc, source) in enumerate(timeline_entries):
                    ts = base_ts + timedelta(hours=t_idx * _rng.randint(2, 48))
                    eloc_name, elat, elng = _rand_location()
                    all_timeline.append({
                        "case_master_id": case_id,
                        "event_time": ts,
                        "event_type": etype,
                        "title": title,
                        "description": desc,
                        "source": source,
                        "latitude": elat,
                        "longitude": elng,
                        "severity": "high" if etype in ("incident", "arrest") else "medium",
                    })

                # ── Evidence ────────────────────────────────────────
                evidence_types = ["Physical", "Documentary", "Digital", "Forensic", "Witness Statement"]
                for _ in range(_rng.randint(2, 5)):
                    ev_type = _rng.choice(evidence_types)
                    all_evidence.append({
                        "case_master_id": case_id,
                        "evidence_type": ev_type,
                        "description": f"{ev_type} evidence collected for {scenario['title']}",
                        "collected_date": reg_date + timedelta(days=_rng.randint(0, 14)),
                        "collected_by_employee_id": io_emp["employee_id"],
                        "location": loc_name,
                        "status": _rng.choice(["Collected", "Analyzed", "Submitted to Court"]),
                    })

                # ── CCTV events ─────────────────────────────────────
                for _ in range(_rng.randint(3, 8)):
                    cloc_name, clat, clng = _rand_location()
                    all_cctv.append({
                        "camera_id": f"CAM-{_rng.randint(1000, 9999)}",
                        "camera_location": cloc_name,
                        "event_time": _rand_datetime(reg_date - timedelta(days=1), reg_date + timedelta(days=3)),
                        "event_type": _rng.choice(["Person Detected", "Vehicle Detected", "Suspicious Activity", "Motion Alert"]),
                        "description": f"CCTV event related to case {case_id}",
                        "case_master_id": case_id,
                        "latitude": clat,
                        "longitude": clng,
                        "flagged": _rng.random() < 0.3,
                    })

            # ── Generate additional cases to reach ~200 ─────────────

            extra_case_count = 200 - len(SCENARIOS)
            for extra_idx in range(extra_case_count):
                case_id += 1
                year = _rng.choice([2023, 2024, 2025, 2026])
                reg_date = _rand_date(date(year, 1, 1), date(year, 12, 28))
                incident_dt = _rand_datetime(reg_date - timedelta(days=_rng.randint(0, 2)), reg_date)
                station_id = _rng.choice(station_ids)
                district_id = next(ps[2] for ps in POLICE_STATIONS if ps[0] == station_id)
                ch = _rng.choice(CRIME_HEADS)
                crime_head_id = ch[0]
                matching_subs = [s for s in CRIME_SUB_HEADS if s[1] == crime_head_id]
                csub = _rng.choice(matching_subs) if matching_subs else CRIME_SUB_HEADS[0]
                io_emp = _rng.choice([e for e in employees if e["unit_id"] == station_id]) if any(e["unit_id"] == station_id for e in employees) else _rng.choice(employees)
                status_id = _rng.choice([s[0] for s in CASE_STATUSES])
                court_id = _rng.choice([c[0] for c in COURTS])
                loc_name, lat, lng = _rand_location()

                all_cases.append({
                    "case_master_id": case_id,
                    "crime_no": _crime_no(station_id, year, len(SCENARIOS) + extra_idx + 1),
                    "case_no": _case_no(station_id, len(SCENARIOS) + extra_idx + 1),
                    "crime_registered_date": reg_date,
                    "police_person_id": io_emp["employee_id"],
                    "police_station_id": station_id,
                    "case_category_id": _rng.choice([1, 1, 1, 2]),  # mostly FIR
                    "gravity_offence_id": _rng.choice([1, 2, 2, 2, 3]),
                    "crime_major_head_id": crime_head_id,
                    "crime_minor_head_id": csub[0],
                    "case_status_id": status_id,
                    "court_id": court_id,
                    "incident_from_date": incident_dt,
                    "incident_to_date": incident_dt + timedelta(hours=_rng.randint(1, 24)),
                    "info_received_ps_date": _rand_datetime(reg_date, reg_date),
                    "latitude": lat,
                    "longitude": lng,
                    "brief_facts": f"{ch[1]} case registered at {next((ps[1] for ps in POLICE_STATIONS if ps[0] == station_id), 'PS')}. Under investigation.",
                })

                # Victims for extra cases
                for _ in range(_rng.randint(1, 3)):
                    victim_id += 1
                    gender = _rng.choice([1, 2])
                    all_victims.append({
                        "victim_master_id": victim_id,
                        "case_master_id": case_id,
                        "victim_name": _rand_name(gender),
                        "age_year": _rng.randint(10, 70),
                        "gender_id": gender,
                        "victim_police": "0",
                    })

                # Accused for extra cases
                acc_count = _rng.randint(1, 3)
                for _ in range(acc_count):
                    accused_id += 1
                    gender = _rng.choice([1, 1, 2])
                    # 20% chance of being a repeat offender
                    if _rng.random() < 0.2 and shared_accused:
                        pick = _rng.choice(shared_accused)
                        all_accused_records.append({
                            "accused_master_id": accused_id,
                            "case_master_id": case_id,
                            "accused_name": pick["accused_name"],
                            "age_year": pick["age_year"],
                            "gender_id": pick["gender_id"],
                            "person_id": pick["person_id"],
                        })
                    else:
                        all_accused_records.append({
                            "accused_master_id": accused_id,
                            "case_master_id": case_id,
                            "accused_name": _rand_name(gender),
                            "age_year": _rng.randint(18, 55),
                            "gender_id": gender,
                            "person_id": f"A{accused_id}",
                        })

                # Complainant for extra cases
                complainant_id += 1
                gender = _rng.choice([1, 2])
                all_complainants.append({
                    "complainant_id": complainant_id,
                    "case_master_id": case_id,
                    "complainant_name": _rand_name(gender),
                    "age_year": _rng.randint(20, 65),
                    "occupation_id": _rng.choice([o[0] for o in OCCUPATIONS]),
                    "religion_id": _rng.choice([r[0] for r in RELIGIONS]),
                    "caste_id": _rng.choice([c[0] for c in CASTES]),
                    "gender_id": gender,
                })

                # Timeline for extra cases
                for t_idx, (etype, title) in enumerate([("incident", "Incident"), ("fir_registered", "FIR Registered")]):
                    all_timeline.append({
                        "case_master_id": case_id,
                        "event_time": incident_dt + timedelta(hours=t_idx),
                        "event_type": etype,
                        "title": title,
                        "description": f"{title} for case {case_id}",
                        "source": "System",
                        "latitude": lat,
                        "longitude": lng,
                        "severity": "medium",
                    })

            # ── Insert FIR layer data ───────────────────────────────

            await _insert_if_empty(session, CaseModel, all_cases)
            await _insert_if_empty(session, VictimModel, all_victims)
            await _insert_if_empty(session, AccusedModel, all_accused_records)
            await _insert_if_empty(session, CompModel, all_complainants)
            await _insert_if_empty(session, ArrestModel, all_arrests)
            await _insert_if_empty(session, CSModel, all_chargesheets)
            await _insert_if_empty(session, ActSectionModel, all_act_sections)

            # ── Insert intelligence layer data ──────────────────────

            # Vehicles
            await _insert_if_empty(session, VehModel, shared_vehicles)

            # We need the auto-generated vehicle IDs for ownership & ANPR
            # Since we use autoincrement, vehicle_id = insertion order + 1
            from sqlalchemy import select
            veh_rows = (await session.execute(select(VehModel))).scalars().all()
            veh_map: dict[str, int] = {v.registration_no: v.vehicle_id for v in veh_rows}
            veh_list = list(veh_map.values())

            # Vehicle Ownership
            veh_own_rows: list[dict[str, Any]] = []
            for vo in all_veh_own:
                v_idx = vo.pop("_vehicle_idx")
                reg_no = shared_vehicles[v_idx]["registration_no"]
                if reg_no in veh_map:
                    vo["vehicle_id"] = veh_map[reg_no]
                    veh_own_rows.append(vo)
            await _insert_if_empty(session, VehOwnModel, veh_own_rows)

            # Phone numbers
            await _insert_if_empty(session, PhoneModel, phone_numbers)
            phone_rows = (await session.execute(select(PhoneModel))).scalars().all()
            phone_ids = [p.phone_id for p in phone_rows]

            # ANPR hits — generate ~2000
            anpr_rows: list[dict[str, Any]] = []
            if veh_list:
                for _ in range(2000):
                    loc_name, lat, lng = _rand_location()
                    anpr_rows.append({
                        "vehicle_id": _rng.choice(veh_list),
                        "camera_id": f"ANPR-{_rng.randint(100, 999)}",
                        "camera_location": loc_name,
                        "captured_at": _rand_datetime(date(2024, 1, 1), date(2026, 6, 30)),
                        "latitude": lat,
                        "longitude": lng,
                        "confidence": round(_rng.uniform(0.75, 0.99), 2),
                        "direction": _rng.choice(["North", "South", "East", "West"]),
                    })
            await _insert_if_empty(session, ANPRModel, anpr_rows)

            # CCTV events
            await _insert_if_empty(session, CCTVModel, all_cctv)

            # CDR — generate ~3000
            cdr_rows: list[dict[str, Any]] = []
            if len(phone_ids) >= 2:
                for _ in range(3000):
                    caller = _rng.choice(phone_ids)
                    receiver = _rng.choice([p for p in phone_ids if p != caller]) if len(phone_ids) > 1 else caller
                    loc_name, lat, lng = _rand_location()
                    cdr_rows.append({
                        "caller_phone_id": caller,
                        "receiver_phone_id": receiver,
                        "call_time": _rand_datetime(date(2024, 1, 1), date(2026, 6, 30)),
                        "duration_seconds": _rng.randint(5, 3600),
                        "call_type": _rng.choice(["voice", "voice", "sms", "data"]),
                        "tower_id": f"TWR-{_rng.randint(10000, 99999)}",
                        "tower_location": loc_name,
                        "latitude": lat,
                        "longitude": lng,
                    })
            await _insert_if_empty(session, CDRModel, cdr_rows)

            # Evidence
            await _insert_if_empty(session, EvidModel, all_evidence)

            # Timeline events
            # Generate additional timeline events to reach ~5000
            existing_tl = len(all_timeline)
            case_ids = [c["case_master_id"] for c in all_cases]
            extra_tl_needed = max(0, 5000 - existing_tl)
            extra_timeline_types = [
                ("witness_statement", "Witness Statement Recorded", "Witness statement taken", "Investigation"),
                ("evidence_collected", "Evidence Collected", "Evidence secured from scene", "Forensic"),
                ("suspect_interrogation", "Suspect Interrogated", "Suspect questioned at station", "Investigation"),
                ("lab_report", "Lab Report Received", "Forensic lab analysis report received", "Forensic"),
                ("court_hearing", "Court Hearing", "Case presented before magistrate", "Legal"),
                ("raid_conducted", "Raid Conducted", "Premises searched under warrant", "Investigation"),
                ("surveillance", "Surveillance Deployed", "Technical surveillance initiated", "Intelligence"),
                ("informant_tip", "Informant Tip Received", "Confidential information received", "Intelligence"),
            ]
            for _ in range(extra_tl_needed):
                c_id = _rng.choice(case_ids)
                etype, title, desc, source = _rng.choice(extra_timeline_types)
                loc_name, lat, lng = _rand_location()
                all_timeline.append({
                    "case_master_id": c_id,
                    "event_time": _rand_datetime(date(2024, 1, 1), date(2026, 6, 30)),
                    "event_type": etype,
                    "title": title,
                    "description": f"{desc} — Case {c_id}",
                    "source": source,
                    "latitude": lat,
                    "longitude": lng,
                    "severity": _rng.choice(["low", "medium", "medium", "high"]),
                })
            await _insert_if_empty(session, TLModel, all_timeline)

            # Criminal relationships — link repeat offenders
            person_to_accused: dict[str, list[int]] = {}
            for acc in all_accused_records:
                pid = acc["person_id"]
                person_to_accused.setdefault(pid, []).append(acc["accused_master_id"])
            for pid, acc_ids in person_to_accused.items():
                if len(acc_ids) > 1:
                    for i in range(len(acc_ids)):
                        for j in range(i + 1, len(acc_ids)):
                            all_crim_rel.append({
                                "accused_id_1": acc_ids[i],
                                "accused_id_2": acc_ids[j],
                                "relationship_type": "co-accused",
                                "strength": round(_rng.uniform(0.5, 1.0), 2),
                                "detected_via": "case_analysis",
                            })
            # Also link accused who share cases
            case_accused_map: dict[int, list[int]] = {}
            for acc in all_accused_records:
                case_accused_map.setdefault(acc["case_master_id"], []).append(acc["accused_master_id"])
            for cid, acc_ids in case_accused_map.items():
                if len(acc_ids) > 1:
                    for i in range(len(acc_ids)):
                        for j in range(i + 1, min(len(acc_ids), i + 3)):  # limit pairs
                            pair = (min(acc_ids[i], acc_ids[j]), max(acc_ids[i], acc_ids[j]))
                            if not any(r["accused_id_1"] == pair[0] and r["accused_id_2"] == pair[1] for r in all_crim_rel):
                                all_crim_rel.append({
                                    "accused_id_1": pair[0],
                                    "accused_id_2": pair[1],
                                    "relationship_type": "co-accused",
                                    "strength": round(_rng.uniform(0.6, 1.0), 2),
                                    "detected_via": "case_link",
                                    "case_master_id": cid,
                                })
            await _insert_if_empty(session, CrimRelModel, all_crim_rel)

        print(f"✓ Seeded {len(all_cases)} cases")
        print(f"✓ Seeded {len(all_victims)} victims")
        print(f"✓ Seeded {len(all_accused_records)} accused records")
        print(f"✓ Seeded {len(all_complainants)} complainants")
        print(f"✓ Seeded {len(all_arrests)} arrests")
        print(f"✓ Seeded {len(all_chargesheets)} chargesheets")
        print(f"✓ Seeded {len(shared_vehicles)} vehicles")
        print(f"✓ Seeded {len(anpr_rows)} ANPR hits")
        print(f"✓ Seeded {len(all_cctv)} CCTV events")
        print(f"✓ Seeded {len(cdr_rows)} CDR records")
        print(f"✓ Seeded {len(all_timeline)} timeline events")
        print(f"✓ Seeded {len(all_evidence)} evidence records")
        print(f"✓ Seeded {len(all_crim_rel)} criminal relationships")
        print(f"✓ Seeded {len(employees)} officers")
        print("✓ Seed complete")

    # Handcrafted demo cases — deterministic, queryable by name
    await _seed_handcrafted_demo_cases()


async def _seed_handcrafted_demo_cases() -> None:
    """Seed 6 deterministic demo cases (Cases 1–6) with named entities.

    Uses ID range 90000+ to avoid collision with procedural data.
    Uses the extended KSP schema: Vehicle, ANPRSighting, CDRRecord,
    CellTower, BiometricMatch, FinancialTransaction, AssociationEdge.
    """
    from sqlalchemy import func, select

    from app.models.fir import (
        Accused as AccusedModel,
        ActSectionAssociation as ActSectionModel,
        ANPRSighting as ANPRSightModel,
        ArrestSurrender as ArrestModel,
        AssociationEdge as AssocEdgeModel,
        BiometricMatch as BioModel,
        CaseMaster as CaseModel,
        CDRRecord as CDRRecModel,
        CellTower as CellTowerModel,
        ChargesheetDetails as CSModel,
        ComplainantDetails as CompModel,
        FinancialTransaction as FinTxModel,
        RelationshipTypeMaster as RelTypeModel,
        Vehicle as FIRVehicleModel,
        Victim as VictimModel,
    )

    async with async_session_factory() as session:
        async with session.begin():
            # Guard: skip if demo cases already seeded (check for case_master_id 90001)
            exists = (
                await session.execute(
                    select(func.count())
                    .select_from(CaseModel)
                    .where(CaseModel.case_master_id == 90001)
                )
            ).scalar_one()
            if exists > 0:
                print("✓ Demo cases already seeded, skipping")
                return

            # ── Relationship type lookup data ──────────────────────
            rel_type_count = (
                await session.execute(
                    select(func.count()).select_from(RelTypeModel)
                )
            ).scalar_one()
            if rel_type_count == 0:
                session.add_all([
                    RelTypeModel(relationship_type_id=1, relationship_type_name="co-accused"),
                    RelTypeModel(relationship_type_id=2, relationship_type_name="financial"),
                    RelTypeModel(relationship_type_id=3, relationship_type_name="communication"),
                    RelTypeModel(relationship_type_id=4, relationship_type_name="cross-case-identity"),
                    RelTypeModel(relationship_type_id=5, relationship_type_name="vehicle-link"),
                ])
                await session.flush()

            # ── Cell towers (shared reference data) ────────────────
            ct_count = (
                await session.execute(
                    select(func.count()).select_from(CellTowerModel)
                )
            ).scalar_one()
            if ct_count == 0:
                session.add_all([
                    CellTowerModel(cell_tower_id=1, tower_code="TWR-BLR-MG01",
                                   latitude=Decimal("12.9716"), longitude=Decimal("77.5946"), district_id=1),
                    CellTowerModel(cell_tower_id=2, tower_code="TWR-BLR-KRM01",
                                   latitude=Decimal("12.9279"), longitude=Decimal("77.6271"), district_id=1),
                    CellTowerModel(cell_tower_id=3, tower_code="TWR-MYS-NAZ01",
                                   latitude=Decimal("12.3051"), longitude=Decimal("76.6551"), district_id=3),
                    CellTowerModel(cell_tower_id=4, tower_code="TWR-BLR-WF01",
                                   latitude=Decimal("12.9698"), longitude=Decimal("77.7500"), district_id=1),
                    CellTowerModel(cell_tower_id=5, tower_code="TWR-HUB-CTY01",
                                   latitude=Decimal("15.3647"), longitude=Decimal("75.1240"), district_id=5),
                    CellTowerModel(cell_tower_id=6, tower_code="TWR-BLR-EC01",
                                   latitude=Decimal("12.8399"), longitude=Decimal("77.6770"), district_id=1),
                    CellTowerModel(cell_tower_id=7, tower_code="TWR-BLR-SB01",
                                   latitude=Decimal("12.9177"), longitude=Decimal("77.6238"), district_id=1),
                ])
                await session.flush()

            # ═══════════════════════════════════════════════════════
            # CASE 1 — Vikram Hegde Syndicate Lead
            # Absconding suspect linked to armed robbery, vehicle ANPR,
            # and CDR contacts with financier/logistics associates.
            # ═══════════════════════════════════════════════════════

            session.add(CaseModel(
                case_master_id=90100,
                crime_no="010302026014200000",
                case_no="010300142",
                crime_registered_date=date(2026, 7, 6),
                police_person_id=1021,  # Koramangala PS officer
                police_station_id=103,
                case_category_id=1,
                gravity_offence_id=1,
                crime_major_head_id=2,   # Robbery
                crime_minor_head_id=3,   # Armed robbery
                case_status_id=1,        # Under Investigation
                court_id=3,
                incident_from_date=datetime(2026, 7, 6, 16, 45),
                incident_to_date=datetime(2026, 7, 6, 18, 10),
                info_received_ps_date=datetime(2026, 7, 6, 18, 35),
                latitude=Decimal("12.9279"),
                longitude=Decimal("77.6271"),
                brief_facts=(
                    "Highway hijack and armed robbery linked to absconding suspect Vikram Hegde. "
                    "ANPR sightings place white Mahindra Scorpio KA05MJ4421 near Koramangala 80 Feet Road. "
                    "CDR analysis links Vikram Hegde with Suresh Gowda and Kiran Kumar before the consignment drop."
                ),
            ))

            session.add(AccusedModel(
                accused_master_id=90100,
                case_master_id=90100,
                accused_name="Vikram Hegde",
                age_year=38,
                gender_id=1,
                person_id="DEMO-VIKRAM-001",
                flagged=True,
                flag_reason="Absconding syndicate leader linked to highway hijack and armed robbery",
            ))
            session.add(AccusedModel(
                accused_master_id=90101,
                case_master_id=90100,
                accused_name="Suresh Gowda",
                age_year=42,
                gender_id=1,
                person_id="DEMO-SURESH-001",
                flagged=True,
                flag_reason="Financier and call contact of Vikram Hegde",
            ))
            session.add(AccusedModel(
                accused_master_id=90102,
                case_master_id=90100,
                accused_name="Kiran Kumar",
                age_year=34,
                gender_id=1,
                person_id="DEMO-KIRAN-001",
            ))

            session.add(VictimModel(
                victim_master_id=90100,
                case_master_id=90100,
                victim_name="Rajesh Kumar",
                age_year=45,
                gender_id=1,
                victim_police="0",
            ))

            session.add(CompModel(
                complainant_id=90100,
                case_master_id=90100,
                complainant_name="Rajesh Kumar",
                age_year=45,
                occupation_id=2,
                religion_id=1,
                caste_id=1,
                gender_id=1,
            ))

            session.add(ActSectionModel(
                case_master_id=90100, act_id="IPC", section_id="IPC392",
                act_order_id=1, section_order_id=1,
            ))
            session.add(ActSectionModel(
                case_master_id=90100, act_id="IPC", section_id="IPC506",
                act_order_id=2, section_order_id=2,
            ))

            session.add(FIRVehicleModel(
                vehicle_id=90100,
                registration_number="KA05MJ4421",
                owner_accused_id=90100,
                active=True,
            ))

            session.add(ANPRSightModel(
                anpr_sighting_id=90100,
                vehicle_id=90100,
                camera_location="Koramangala 80 Feet Road Cam-01",
                sighting_date_time=datetime(2026, 7, 6, 17, 5),
                latitude=Decimal("12.9279"),
                longitude=Decimal("77.6271"),
            ))
            session.add(ANPRSightModel(
                anpr_sighting_id=90101,
                vehicle_id=90100,
                camera_location="Silk Board Junction ANPR",
                sighting_date_time=datetime(2026, 7, 6, 17, 45),
                latitude=Decimal("12.9177"),
                longitude=Decimal("77.6238"),
            ))

            session.add(CDRRecModel(
                cdr_record_id=90100,
                accused_master_id=90100,
                cell_tower_id=2,
                call_date_time=datetime(2026, 7, 6, 17, 10),
                duration_seconds=240,
                connected_accused_id=90101,
            ))
            session.add(CDRRecModel(
                cdr_record_id=90101,
                accused_master_id=90100,
                cell_tower_id=7,
                call_date_time=datetime(2026, 7, 6, 17, 45),
                duration_seconds=98,
                connected_accused_id=90102,
            ))

            session.add(BioModel(
                biometric_match_id=90100,
                accused_master_id=90100,
                location_name="Koramangala 80 Feet Road Cam-01",
                match_date_time=datetime(2026, 7, 6, 17, 7),
                match_type="facial_recognition",
                confidence_score=Decimal("0.91"),
            ))

            session.add(AssocEdgeModel(
                association_edge_id=90100,
                source_entity_type="Accused",
                source_entity_id=str(90100),
                target_entity_type="Accused",
                target_entity_id=str(90101),
                relationship_type_id=3,
                evidence="CDR call: Vikram Hegde to Suresh Gowda for 240 seconds before consignment drop",
                duration_seconds=240,
            ))
            session.add(AssocEdgeModel(
                association_edge_id=90101,
                source_entity_type="Accused",
                source_entity_id=str(90100),
                target_entity_type="Accused",
                target_entity_id=str(90102),
                relationship_type_id=3,
                evidence="CDR call: Vikram Hegde to Kiran Kumar near Silk Board sector",
                duration_seconds=98,
            ))

            await session.flush()

            # ═══════════════════════════════════════════════════════
            # CASE 2 — Cross-District Repeat Suspect
            # Sunil Jadhav appears in two FIRs across Bengaluru Urban
            # (Koramangala PS, dist 1) and Mysuru (Nazarbad PS, dist 3),
            # months apart, different crime categories (Robbery vs Theft).
            # ═══════════════════════════════════════════════════════

            SUNIL_PERSON_ID = "DEMO-SUNIL-001"

            # Case 2A — Robbery in Bengaluru
            session.add(CaseModel(
                case_master_id=90001,
                crime_no="010302025000100000",
                case_no="010300010",
                crime_registered_date=date(2025, 2, 15),
                police_person_id=1021,  # Koramangala PS officer
                police_station_id=103,
                case_category_id=1,
                gravity_offence_id=1,
                crime_major_head_id=2,   # Robbery
                crime_minor_head_id=3,   # Armed robbery
                case_status_id=1,        # Under Investigation
                court_id=3,
                incident_from_date=datetime(2025, 2, 14, 22, 30),
                incident_to_date=datetime(2025, 2, 14, 23, 15),
                info_received_ps_date=datetime(2025, 2, 15, 0, 10),
                latitude=Decimal("12.9279"),
                longitude=Decimal("77.6271"),
                brief_facts="Armed robbery at provision store on 80 Feet Road, Koramangala. Single male suspect brandished knife, took Rs 45,000 cash and gold chain from shopkeeper. Fled on two-wheeler heading towards Madiwala. Suspect identified as Sunil Jadhav from CCTV footage.",
            ))

            # Case 2B — Theft in Mysuru (same person, 4 months later)
            session.add(CaseModel(
                case_master_id=90002,
                crime_no="030102025000100000",
                case_no="030100010",
                crime_registered_date=date(2025, 6, 10),
                police_person_id=1121,  # Nazarbad PS officer
                police_station_id=301,
                case_category_id=1,
                gravity_offence_id=2,
                crime_major_head_id=3,   # Theft
                crime_minor_head_id=5,   # House breaking theft
                case_status_id=1,        # Under Investigation
                court_id=4,
                incident_from_date=datetime(2025, 6, 9, 3, 0),
                incident_to_date=datetime(2025, 6, 9, 5, 0),
                info_received_ps_date=datetime(2025, 6, 10, 7, 0),
                latitude=Decimal("12.3051"),
                longitude=Decimal("76.6551"),
                brief_facts="House break-in at residential property in Nazarbad, Mysuru. Laptop, jewellery worth Rs 2.8 lakh stolen. Fingerprints recovered from entry point. Suspect identified as Sunil Jadhav, matching description from earlier Bengaluru robbery case.",
            ))

            # Accused records — same person_id links them
            session.add(AccusedModel(
                accused_master_id=90001,
                case_master_id=90001,
                accused_name="Sunil Jadhav",
                age_year=28,
                gender_id=1,
                person_id=SUNIL_PERSON_ID,
            ))
            session.add(AccusedModel(
                accused_master_id=90002,
                case_master_id=90002,
                accused_name="Sunil Jadhav",
                age_year=28,
                gender_id=1,
                person_id=SUNIL_PERSON_ID,
            ))

            # Victims
            session.add(VictimModel(
                victim_master_id=90001,
                case_master_id=90001,
                victim_name="Ravi Kumar Shetty",
                age_year=52,
                gender_id=1,
                victim_police="0",
            ))
            session.add(VictimModel(
                victim_master_id=90002,
                case_master_id=90002,
                victim_name="Padma Deshpande",
                age_year=45,
                gender_id=2,
                victim_police="0",
            ))

            # Complainants
            session.add(CompModel(
                complainant_id=90001,
                case_master_id=90001,
                complainant_name="Ravi Kumar Shetty",
                age_year=52,
                occupation_id=2,
                religion_id=1,
                caste_id=1,
                gender_id=1,
            ))
            session.add(CompModel(
                complainant_id=90002,
                case_master_id=90002,
                complainant_name="Padma Deshpande",
                age_year=45,
                occupation_id=10,
                religion_id=1,
                caste_id=1,
                gender_id=2,
            ))

            # Act/Section associations
            session.add(ActSectionModel(
                case_master_id=90001, act_id="IPC", section_id="IPC392",
                act_order_id=1, section_order_id=1,
            ))
            session.add(ActSectionModel(
                case_master_id=90002, act_id="IPC", section_id="IPC379",
                act_order_id=1, section_order_id=1,
            ))

            # Vehicle for Case 2A — suspect's two-wheeler
            session.add(FIRVehicleModel(
                vehicle_id=90001,
                registration_number="KA01MH4532",
                owner_accused_id=90001,
                active=True,
            ))

            # ANPR sightings linking the vehicle across districts
            session.add(ANPRSightModel(
                anpr_sighting_id=90001,
                vehicle_id=90001,
                camera_location="Madiwala Junction, Bengaluru",
                sighting_date_time=datetime(2025, 2, 14, 23, 20),
                latitude=Decimal("12.9218"),
                longitude=Decimal("77.6190"),
            ))
            session.add(ANPRSightModel(
                anpr_sighting_id=90002,
                vehicle_id=90001,
                camera_location="Mysuru Road Toll, Ramanagara",
                sighting_date_time=datetime(2025, 6, 8, 21, 45),
                latitude=Decimal("12.7113"),
                longitude=Decimal("77.2810"),
            ))

            # CDR — calls near incident times
            session.add(CDRRecModel(
                cdr_record_id=90001,
                accused_master_id=90001,
                cell_tower_id=2,  # Koramangala tower
                call_date_time=datetime(2025, 2, 14, 22, 15),
                duration_seconds=45,
                connected_accused_id=None,
            ))
            session.add(CDRRecModel(
                cdr_record_id=90002,
                accused_master_id=90002,
                cell_tower_id=3,  # Mysuru tower
                call_date_time=datetime(2025, 6, 9, 2, 50),
                duration_seconds=120,
                connected_accused_id=None,
            ))

            # Biometric — fingerprint match at Mysuru scene
            session.add(BioModel(
                biometric_match_id=90001,
                accused_master_id=90002,
                location_name="Nazarbad residence entry point",
                match_date_time=datetime(2025, 6, 10, 11, 30),
                match_type="fingerprint",
                confidence_score=Decimal("0.94"),
            ))

            # AssociationEdge — cross-district link
            session.add(AssocEdgeModel(
                association_edge_id=90001,
                source_entity_type="Accused",
                source_entity_id=str(90001),
                target_entity_type="Accused",
                target_entity_id=str(90002),
                relationship_type_id=4,  # cross-case-identity
                evidence="Same person_id DEMO-SUNIL-001; fingerprint match; ANPR vehicle KA01MH4532 sighted in both districts",
            ))

            await session.flush()

            # ═══════════════════════════════════════════════════════
            # CASE 3 — Weak / Circumstantial Evidence
            # FIR registered but minimal supporting data. No ANPR,
            # no CDR, no biometric. Only a vague complainant statement.
            # ═══════════════════════════════════════════════════════

            session.add(CaseModel(
                case_master_id=90003,
                crime_no="010402025000100000",
                case_no="010400010",
                crime_registered_date=date(2025, 4, 20),
                police_person_id=1031,  # HSR Layout PS officer
                police_station_id=104,
                case_category_id=1,
                gravity_offence_id=2,
                crime_major_head_id=3,   # Theft
                crime_minor_head_id=6,   # Pickpocketing
                case_status_id=1,        # Under Investigation
                court_id=1,
                incident_from_date=datetime(2025, 4, 19, 18, 0),
                incident_to_date=datetime(2025, 4, 19, 19, 0),
                info_received_ps_date=datetime(2025, 4, 20, 9, 0),
                latitude=Decimal("12.9116"),
                longitude=Decimal("77.6474"),
                brief_facts="Complainant reports wallet stolen while boarding BMTC bus at HSR Layout bus stop. No witnesses identified. CCTV at bus stop non-functional at time of incident. Suspect description vague — male, medium build, dark clothing.",
            ))

            session.add(AccusedModel(
                accused_master_id=90003,
                case_master_id=90003,
                accused_name="Unknown Suspect",
                age_year=None,
                gender_id=1,
                person_id="DEMO-UNK-001",
            ))

            session.add(VictimModel(
                victim_master_id=90003,
                case_master_id=90003,
                victim_name="Kiran Bhat",
                age_year=34,
                gender_id=1,
                victim_police="0",
            ))

            session.add(CompModel(
                complainant_id=90003,
                case_master_id=90003,
                complainant_name="Kiran Bhat",
                age_year=34,
                occupation_id=4,
                religion_id=1,
                caste_id=1,
                gender_id=1,
            ))

            session.add(ActSectionModel(
                case_master_id=90003, act_id="IPC", section_id="IPC379",
                act_order_id=1, section_order_id=1,
            ))

            # No vehicle, ANPR, CDR, biometric, financial, or chargesheet
            # — deliberately sparse

            await session.flush()

            # ═══════════════════════════════════════════════════════
            # CASE 4 — Financial Crime (Money Trail)
            # 3 accused linked via FinancialTransaction records.
            # Fraud/Cheating category. No vehicle or CDR evidence.
            # ═══════════════════════════════════════════════════════

            session.add(CaseModel(
                case_master_id=90004,
                crime_no="010602025000100000",
                case_no="010600010",
                crime_registered_date=date(2025, 3, 5),
                police_person_id=1051,  # Electronic City PS officer
                police_station_id=106,
                case_category_id=1,
                gravity_offence_id=2,
                crime_major_head_id=4,   # Fraud
                crime_minor_head_id=8,   # Cheating
                case_status_id=1,        # Under Investigation
                court_id=3,
                incident_from_date=datetime(2024, 11, 1, 0, 0),
                incident_to_date=datetime(2025, 2, 28, 23, 59),
                info_received_ps_date=datetime(2025, 3, 5, 10, 0),
                latitude=Decimal("12.8399"),
                longitude=Decimal("77.6770"),
                brief_facts="Organized cheating scheme targeting IT professionals in Electronic City. Accused Deepak Kulkarni, Meena Patil, and Nagesh Rao operated fake investment platform 'CryptoYield Karnataka'. Total 18 victims defrauded of Rs 1.2 crore over 4 months. Bank statements show structured fund transfers between accused personal accounts.",
            ))

            # Three accused
            session.add(AccusedModel(
                accused_master_id=90004,
                case_master_id=90004,
                accused_name="Deepak Kulkarni",
                age_year=35,
                gender_id=1,
                person_id="DEMO-DEEPAK-001",
            ))
            session.add(AccusedModel(
                accused_master_id=90005,
                case_master_id=90004,
                accused_name="Meena Patil",
                age_year=29,
                gender_id=2,
                person_id="DEMO-MEENA-001",
            ))
            session.add(AccusedModel(
                accused_master_id=90006,
                case_master_id=90004,
                accused_name="Nagesh Rao",
                age_year=42,
                gender_id=1,
                person_id="DEMO-NAGESH-001",
            ))

            # Victims (representative sample)
            session.add(VictimModel(
                victim_master_id=90004,
                case_master_id=90004,
                victim_name="Anil Prasad",
                age_year=38,
                gender_id=1,
                victim_police="0",
            ))
            session.add(VictimModel(
                victim_master_id=90005,
                case_master_id=90004,
                victim_name="Shwetha Reddy",
                age_year=31,
                gender_id=2,
                victim_police="0",
            ))

            session.add(CompModel(
                complainant_id=90004,
                case_master_id=90004,
                complainant_name="Anil Prasad",
                age_year=38,
                occupation_id=4,
                religion_id=1,
                caste_id=1,
                gender_id=1,
            ))

            session.add(ActSectionModel(
                case_master_id=90004, act_id="IPC", section_id="IPC420",
                act_order_id=1, section_order_id=1,
            ))
            session.add(ActSectionModel(
                case_master_id=90004, act_id="IPC", section_id="IPC406",
                act_order_id=2, section_order_id=2,
            ))

            # Financial transactions — the money trail
            session.add(FinTxModel(
                financial_transaction_id=90001,
                from_accused_id=90004,   # Deepak -> Meena
                to_accused_id=90005,
                amount=Decimal("2500000"),
                transaction_date=datetime(2024, 12, 15, 14, 30),
            ))
            session.add(FinTxModel(
                financial_transaction_id=90002,
                from_accused_id=90005,   # Meena -> Nagesh
                to_accused_id=90006,
                amount=Decimal("1800000"),
                transaction_date=datetime(2025, 1, 10, 11, 0),
            ))
            session.add(FinTxModel(
                financial_transaction_id=90003,
                from_accused_id=90006,   # Nagesh -> Deepak (circular)
                to_accused_id=90004,
                amount=Decimal("750000"),
                transaction_date=datetime(2025, 2, 5, 16, 45),
            ))
            session.add(FinTxModel(
                financial_transaction_id=90004,
                from_accused_id=90004,   # Deepak -> Nagesh
                to_accused_id=90006,
                amount=Decimal("3200000"),
                transaction_date=datetime(2025, 2, 20, 9, 15),
            ))

            # AssociationEdge — financial links
            session.add(AssocEdgeModel(
                association_edge_id=90002,
                source_entity_type="Accused",
                source_entity_id=str(90004),
                target_entity_type="Accused",
                target_entity_id=str(90005),
                relationship_type_id=2,  # financial
                evidence="4 bank transfers totaling Rs 82.5 lakh between personal accounts; structured to avoid reporting thresholds",
            ))
            session.add(AssocEdgeModel(
                association_edge_id=90003,
                source_entity_type="Accused",
                source_entity_id=str(90005),
                target_entity_type="Accused",
                target_entity_id=str(90006),
                relationship_type_id=2,
                evidence="Rs 18 lakh transfer from Meena Patil SBI account to Nagesh Rao HDFC account",
            ))
            session.add(AssocEdgeModel(
                association_edge_id=90004,
                source_entity_type="Accused",
                source_entity_id=str(90006),
                target_entity_type="Accused",
                target_entity_id=str(90004),
                relationship_type_id=2,
                evidence="Rs 39.5 lakh circular transfer pattern between Nagesh Rao and Deepak Kulkarni",
            ))

            # Arrest — only the main accused arrested so far
            session.add(ArrestModel(
                arrest_surrender_id=90001,
                case_master_id=90004,
                arrest_surrender_type_id=1,
                arrest_surrender_date=date(2025, 3, 12),
                arrest_surrender_state_id=KARNATAKA_STATE_ID,
                arrest_surrender_district_id=1,
                police_station_id=106,
                io_id=1051,
                court_id=3,
                accused_master_id=90004,
                is_accused=True,
                is_complainant_accused=False,
            ))

            await session.flush()

            # ═══════════════════════════════════════════════════════
            # CASE 5 — Closed / Chargesheeted Case
            # Fully resolved assault case. Chargesheet filed,
            # case status = Chargesheeted. Complete evidence chain.
            # ═══════════════════════════════════════════════════════

            session.add(CaseModel(
                case_master_id=90005,
                crime_no="010102024000100000",
                case_no="010100010",
                crime_registered_date=date(2024, 8, 10),
                police_person_id=1001,  # Cubbon Park PS officer
                police_station_id=101,
                case_category_id=1,
                gravity_offence_id=1,
                crime_major_head_id=8,   # Assault
                crime_minor_head_id=19,  # Grievous hurt
                case_status_id=2,        # Chargesheeted
                court_id=1,
                incident_from_date=datetime(2024, 8, 9, 21, 0),
                incident_to_date=datetime(2024, 8, 9, 21, 30),
                info_received_ps_date=datetime(2024, 8, 9, 22, 0),
                latitude=Decimal("12.9716"),
                longitude=Decimal("77.5946"),
                brief_facts="Grievous assault outside restaurant on MG Road. Accused Prakash Gowda attacked victim with iron rod following verbal altercation. Victim sustained fracture to left forearm. Multiple eyewitnesses. Weapon recovered from scene. Accused arrested same night. Chargesheet filed.",
            ))

            session.add(AccusedModel(
                accused_master_id=90007,
                case_master_id=90005,
                accused_name="Prakash Gowda",
                age_year=33,
                gender_id=1,
                person_id="DEMO-PRAKASH-001",
            ))

            session.add(VictimModel(
                victim_master_id=90006,
                case_master_id=90005,
                victim_name="Santosh Murthy",
                age_year=29,
                gender_id=1,
                victim_police="0",
            ))

            session.add(CompModel(
                complainant_id=90005,
                case_master_id=90005,
                complainant_name="Santosh Murthy",
                age_year=29,
                occupation_id=4,
                religion_id=1,
                caste_id=1,
                gender_id=1,
            ))

            session.add(ActSectionModel(
                case_master_id=90005, act_id="IPC", section_id="IPC324",
                act_order_id=1, section_order_id=1,
            ))
            session.add(ActSectionModel(
                case_master_id=90005, act_id="IPC", section_id="IPC506",
                act_order_id=2, section_order_id=2,
            ))

            # Arrest
            session.add(ArrestModel(
                arrest_surrender_id=90002,
                case_master_id=90005,
                arrest_surrender_type_id=1,
                arrest_surrender_date=date(2024, 8, 9),
                arrest_surrender_state_id=KARNATAKA_STATE_ID,
                arrest_surrender_district_id=1,
                police_station_id=101,
                io_id=1001,
                court_id=1,
                accused_master_id=90007,
                is_accused=True,
                is_complainant_accused=False,
            ))

            # Chargesheet
            session.add(CSModel(
                cs_id=90001,
                case_master_id=90005,
                cs_date=datetime(2024, 10, 15, 0, 0),
                cs_type="A",
                police_person_id=1001,
            ))

            # Biometric — weapon fingerprint
            session.add(BioModel(
                biometric_match_id=90002,
                accused_master_id=90007,
                location_name="MG Road restaurant entrance",
                match_date_time=datetime(2024, 8, 10, 2, 30),
                match_type="fingerprint",
                confidence_score=Decimal("0.97"),
            ))

            await session.flush()

            # ═══════════════════════════════════════════════════════
            # CASE 6 — Repeat Offender With Priors
            # Ramesh Adiga linked to 3 separate historical cases
            # across different crime categories, with arrests.
            # ═══════════════════════════════════════════════════════

            RAMESH_PERSON_ID = "DEMO-RAMESH-001"

            # Case 6A — Assault (2023)
            session.add(CaseModel(
                case_master_id=90006,
                crime_no="010802023000100000",
                case_no="010800010",
                crime_registered_date=date(2023, 5, 20),
                police_person_id=1071,  # Jayanagar PS officer
                police_station_id=108,
                case_category_id=1,
                gravity_offence_id=2,
                crime_major_head_id=8,   # Assault
                crime_minor_head_id=20,  # Simple hurt
                case_status_id=2,        # Chargesheeted
                court_id=1,
                incident_from_date=datetime(2023, 5, 19, 20, 0),
                incident_to_date=datetime(2023, 5, 19, 20, 30),
                info_received_ps_date=datetime(2023, 5, 19, 21, 0),
                latitude=Decimal("12.9308"),
                longitude=Decimal("77.5839"),
                brief_facts="Bar fight at establishment in Jayanagar 4th Block. Accused Ramesh Adiga punched victim causing facial injuries. Accused had consumed alcohol. Arrested and released on bail.",
            ))

            # Case 6B — Theft (2024)
            session.add(CaseModel(
                case_master_id=90007,
                crime_no="010902024000100000",
                case_no="010900010",
                crime_registered_date=date(2024, 1, 12),
                police_person_id=1081,  # JP Nagar PS officer
                police_station_id=109,
                case_category_id=1,
                gravity_offence_id=2,
                crime_major_head_id=15,  # Motor Vehicle Theft
                crime_minor_head_id=27,  # Two-wheeler theft
                case_status_id=2,        # Chargesheeted
                court_id=2,
                incident_from_date=datetime(2024, 1, 11, 2, 0),
                incident_to_date=datetime(2024, 1, 11, 5, 0),
                info_received_ps_date=datetime(2024, 1, 12, 8, 0),
                latitude=Decimal("12.9050"),
                longitude=Decimal("77.5850"),
                brief_facts="Two-wheeler stolen from apartment parking in JP Nagar. CCTV footage shows accused Ramesh Adiga breaking steering lock and riding away. Vehicle recovered 3 days later in Banashankari. Accused arrested.",
            ))

            # Case 6C — Robbery (2025, current)
            session.add(CaseModel(
                case_master_id=90008,
                crime_no="011002025000100000",
                case_no="011000010",
                crime_registered_date=date(2025, 5, 1),
                police_person_id=1091,  # Marathahalli PS officer
                police_station_id=110,
                case_category_id=1,
                gravity_offence_id=1,
                crime_major_head_id=2,   # Robbery
                crime_minor_head_id=3,   # Armed robbery
                case_status_id=1,        # Under Investigation
                court_id=3,
                incident_from_date=datetime(2025, 4, 30, 23, 0),
                incident_to_date=datetime(2025, 4, 30, 23, 30),
                info_received_ps_date=datetime(2025, 5, 1, 0, 15),
                latitude=Decimal("12.9591"),
                longitude=Decimal("77.7009"),
                brief_facts="Armed robbery at ATM kiosk in Marathahalli. Accused Ramesh Adiga threatened victim with knife, took Rs 20,000 cash. Suspect identified from ATM camera footage matching prior records. Two-wheeler used in escape sighted on ANPR near Whitefield. Accused has 2 prior cases — assault in Jayanagar (2023) and vehicle theft in JP Nagar (2024).",
            ))

            # Accused records — same person_id links all three
            session.add(AccusedModel(
                accused_master_id=90008,
                case_master_id=90006,
                accused_name="Ramesh Adiga",
                age_year=31,
                gender_id=1,
                person_id=RAMESH_PERSON_ID,
            ))
            session.add(AccusedModel(
                accused_master_id=90009,
                case_master_id=90007,
                accused_name="Ramesh Adiga",
                age_year=32,
                gender_id=1,
                person_id=RAMESH_PERSON_ID,
            ))
            session.add(AccusedModel(
                accused_master_id=90010,
                case_master_id=90008,
                accused_name="Ramesh Adiga",
                age_year=33,
                gender_id=1,
                person_id=RAMESH_PERSON_ID,
            ))

            # Victims
            session.add(VictimModel(
                victim_master_id=90007,
                case_master_id=90006,
                victim_name="Girish Nayak",
                age_year=27,
                gender_id=1,
                victim_police="0",
            ))
            session.add(VictimModel(
                victim_master_id=90008,
                case_master_id=90007,
                victim_name="Vidya Acharya",
                age_year=30,
                gender_id=2,
                victim_police="0",
            ))
            session.add(VictimModel(
                victim_master_id=90009,
                case_master_id=90008,
                victim_name="Harish Swamy",
                age_year=35,
                gender_id=1,
                victim_police="0",
            ))

            # Complainants
            session.add(CompModel(
                complainant_id=90006,
                case_master_id=90006,
                complainant_name="Girish Nayak",
                age_year=27,
                occupation_id=4,
                religion_id=1,
                caste_id=1,
                gender_id=1,
            ))
            session.add(CompModel(
                complainant_id=90007,
                case_master_id=90007,
                complainant_name="Vidya Acharya",
                age_year=30,
                occupation_id=8,
                religion_id=1,
                caste_id=2,
                gender_id=2,
            ))
            session.add(CompModel(
                complainant_id=90008,
                case_master_id=90008,
                complainant_name="Harish Swamy",
                age_year=35,
                occupation_id=2,
                religion_id=1,
                caste_id=1,
                gender_id=1,
            ))

            # Act/Section associations
            session.add(ActSectionModel(
                case_master_id=90006, act_id="IPC", section_id="IPC323",
                act_order_id=1, section_order_id=1,
            ))
            session.add(ActSectionModel(
                case_master_id=90007, act_id="IPC", section_id="IPC379",
                act_order_id=1, section_order_id=1,
            ))
            session.add(ActSectionModel(
                case_master_id=90008, act_id="IPC", section_id="IPC392",
                act_order_id=1, section_order_id=1,
            ))

            # Arrests for Case 6A and 6B (not yet for 6C)
            session.add(ArrestModel(
                arrest_surrender_id=90003,
                case_master_id=90006,
                arrest_surrender_type_id=1,
                arrest_surrender_date=date(2023, 5, 20),
                arrest_surrender_state_id=KARNATAKA_STATE_ID,
                arrest_surrender_district_id=1,
                police_station_id=108,
                io_id=1071,
                court_id=1,
                accused_master_id=90008,
                is_accused=True,
                is_complainant_accused=False,
            ))
            session.add(ArrestModel(
                arrest_surrender_id=90004,
                case_master_id=90007,
                arrest_surrender_type_id=1,
                arrest_surrender_date=date(2024, 1, 15),
                arrest_surrender_state_id=KARNATAKA_STATE_ID,
                arrest_surrender_district_id=1,
                police_station_id=109,
                io_id=1081,
                court_id=2,
                accused_master_id=90009,
                is_accused=True,
                is_complainant_accused=False,
            ))

            # Chargesheets for Cases 6A and 6B
            session.add(CSModel(
                cs_id=90002,
                case_master_id=90006,
                cs_date=datetime(2023, 7, 25, 0, 0),
                cs_type="A",
                police_person_id=1071,
            ))
            session.add(CSModel(
                cs_id=90003,
                case_master_id=90007,
                cs_date=datetime(2024, 3, 20, 0, 0),
                cs_type="A",
                police_person_id=1081,
            ))

            # Vehicle for Case 6C — suspect's bike
            session.add(FIRVehicleModel(
                vehicle_id=90002,
                registration_number="KA05EF7890",
                owner_accused_id=90010,
                active=True,
            ))

            # ANPR for Case 6C
            session.add(ANPRSightModel(
                anpr_sighting_id=90003,
                vehicle_id=90002,
                camera_location="Marathahalli Bridge ANPR",
                sighting_date_time=datetime(2025, 4, 30, 23, 10),
                latitude=Decimal("12.9591"),
                longitude=Decimal("77.7009"),
            ))
            session.add(ANPRSightModel(
                anpr_sighting_id=90004,
                vehicle_id=90002,
                camera_location="Whitefield ITPL Road ANPR",
                sighting_date_time=datetime(2025, 4, 30, 23, 35),
                latitude=Decimal("12.9698"),
                longitude=Decimal("77.7500"),
            ))

            # CDR for Case 6C
            session.add(CDRRecModel(
                cdr_record_id=90003,
                accused_master_id=90010,
                cell_tower_id=4,  # Whitefield
                call_date_time=datetime(2025, 4, 30, 23, 5),
                duration_seconds=30,
                connected_accused_id=None,
            ))

            # Biometric — ATM camera face match
            session.add(BioModel(
                biometric_match_id=90003,
                accused_master_id=90010,
                location_name="SBI ATM Marathahalli",
                match_date_time=datetime(2025, 5, 1, 10, 0),
                match_type="facial_recognition",
                confidence_score=Decimal("0.89"),
            ))

            # AssociationEdge — repeat offender links
            session.add(AssocEdgeModel(
                association_edge_id=90005,
                source_entity_type="Accused",
                source_entity_id=str(90008),
                target_entity_type="Accused",
                target_entity_id=str(90009),
                relationship_type_id=4,  # cross-case-identity
                evidence="Same person_id DEMO-RAMESH-001; prior arrest record",
            ))
            session.add(AssocEdgeModel(
                association_edge_id=90006,
                source_entity_type="Accused",
                source_entity_id=str(90009),
                target_entity_type="Accused",
                target_entity_id=str(90010),
                relationship_type_id=4,
                evidence="Same person_id DEMO-RAMESH-001; escalating crime severity pattern",
            ))
            session.add(AssocEdgeModel(
                association_edge_id=90007,
                source_entity_type="Accused",
                source_entity_id=str(90008),
                target_entity_type="Accused",
                target_entity_id=str(90010),
                relationship_type_id=4,
                evidence="Same person_id DEMO-RAMESH-001; 3 cases over 2 years",
            ))

            await session.flush()

    print("✓ Seeded 6 handcrafted demo cases (Cases 1–6)")
    print("  Case 1: Vikram Hegde — syndicate lead with vehicle/CDR links")
    print("  Case 2: Sunil Jadhav — cross-district repeat (Bengaluru + Mysuru)")
    print("  Case 3: Unknown suspect — weak/circumstantial evidence")
    print("  Case 4: Deepak Kulkarni / Meena Patil / Nagesh Rao — financial crime")
    print("  Case 5: Prakash Gowda — closed/chargesheeted assault")
    print("  Case 6: Ramesh Adiga — repeat offender (3 cases, escalating)")


async def create_tables() -> None:
    """Create all tables (for dev without Alembic)."""
    from app.database import engine
    from app.models import Base  # noqa: F811

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main() -> None:
    print("Creating tables...")
    await create_tables()
    print("Seeding database...")
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
