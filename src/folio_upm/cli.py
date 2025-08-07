#!/usr/bin/env python
import json

import click

from folio_upm.integration.services.eureka_cleanup_service import EurekaCleanupService
from folio_upm.integration.services.eureka_migration_service import EurekaMigrationService
from folio_upm.model.cleanup.hash_role_cleanup_record import HashRoleCleanupRecord
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.model.load.okapi_load_result import OkapiLoadResult
from folio_upm.model.report.eureka_migration_report import EurekaMigrationReport
from folio_upm.model.report.hash_roles_cleanup_report import HashRolesCleanupReport
from folio_upm.model.result.eureka_migration_data import EurekaMigrationData
from folio_upm.services.eureka_hash_role_analyzer import EurekaHashRoleAnalyzer
from folio_upm.services.load_result_analyzer import LoadResultAnalyzer
from folio_upm.services.loaders.capabilities_loader import CapabilitiesLoader
from folio_upm.services.loaders.eureka_data_loader import EurekaDataLoader
from folio_upm.services.loaders.okapi_data_loader import OkapiDataLoader
from folio_upm.services.ps_details_service import PermissionDetailsService
from folio_upm.storage.tenant_storage_service import TenantStorageService
from folio_upm.utils import log_factory
from folio_upm.utils.system_roles_provider import SystemRolesProvider
from folio_upm.utils.upm_env import Env
from folio_upm.xlsx.cleanup_process_report_service import CleanupProcessReportProvider
from folio_upm.xlsx.eureka_report_provider import EurekaReportProvider
from folio_upm.xlsx.migration_process_report_provider import MigrationProcessReportProvider
from folio_upm.xlsx.okapi_analysis_report_provider import OkapiAnalysisReportProvider

xlsx_ext = "xlsx"
json_gz_ext = "json.gz"

okapi_permissions_fn = "okapi-permissions"
eureka_capabilities_fn = "eureka-capabilities"

okapi_analysis_result_fn = "okapi-analysis-result"
eureka_migration_data_fn = "eureka-migration-data"
migration_result_fn = "migration-report"

eureka_migrated_data_fn = "eureka-migrated-data"
hash_roles_analysis_result_fn = "hash-roles-analysis-result"
hash_roles_cleanup_data_fn = "hash-roles-cleanup-data"
hash_roles_cleanup_report_fn = "hash-roles-cleanup-report"


_log = log_factory.get_logger("cli.py")


@click.group()
def cli():
    """A simple CLI tool."""
    pass


@cli.command("collect-permissions")
def collect_permissions():
    storage_service = TenantStorageService()
    perms_load_result = OkapiDataLoader().load_okapi_data()
    storage_service.save_object(okapi_permissions_fn, json_gz_ext, perms_load_result)


@cli.command("collect-capabilities")
def collect_capabilities():
    __collect_capabilities(eureka_capabilities_fn)


@cli.command("generate-report")
def generate_report():
    migration_strategy = Env().get_migration_strategy()
    strategy_name = migration_strategy.get_name()
    _log.info("Generating report for strategy: %s ...", strategy_name)
    SystemRolesProvider().print_system_roles()

    storage_service = TenantStorageService()
    okapi_permissions_dict = storage_service.require_object(okapi_permissions_fn, json_gz_ext)
    okapi_load_result = OkapiLoadResult(**okapi_permissions_dict)
    eureka_load_result = EurekaDataLoader().find_load_result()
    load_result_analyzer = LoadResultAnalyzer(okapi_load_result, eureka_load_result)
    analysis_result = load_result_analyzer.get_results()

    okapi_analysis_fn = f"{okapi_analysis_result_fn}-{strategy_name}"
    okapi_xlsx_analysis_result = OkapiAnalysisReportProvider(analysis_result).generate()
    storage_service.save_object(okapi_analysis_fn, xlsx_ext, okapi_xlsx_analysis_result)

    eureka_data_fn = f"{eureka_migration_data_fn}-{strategy_name}"
    eureka_migration_data = load_result_analyzer.get_eureka_migration_data()
    storage_service.save_object(eureka_data_fn, json_gz_ext, eureka_migration_data.model_dump(by_alias=True))
    _log.info("Report is successfully generated for strategy: %s", strategy_name)


@cli.command("run-eureka-migration")
def run_eureka_migration():
    strategy_name = Env().get_migration_strategy().get_name()
    _log.info("Running eureka migration for strategy: %s ...", strategy_name)

    _eureka_migration_data_fn = f"{eureka_migration_data_fn}-{strategy_name}"
    storage_service = TenantStorageService()
    eureka_migration_data_dict = storage_service.require_object(_eureka_migration_data_fn, json_gz_ext)
    migration_data = EurekaMigrationData(**eureka_migration_data_dict)
    migration_report = EurekaMigrationService().migrate_to_eureka(migration_data)

    _migration_result_fn = f"{migration_result_fn}-{strategy_name}"
    storage_service.save_object(_migration_result_fn, json_gz_ext, migration_report.model_dump(by_alias=True))
    _log.info("Eureka migration successfully finished for strategy: %s", strategy_name)


@cli.command("generate-eureka-migration-report")
def generate_migration_report():
    _log.info("Generating migration report ...")
    strategy_name = Env().get_migration_strategy().get_name()
    storage_service = TenantStorageService()
    _migration_result_fn = f"{migration_result_fn}-{strategy_name}"
    raw_migration_report = storage_service.require_object(_migration_result_fn, json_gz_ext)
    migration_report = EurekaMigrationReport(**raw_migration_report)
    migration_xlsx_report = MigrationProcessReportProvider(migration_report).generate()
    storage_service.save_object(_migration_result_fn, json_gz_ext, migration_xlsx_report)
    _log.info("Migration report successfully generated for strategy: %s", strategy_name)


