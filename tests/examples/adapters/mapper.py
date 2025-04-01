from datetime import datetime

from pyqure import component
from tests.examples.adapters.items import VaccineItem
from tests.examples.domain.models.patient import Vaccine


@component
class VaccineMapper:
    def to_domain(self, item: VaccineItem) -> Vaccine:
        return Vaccine(
            name=item["name"],
            injection_date=datetime.fromisoformat(item["injection_date"]),
            recall_date=datetime.fromisoformat(item["recall_date"]),
        )
