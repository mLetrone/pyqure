from dataclasses import dataclass
from datetime import date


class SocialId(str): ...


@dataclass
class Patient:
    first_name: str
    last_name: str
    social_id: SocialId


@dataclass
class Vaccine:
    name: str
    injection_date: date
    recall_date: date
