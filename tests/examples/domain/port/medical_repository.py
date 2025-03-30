from abc import ABC, abstractmethod

from tests.examples.domain.models.patient import Patient, Vaccine


class MedicalRepository(ABC):
    @abstractmethod
    def get_vaccines(self, patient: Patient) -> list[Vaccine]:
        """Get patient's vaccines."""
