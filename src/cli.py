#!/usr/bin/env python
from collections import OrderedDict

import click

from integrations import s3_client
from services import okapi_service, permission_service, xslx_service
from utils import log_factory, env


@click.group()
def cli():
    """A simple CLI tool."""
    pass


def getOkapiDefinedPermissionNameSet(_okapiModuleDescriptors):
    _result = set()
    for _moduleDesc in _okapiModuleDescriptors:
        _permissionSets = _moduleDesc.get('permissionSets', [])
        for _perm in _permissionSets:
            _result.add(_perm.get('permissionName'))
    return _result


def _getUserIds(_accessToken, _permissions):
    _allGrantedTo = {}
    for _permission in _permissions:
        _grantedTo = _permission.get('grantedTo', [])
        _allGrantedTo += _grantedTo
    _uniqueValues = list(_allGrantedTo.keys())


_log = log_factory.get_logger(__name__)
configName = "all"


@cli.command("collect-permissions")
def collect_permissions():
    _log.info("Starting user permission loading...")
    okapi_permissions = okapi_service.get_okapi_defined_permissions()
    permissions = permission_service.load_all_permissions_by_query("mutable==true")
    permission_users = permission_service.load_permission_users(permissions)
    enriched_permissions = permission_service.enrich_permissions(permissions, permission_users)
    result_object = OrderedDict({
        'okapiPermissions': okapi_permissions,
        'mutablePermissions': enriched_permissions,
        'permissionUsers': permission_users,
    })

    path = f"{env.get_tenant_id()}/analysis-result.json"
    s3_client.put_json_object(path=path, data=result_object)
    _log.info("Permission loading finished successfully.")


@cli.command("generate-excel")
def generate_excel():
    path = f"{env.get_tenant_id()}/analysis-result.json"
    analysis_report = s3_client.read_json_object(path)
    xslx_report = xslx_service.generate_report(analysis_report)

    xlsx_path = f"{env.get_tenant_id()}/analysis-result.xlsx"
    s3_client.upload_file(xlsx_path, xslx_report)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        _log.error(f"Failed to execute CLI command: {e}")
        raise Exception(e)
