from pyqure.injection import component
from tests.examples.adapters.items import VaccineItem
from tests.examples.adapters.mapper import VaccineMapper
from tests.examples.domain.exceptions import MedicalException
from tests.examples.domain.models.patient import Patient, Vaccine
from tests.examples.domain.port.medical_repository import MedicalRepository


@component
class InMemoryMedicalRepository(MedicalRepository):
    def __init__(
        self, mapper: VaccineMapper, data: dict[str, list[VaccineItem]] | None = None
    ) -> None:
        self.data = data or {}
        self.mapper = mapper

    def get_vaccines(self, patient: Patient) -> list[Vaccine]:
        if vaccine_items := self.data.get(patient.social_id):
            return [self.mapper.to_domain(item) for item in vaccine_items]

        raise MedicalException(f"No records found for the patient#{patient.social_id}!")
