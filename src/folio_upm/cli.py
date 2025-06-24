#!/usr/bin/env python
import os
import time

import click

from folio_upm.dto.results import AnalysisResult, EurekaLoadResult
from folio_upm.dto.strategy_type import StrategyType
from folio_upm.services.eureka_service import EurekaService
from folio_upm.services.load_result_analyzer import LoadResultAnalyzer
from folio_upm.services.permission_loader import PermissionLoader
from folio_upm.services.xlsx_generator import XlsxReportGenerator
from folio_upm.storage.s3_client import UpmS3Client
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.utils import upm_env
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env
from services import graph_service
from utils import log_factory

upm_env.load_dotenv()

_okapi_permissions_json_fn = "okapi-permissions.json.gz"
_eureka_capabilities_json_fn = "eureka-capabilities.json.gz"
_analysis_result_json_fn = "analysis-result.json.gz"
_analysis_result_xlsx_fn = "analysis-result.xlsx"


_log = log_factory.get_logger('cli.py')


@click.group()
def cli():
    """A simple CLI tool."""
    pass


@cli.command("collect-permissions")
def collect_permissions():
    load_result_object = PermissionLoader().load_permission_data()
    S3TenantStorage().save_object(_okapi_permissions_json_fn, load_result_object)


@cli.command("collect-capabilities")
def collect_capabilities():
    capability_load_result = EurekaLoadResult()
    S3TenantStorage().save_object(_analysis_result_json_fn, capability_load_result)


@cli.command("generate-report")
@click.option("--store-locally", is_flag=True, default=False)
@click.option("--role-strategy", default="distributed")
def generate_report(store_locally: bool = False, role_strategy: str = "distributed"):
    strategy = StrategyType[role_strategy.upper()].value
    if not strategy:
        _log.error(f"Invalid role strategy: {role_strategy}.")
        raise ValueError(f"Invalid role strategy: {role_strategy}.")

    tenant_id = Env().get_tenant_id()
    path_prefix = f"{tenant_id}/{tenant_id}"
    load_result = get_tenant_json_gz(_okapi_permissions_json_fn)
    if not load_result:
        raise FileNotFoundError(f"{_okapi_permissions_json_fn} file not found.")

    eureka_load_result = get_tenant_json_gz(_eureka_capabilities_json_fn)

    analysis_result = LoadResultAnalyzer(load_result, eureka_load_result, strategy.value).get_results()
    xlsx_report_bytes = XlsxReportGenerator(analysis_result).get_report_bytes()

    if store_locally:
        write_local_data(analysis_result, store_locally, xlsx_report_bytes)

    compressed_json = JsonUtils.to_json_gz(analysis_result.model_dump())

    s3_client = UpmS3Client()
    s3_client.upload_file(f"{path_prefix}-{_analysis_result_xlsx_fn}", xlsx_report_bytes)
    s3_client.upload_file(f"{path_prefix}-{_analysis_result_json_fn}", compressed_json)


@cli.command("download-json")
@click.option(
    "--out-file",
    "out_file",
    type=click.Path(exists=False, writable=True),
    default="okapi-permissions.json",
)
def download_load_json(out_file):
    permission_data = get_tenant_json_gz("okapi-permissions")
    JsonUtils.to_formatted_json_file(permission_data, file=out_file)


@cli.command("run-eureka-migration")
def run_eureka_migration():
    """Create Eureka roles based on Okapi permissions."""
    analysis_result = AnalysisResult(**get_tenant_json_gz("analysis-result"))
    EurekaService().migrate_to_eureka(analysis_result)
    _log.info("Starting creation of Eureka roles based on Okapi permissions...")


@cli.command("generate-report-2")
def generate_report_2():
    load_result = S3TenantStorage().download_json_gz(_okapi_permissions_json_fn)
    LoadResultAnalyzer(load_result).get_results()
    _log.info("Analysis finished.")


def get_tenant_json_gz(json_name):
    tenant_id = Env().get_tenant_id()
    file_path = f"{tenant_id}/{tenant_id}-{json_name}.json.gz"
    _log.info(f"Loading JSON from s3: {file_path}")
    return UpmS3Client().read_object(file_path)


def upload_tenant_json_gz(json_name):
    tenant_id = Env().get_tenant_id()
    file_path = f"{tenant_id}/{tenant_id}-{json_name}.json.gz"
    _log.info(f"Loading JSON from s3: {file_path}")
    return UpmS3Client().read_object(file_path)


def get_file_path(file_name: str, extension="json", ts=None) -> str:
    tenant_id = Env().get_tenant_id()
    return f"{tenant_id}/{tenant_id}-{file_name}{'-' if ts else ''}.{extension}"


def write_local_data(analysis_report, store_locally, xlsx_report):
    tenant_id = Env().get_tenant_id()
    directory = f".temp/{tenant_id}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    report_time = time.time_ns()
    with open(f"{directory}/{tenant_id}-analysis-report-{report_time}.xlsx", "wb") as f:
        f.write(xlsx_report.getbuffer())
        xlsx_report.seek(0)
    graph_service.generate_graph(analysis_report, ts=report_time, store=store_locally)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        _log.error(f"Failed to execute CLI command: {e}")
        raise Exception(e)
