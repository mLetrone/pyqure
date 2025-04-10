from datetime import datetime

from pyqure.injection import inject
from tests.examples.domain.models.patient import Patient
from tests.examples.domain.port.medical_repository import MedicalRepository


@inject
def is_up_to_date(repository: MedicalRepository, patient: Patient) -> bool:
    vaccines = repository.get_vaccines(patient)

    return all(vaccine.recall_date < datetime.now() for vaccine in vaccines)