@cli.command("analyze-hash-roles")
@click.option("--force-reload", is_flag=True, default=False, help="Force reloading of eureka capabilities.")
def analyze_hash_roles(force_reload: bool):
    strategy_name = Env().get_migration_strategy().get_name()
    storage_service = TenantStorageService()
    _log.info("Analyzing hash-role capabilities for: %s", strategy_name)
    _migrated_eureka_data_fn = f"{eureka_migrated_data_fn}-{strategy_name}"

    if force_reload:
        eureka_load_rs = __collect_capabilities(_migrated_eureka_data_fn)
    else:
        eureka_rs_loader = EurekaDataLoader(use_ref_file=False, src_file_name=_migrated_eureka_data_fn)
        eureka_load_rs = eureka_rs_loader.find_load_result()
        if eureka_load_rs is None:
            eureka_load_rs = __collect_capabilities(_migrated_eureka_data_fn)

    hash_role_analysis_result = EurekaHashRoleAnalyzer(eureka_load_rs).get_result()
    hash_role_xlsx_analysis_result = EurekaReportProvider(hash_role_analysis_result).generate()
    xlsx_analysis_result_fn = f"{hash_roles_analysis_result_fn}-{strategy_name}"
    storage_service.save_object(xlsx_analysis_result_fn, xlsx_ext, hash_role_xlsx_analysis_result)

    cleanup_records = HashRoleCleanupRecord.get_records_from_analysis_result(hash_role_analysis_result)
    cleanup_records_dicts = [x.model_dump(by_alias=True) for x in cleanup_records]
    _hash_roles_cleanup_data_fn = f"{hash_roles_cleanup_data_fn}-{strategy_name}"
    storage_service.save_object(_hash_roles_cleanup_data_fn, json_gz_ext, cleanup_records_dicts)
    _log.info("Hash-Roles analysis successfully finished for strategy: %s", strategy_name)


@cli.command("cleanup-hash-roles")
def clean_hash_roles():
    migration_strategy = Env().get_migration_strategy()
    strategy_name = migration_strategy.get_name()
    _log.info("Cleaning hash roles for strategy: %s ...", strategy_name)

    storage_service = TenantStorageService()
    _hash_roles_cleanup_data_fn = f"{hash_roles_cleanup_data_fn}-{strategy_name}"
    hash_role_raw_cleanup_records = storage_service.require_object(_hash_roles_cleanup_data_fn, json_gz_ext)
    hash_role_cleanup_records = [HashRoleCleanupRecord(**x) for x in hash_role_raw_cleanup_records]
    cleanup_service = EurekaCleanupService(hash_role_cleanup_records)
    hash_role_cleanup_report = cleanup_service.perform_cleanup()

    result_fn = f"{hash_roles_cleanup_report_fn}-{strategy_name}"
    storage_service.save_object(result_fn, json_gz_ext, hash_role_cleanup_report.model_dump(by_alias=True))
    _log.info("Hash-Roles cleanup successfully finished for strategy: %s", strategy_name)


@cli.command("generate-cleanup-report")
def generate_cleanup_report():
    _log.info("Generating cleanup report...")
    strategy_name = Env().get_migration_strategy().get_name()
    storage_service = TenantStorageService()
    cleanup_report_fm = f"{hash_roles_cleanup_report_fn}-{strategy_name}"
    raw_cleanup_report = storage_service.require_object(cleanup_report_fm, json_gz_ext)
    cleanup_report = HashRolesCleanupReport(**raw_cleanup_report)
    migration_xlsx_report = CleanupProcessReportProvider(cleanup_report).generate()
    storage_service.save_object(cleanup_report_fm, json_gz_ext, migration_xlsx_report)
    _log.info("Cleanup report successfully generated for strategy: %s", strategy_name)


@cli.command("download-json")
@click.argument("source_file", type=str)
@click.argument("out_file", type=str)
def download_json(source_file, out_file):
    storage_service = TenantStorageService()
    analysis_result_dict = storage_service.find_object_by_key(source_file)
    if analysis_result_dict is None:
        raise FileNotFoundError(f"File not found: {source_file}")
    with open(out_file, "w") as f:
        json.dump(analysis_result_dict, f, indent=2)


@cli.command("explain-permissions")
@click.option("--name", "-n", type=str, default=None, help="Name of the permission to explain")
@click.option("--file", "-f", type=str, default=None, help="File containing permission names to explain")
def explain_permissions(name, file):
    """Explain a permission by its name."""
    _log.info("Explaining permission: %s", name)
    storage_service = TenantStorageService()
    okapi_load_result_dict = storage_service.require_object(okapi_permissions_fn, json_gz_ext)
    okapi_load_result = OkapiLoadResult(**okapi_load_result_dict)
    pd_service = PermissionDetailsService(okapi_load_result)
    if name:
        _log.info("Explaining permissions by file name: %s", file)
        pd_service.print_explained_permission_set(name)
        return

    if file:
        _log.info("Loading permission names from file: %s", file)
        with open(file, "r") as f:
            for line in f:
                pd_service.print_explained_permission_set(line)
        return


def __collect_capabilities(result_fn: str) -> EurekaLoadResult:
    storage_service = TenantStorageService()
    capability_load_result = CapabilitiesLoader().load_capabilities()
    storage_service.save_object(result_fn, json_gz_ext, capability_load_result)
    return EurekaLoadResult(**capability_load_result)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        if Env().get_bool_cached("LOG_ERROR_STACKTRACE", False):
            _log.error(e, exc_info=True)
        else:
            _log.error(e)
