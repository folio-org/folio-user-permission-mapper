import pytest

from utils.json_stub_loader import JsonStubLoader


@pytest.fixture
def stub_loader():
    """Provides JsonStubLoader utility"""
    return JsonStubLoader()

@pytest.fixture
def mock_okapi():
    """Provides MockOkapiResponses utility"""
    return MockOkapiResponses()

@pytest.fixture
def sample_modules_from_json(stub_loader):
    """Load sample modules from JSON file"""
    return stub_loader.load_okapi_modules()

@pytest.fixture
def sample_permissions_from_json(stub_loader):
    """Load sample permissions from JSON file"""
    return stub_loader.load_okapi_permissions()
