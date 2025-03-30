from pyqure.container import DependencyContainer, Key
from pyqure.injectables import Constant
from pyqure.injection import configuration
from tests.examples.adapters.items import VaccineItem


@configuration(autoload=True)
def config(container: DependencyContainer) -> None:
    container[Key(dict[str, list[VaccineItem]], "data")] = Constant(
        {
            "123456790": [
                VaccineItem(name="rabies", injection_date="1999-04-17", recall_date="2024-04-17"),
                VaccineItem(name="tetanus", injection_date="2000-05-24", recall_date="2025-05-17"),
            ],
            "0976543215": [
                VaccineItem(name="rabies", injection_date="1995-11-01", recall_date="2020-11-01"),
                VaccineItem(name="tetanus", injection_date="1999-04-17", recall_date="2024-04-17"),
            ],
        }
    )
