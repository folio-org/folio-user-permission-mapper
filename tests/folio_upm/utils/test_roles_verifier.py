from folio_upm.utils.roles_verifier import RoleLengthVerifier
from folio_upm.utils.utils import Utils


class TestRoleLengthVerifier:

    def test_valid_roles(self):
        verifier = RoleLengthVerifier()
        result = verifier.is_valid_amount_of_roles(["role1", "role2", "role3"])
        assert result is True

    def test_invalid_roles_count(self):
        verifier = RoleLengthVerifier()
        roles = [f"role-{Utils.random_string(50)}" for _ in range(100)]
        result = verifier.is_valid_amount_of_roles(roles)
        assert result is False

