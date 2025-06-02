import typing
from collections import OrderedDict
from typing import List, Optional

from dto.models import AnalysisReport, AnalysisResult, Permission


def analyze_results(analysis_json: dict) -> AnalysisResult:
    report = AnalysisReport(**analysis_json)

    return AnalysisResult(
        permissionSets=__get_mutable_permission_descriptors(report),
        permissionSetsNesting=__get_mutable_permission_set_nesting(report),
        usersPermissionSets=__get_user_permission_sets(report),
        permissionSetUsers=____get_permission_set_users(report),
        permissionPermissionSets=__get_permission_set_permission_sets(report),
    )

def __get_mutable_permission_descriptors(report: AnalysisReport) -> typing.OrderedDict[str, Permission]:
    result = OrderedDict()
    for permission in report.allPermissions:
        mutable = permission.mutable
        if mutable:
            result[permission.permissionName] = permission
    return result


def __get_mutable_permission_set_nesting(report: AnalysisReport) -> typing.OrderedDict[str, List[str]]:
    result = OrderedDict()
    for permission in report.allPermissions:
        if not permission.mutable:
            continue
        permission_name = permission.permissionName
        parent_permissions_names = permission.childOf
        result[permission_name] = []
        for parent_permission_name in parent_permissions_names:
            result[permission_name].append(parent_permission_name)
    return result


def __get_user_permission_sets(report: AnalysisReport) -> typing.OrderedDict[str, List[str]]:
    result = OrderedDict()
    mutable_permission_names = __get_mutable_permission_names(report)
    permission_users = report.allPermissionUsers
    for permission_user in permission_users:
        user_permissions = []
        user_id = permission_user.userId
        for permission in permission_user.permissions:
            if permission in mutable_permission_names:
                user_permissions.append(permission)
        result[user_id] = user_permissions
    return result


def __get_permission_set_permission_sets(report: AnalysisReport) -> typing.OrderedDict[str, List[str]]:
    result = OrderedDict()
    for permission in report.allPermissions:
        permission_name = permission.permissionName
        sub_permissions = permission.subPermissions
        if permission_name.startswith('SYS#'):
            continue
        else:
            result[permission_name] = sub_permissions
    return result


def ____get_permission_set_users(report: AnalysisReport) -> typing.OrderedDict[str, List[str]]:
    result = OrderedDict()
    mutable_permission_names = __get_mutable_permission_names(report)
    for permission in report.allPermissions:
        permission_name = permission.permissionName
        if permission_name not in mutable_permission_names:
            continue
        if permission.assignedUserIds:
            result[permission_name] = permission.assignedUserIds
    return result


def __get_mutable_permission_names(report: AnalysisReport):
    mutable_permissions = report.allPermissions
    return set([x.permissionName for x in mutable_permissions if x.mutable])

