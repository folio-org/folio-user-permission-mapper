#!/usr/bin/env python
import json

import click

from folio_upm.dto.results import AnalysisResult, OkapiLoadResult
from folio_upm.integration.services.eureka_migration_service import EurekaMigrationService
from folio_upm.services.load_result_analyzer import LoadResultAnalyzer
from folio_upm.services.loaders.capabilities_loader import CapabilitiesLoader
from folio_upm.services.loaders.eureka_result_loader import EurekaResultLoader
from folio_upm.services.loaders.permission_loader import PermissionLoader
from folio_upm.storage.tenant_storage_service import TenantStorageService
from folio_upm.utils import log_factory
from folio_upm.utils.system_roles_provider import SystemRolesProvider
from folio_upm.utils.upm_env import Env
from folio_upm.xlsx.migration_result_service import MigrationResultService
from folio_upm.xlsx.xlsx_report_provider import XlsxReportProvider

xlsx_ext = "xlsx"
json_gz_ext = "json.gz"
okapi_permissions_fn = "okapi-permissions"
eureka_capabilities_fn = "eureka-capabilities"
mixed_analysis_result_fn = "analysis-result"
eureka_migration_result_fn = "migration-result"


_log = log_factory.get_logger("cli.py")


@click.group()
def cli():
    """A simple CLI tool."""
    pass


@cli.command("collect-permissions")
def collect_permissions():
    storage_service = TenantStorageService()
    perms_load_result = PermissionLoader().load_permission_data()
    storage_service.save_object(okapi_permissions_fn, json_gz_ext, perms_load_result)


@cli.command("collect-capabilities")
def collect_capabilities():
    storage_service = TenantStorageService()
    capability_load_result = CapabilitiesLoader().load_capabilities()
    storage_service.save_object(eureka_capabilities_fn, json_gz_ext, capability_load_result)


@cli.command("generate-report")
def generate_report():
    migration_strategy = Env().get_migration_strategy()
    strategy_name = migration_strategy
    _log.info("Generating report for strategy: %s ...", strategy_name)
    SystemRolesProvider().print_system_roles()

    storage_service = TenantStorageService()
    okapi_load_result = OkapiLoadResult(**storage_service.require_object(okapi_permissions_fn, json_gz_ext))
    eureka_load_result = EurekaResultLoader().get_load_result()
    analysis_result = LoadResultAnalyzer(okapi_load_result, eureka_load_result).get_results()
    workbook = XlsxReportProvider(analysis_result).generate_report()

    result_fn = f"{mixed_analysis_result_fn}-{strategy_name}"
    storage_service.save_object(result_fn, xlsx_ext, workbook, include_ts=True)
    storage_service.save_object(result_fn, json_gz_ext, analysis_result.model_dump())
    _log.info("Report is successfully generated for strategy: %s", strategy_name)


@cli.command("run-eureka-migration")
def run_eureka_migration():
    migration_strategy = Env().get_migration_strategy()
    _log.info("Running eureka migration for strategy: %s ...", migration_strategy.get_name())
    result_fn = f"{mixed_analysis_result_fn}-{migration_strategy.get_name()}"
    storage_service = TenantStorageService()
    analysis_result_dict = storage_service.require_object(result_fn, json_gz_ext)
    analysis_result = AnalysisResult(**analysis_result_dict)
    migration_result = EurekaMigrationService().migrate_to_eureka(analysis_result)
    migration_result_report = MigrationResultService(migration_result).generate_report()
    storage_service.save_object(eureka_migration_result_fn, json_gz_ext, migration_result.model_dump())
    storage_service.save_object(eureka_migration_result_fn, xlsx_ext, migration_result_report, include_ts=True)


@cli.command("download-json")
@click.argument("source_file", type=str)
@click.argument("out_file", type=str)
def download_json(source_file, out_file):
    storage_service = TenantStorageService()
    analysis_result_dict = storage_service.get_ref_object_by_key(source_file)
    if analysis_result_dict is None:
        raise FileNotFoundError(f"File not found: {source_file}")
    with open(out_file, "w") as f:
        json.dump(analysis_result_dict, f, indent=2)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        _log.error(e, exc_info=True)
        _log.error("Command execution finished with error: %s", e)
