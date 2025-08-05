from collections import OrderedDict

from folio_upm.model.analysis.analyzed_permission_set import AnalyzedPermissionSet
from folio_upm.model.okapi.permission_set import PermissionSet
from folio_upm.model.result.permission_analysis_result import PermissionAnalysisResult
from folio_upm.model.support.expanded_permission_set import ExpandedPermissionSet
from folio_upm.model.support.sourced_permission_set import SourcedPermissionSet
from folio_upm.model.types.source_type import PS
from folio_upm.utils.sub_ps_helper import SubPermissionsHelper


class TestSubPermissionsUtils:

    def test_get_sub_permissions_empty(self):
        sub_ps_helper = SubPermissionsHelper(self.simple_ps_analysis_result())
        expanded_ps = sub_ps_helper.expand_sub_ps("unknown")
        assert expanded_ps == []

    def test_get_sub_permissions(self):
        sub_ps_helper = SubPermissionsHelper(self.simple_ps_analysis_result())
        result = sub_ps_helper.expand_sub_ps("user_ps")

        assert result == [
            ExpandedPermissionSet(permissionName="okapi_set", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="okapi_perm", expandedFrom=[]),
        ]

    def test_nested_mutable_permissions(self):
        sub_ps_helper = SubPermissionsHelper(self.nested_user_ps_sets())

        result = sub_ps_helper.expand_sub_ps("user_ps1")
        assert result == [
            ExpandedPermissionSet(permissionName="okapi_ps1", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="user_ps2", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="user_ps3", expandedFrom=["user_ps1"]),
            ExpandedPermissionSet(permissionName="okapi_ps2", expandedFrom=["user_ps1"]),
            ExpandedPermissionSet(permissionName="okapi_ps3", expandedFrom=["user_ps1"]),
            ExpandedPermissionSet(permissionName="okapi_ps4", expandedFrom=["user_ps1"]),
        ]

        result2 = sub_ps_helper.expand_sub_ps("user_ps2")
        assert result2 == [
            ExpandedPermissionSet(permissionName="okapi_ps2", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="user_ps3", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="okapi_ps3", expandedFrom=["user_ps2"]),
            ExpandedPermissionSet(permissionName="okapi_ps4", expandedFrom=["user_ps2"]),
        ]

        result3 = sub_ps_helper.expand_sub_ps("user_ps3")
        assert result3 == [
            ExpandedPermissionSet(permissionName="okapi_ps3", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="okapi_ps4", expandedFrom=[]),
        ]

    def test_nested_ps_with_self_reference(self):
        sub_ps_helper = SubPermissionsHelper(self.ps_analys_result_with_self_ref())
        result = sub_ps_helper.expand_sub_ps("user_ps1")

        assert result == [
            ExpandedPermissionSet(permissionName="okapi_ps1", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="user_ps2", expandedFrom=["user_ps2"]),
            ExpandedPermissionSet(permissionName="user_ps1", expandedFrom=["user_ps1", "user_ps2"]),
            ExpandedPermissionSet(permissionName="user_ps3", expandedFrom=["user_ps1"]),
            ExpandedPermissionSet(permissionName="okapi_ps2", expandedFrom=["user_ps1"]),
            ExpandedPermissionSet(permissionName="okapi_ps3", expandedFrom=["user_ps2"]),
            ExpandedPermissionSet(permissionName="okapi_ps4", expandedFrom=["user_ps2"]),
        ]

    def test_nested_ps_with_unknown_ps_name(self):
        sub_ps_helper = SubPermissionsHelper(self.ps_analys_result_with_unknown_ps())
        result = sub_ps_helper.expand_sub_ps("user_ps1")

        assert result == [
            ExpandedPermissionSet(permissionName="okapi_ps1", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="unknown_ps", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="user_ps2", expandedFrom=[]),
            ExpandedPermissionSet(permissionName="okapi_ps2", expandedFrom=["user_ps1"]),
            ExpandedPermissionSet(permissionName="okapi_ps3", expandedFrom=["user_ps1"]),
        ]

    def simple_ps_analysis_result(self) -> PermissionAnalysisResult:
        user_set = self.ps_set("user_ps", "User-Defined Ps", ["okapi_set", "okapi_perm"])

        okapi_ps1 = self.ps_set("okapi_ps1", "Okapi PS #1", [])
        okapi_ps2 = self.ps_set("okapi_ps2", "Okapi PS #2", [])
        okapi_set = self.ps_set("ps1", "Okapi Permission Set", ["okapi_ps1", "okapi_ps2"])
        okapi_perm = self.ps_set("ps1", "Okapi Permission", [])

        return PermissionAnalysisResult(
            mutable=self.analyzed_ps_dict([user_set]),
            okapi=self.analyzed_ps_dict([okapi_ps1, okapi_ps2, okapi_set, okapi_perm]),
        )

    def nested_user_ps_sets(self) -> PermissionAnalysisResult:
        user_ps1 = self.ps_set("user_ps1", "User-Defined Ps", ["user_ps2", "okapi_ps1", "user_ps3"])
        user_ps2 = self.ps_set("user_ps2", "User-Defined Ps", ["user_ps3", "okapi_ps2"])
        user_ps3 = self.ps_set("user_ps3", "User-Defined Ps", ["okapi_ps3", "okapi_ps4"])

        okapi_ps1 = self.ps_set("okapi_ps1", "Okapi PS #1", [])
        okapi_ps2 = self.ps_set("okapi_ps2", "Okapi PS #2", [])
        okapi_ps3 = self.ps_set("okapi_ps3", "Okapi PS #3", [])

        return PermissionAnalysisResult(
            mutable=self.analyzed_ps_dict([user_ps1, user_ps2, user_ps3]),
            okapi=self.analyzed_ps_dict([okapi_ps1, okapi_ps2, okapi_ps3]),
        )

    def ps_analys_result_with_self_ref(self) -> PermissionAnalysisResult:
        user_ps1 = self.ps_set("user_ps1", "User-Defined Ps", ["user_ps1", "user_ps2", "okapi_ps1"])
        user_ps2 = self.ps_set("user_ps2", "User-Defined Ps", ["user_ps1", "user_ps3", "okapi_ps2"])
        user_ps3 = self.ps_set("user_ps3", "User-Defined Ps", ["user_ps1", "okapi_ps3", "okapi_ps4"])

        okapi_ps1 = self.ps_set("okapi_ps1", "Okapi PS #1", [])
        okapi_ps2 = self.ps_set("okapi_ps2", "Okapi PS #2", [])
        okapi_ps3 = self.ps_set("okapi_ps3", "Okapi PS #3", [])

        return PermissionAnalysisResult(
            mutable=self.analyzed_ps_dict([user_ps1, user_ps2, user_ps3]),
            okapi=self.analyzed_ps_dict([okapi_ps1, okapi_ps2, okapi_ps3]),
        )

    def ps_analys_result_with_unknown_ps(self) -> PermissionAnalysisResult:
        user_ps1 = self.ps_set("user_ps1", "User-Defined Ps", ["user_ps2", "okapi_ps1", "unknown_ps"])
        user_ps2 = self.ps_set("user_ps2", "User-Defined Ps", ["okapi_ps2", "okapi_ps3", "unknown_ps"])

        okapi_ps1 = self.ps_set("okapi_ps1", "Okapi PS #1", [])
        okapi_ps2 = self.ps_set("okapi_ps2", "Okapi PS #2", [])
        okapi_ps3 = self.ps_set("okapi_ps3", "Okapi PS #3", [])

        return PermissionAnalysisResult(
            mutable=self.analyzed_ps_dict([user_ps1, user_ps2]),
            okapi=self.analyzed_ps_dict([okapi_ps1, okapi_ps2, okapi_ps3]),
        )

    @staticmethod
    def print_result(expanded_ps: list[ExpandedPermissionSet]):
        print()
        for v in expanded_ps:
            print(f'ExpandedPermissionSet(permissionName="{v.permissionName}", expandedFrom={v.expandedFrom}),')

    @staticmethod
    def analyzed_ps(value: PermissionSet) -> AnalyzedPermissionSet:
        return AnalyzedPermissionSet(
            permissionName=value.permissionName,
            sourcePermSets=[SourcedPermissionSet(src=PS, val=value)],
        )

    @staticmethod
    def analyzed_ps_dict(analyzed_ps_list: list[PermissionSet]) -> OrderedDict[str, AnalyzedPermissionSet]:
        return OrderedDict({ap.permissionName: TestSubPermissionsUtils.analyzed_ps(ap) for ap in analyzed_ps_list})

    @staticmethod
    def ps_set(name: str, display_name=None, sub_permissions=None) -> PermissionSet:
        if sub_permissions is None:
            sub_permissions = []
        return PermissionSet(
            permissionName=name,
            displayName=display_name,
            subPermissions=sub_permissions,
        )
