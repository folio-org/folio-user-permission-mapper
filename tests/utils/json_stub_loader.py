import json
from pathlib import Path
from typing import Dict, Any, List

class JsonStubLoader:
    """Utility for loading JSON stub files for tests"""

    def __init__(self, stub_base_path: str = "tests/resources/stubs"):
        self.base_path = Path(stub_base_path)

    def load_json(self, file_path: str) -> Dict[str, Any] | List[Dict[str, Any]]:
        """Load JSON data from stub file"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"Stub file not found: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_okapi_modules(self, filename: str = "module-descriptors.json") -> List[Dict[str, Any]]:
        """Load module descriptors from okapi stubs"""
        return self.load_json(f"okapi/mod-permissions/{filename}")

    def load_okapi_permissions(self, filename: str = "permission-sets.json") -> List[Dict[str, Any]]:
        """Load permission sets from okapi stubs"""
        return self.load_json(f"okapi/mod-permissions/{filename}")

    def get_stub_path(self, relative_path: str) -> Path:
        """Get full path to stub file"""
        return self.base_path / relative_path
