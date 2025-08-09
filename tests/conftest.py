import pytest

from folio_upm.model.cls_support import SingletonMeta


@pytest.fixture(scope="class")
def clear_singletons():
    SingletonMeta._instances.clear()
    yield
    SingletonMeta._instances.clear()
