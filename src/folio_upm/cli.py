#!/usr/bin/env python
from typing import Tuple

import click

from folio_upm.dto.results import AnalysisResult
from folio_upm.dto.strategy_type import StrategyType
from folio_upm.integration.services.eureka_service import EurekaService
from folio_upm.services.load_result_analyzer import LoadResultAnalyzer
from folio_upm.services.loaders.capabilities_loader import CapabilitiesLoader
from folio_upm.services.loaders.eureka_result_loader import EurekaResultLoader
from folio_upm.services.loaders.permission_loader import PermissionLoader
from folio_upm.storage.s3_storage import S3Storage
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.storage.tenant_storage_service import TenantStorageService
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env
from folio_upm.xlsx.excel_generator import ExcelResultGenerator

xlsx_ext = "xlsx"
json_gz_ext = "json.gz"
okapi_permissions_fn = "okapi-permissions"
eureka_capabilities_fn = "eureka-capabilities"
mixed_analysis_result_fn = "analysis-result"


_log = log_factory.get_logger("cli.py")


@click.group()
def cli():
    """A simple CLI tool."""
    pass


@cli.command("collect-permissions")
def collect_permissions():
    perms_load_result = PermissionLoader().load_permission_data()
    storage_service = TenantStorageService()
    storage_service.save_object(okapi_permissions_fn, json_gz_ext, perms_load_result)


@cli.command("collect-capabilities")
@click.option("--storage", "-s", type=click.Choice(["s3", "local"]), multiple=True, default=["s3"])
def collect_capabilities(storage: Tuple):
    capability_load_result = CapabilitiesLoader().load_capabilities()
    storage_service = TenantStorageService(get_storages_list(storage))
    storage_service.save_object(eureka_capabilities_fn, json_gz_ext, capability_load_result)


@cli.command("generate-report")
def generate_report(storage: Tuple):
    storages = get_storages_list(storage)
    storage_service = TenantStorageService(storages)
    load_result = storage_service.require_object(okapi_permissions_fn, json_gz_ext)
    eureka_load_result = EurekaResultLoader(storages).get_load_result()
    analysis_result = LoadResultAnalyzer(load_result, eureka_load_result).get_results()
    workbook = ExcelResultGenerator(analysis_result).generate_report()

    storage_service.save_object(mixed_analysis_result_fn, xlsx_ext, workbook)
    storage_service.save_object(mixed_analysis_result_fn, json_gz_ext, analysis_result.model_dump())


@cli.command("run-eureka-migration")
def run_eureka_migration():
    analysis_result = AnalysisResult(**get_tenant_json_gz("analysis-result"))
    EurekaService().migrate_to_eureka(analysis_result)
    _log.info("Starting creation of Eureka roles based on Okapi permissions...")


def get_tenant_json_gz(json_name):
    tenant_id = Env().get_tenant_id()
    file_path = f"{tenant_id}/{tenant_id}-{json_name}.json.gz"
    _log.info(f"Loading JSON from s3: {file_path}")
    return S3Storage().read_object(file_path)


def get_storages_list(storage):
    return [i for i in storage]


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        _log.error(e, exc_info=True)
