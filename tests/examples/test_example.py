from tests.examples.app.run import Handler, is_up_to_date
from tests.examples.domain.models.patient import Patient, SocialId


def test_is_up_to_date() -> None:
    patient_a = Patient("Bob", "Smith", SocialId("0976543215"))
    assert is_up_to_date(patient=patient_a)

    patient_b = Patient("John", "Doe", SocialId("123456790"))
    assert not is_up_to_date(patient=patient_b)


def test_handler() -> None:
    patient_a = Patient("Bob", "Smith", SocialId("0976543215"))
    assert Handler().handle(patient_a)
