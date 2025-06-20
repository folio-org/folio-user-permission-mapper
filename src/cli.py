#!/usr/bin/env python
import os
import time

import click
import dotenv

from dto.models import AnalysisResult
from integrations import s3_client
from services import analysis_service, eureka_service, graph_service, permission_loader, xlsx_service
from utils import env, json_utils, log_factory

_log = log_factory.get_logger(__name__)
_okapi_permissions_json_fn = "okapi-permissions.json.gz"
_analysis_result_json_fn = "analysis-result.json.gz"
_analysis_result_xlsx_fn = "analysis-result.xlsx"

dotenv.load_dotenv()
dotenv.load_dotenv(os.getenv("DOTENV", ".env"), override=True)


@click.group()
def cli():
    """A simple CLI tool."""
    pass


@cli.command("collect-permissions")
def collect_permissions():
    load_result_object = permission_loader.load_permission_data()
    tenant_id = env.get_tenant_id()
    path = f"{tenant_id}/{tenant_id}-{_okapi_permissions_json_fn}"
    compressed_json = json_utils.to_gz_json(load_result_object)
    s3_client.upload_file(path, compressed_json)


@cli.command("generate-report")
@click.option("--store-locally", is_flag=True, default=False)
@click.option("--role-strategy", default="distributed")
def generate_report(store_locally: bool = False, role_strategy: str = "distributed"):
    tenantId = env.get_tenant_id()
    path = f"{tenantId}/{tenantId}-{_okapi_permissions_json_fn}"
    load_result = s3_client.read_json_gz_object(path)
    analysis_report = analysis_service.analyze_results(load_result, role_strategy)
    xlsx_report = xlsx_service.generate_report(analysis_report)

    if store_locally:
        directory = f".temp/{tenantId}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        report_time = time.time_ns()
        with open(f"{directory}/{tenantId}-analysis-report-{report_time}.xlsx", "wb") as f:
            f.write(xlsx_report.getbuffer())
            xlsx_report.seek(0)

        graph_service.generate_graph(analysis_report, ts=report_time, store=store_locally)

    analysis_report_dict = analysis_report.model_dump()
    compressed_json = json_utils.to_gz_json(analysis_report_dict)
    s3_client.upload_file(f"{tenantId}/{tenantId}-{_analysis_result_xlsx_fn}", xlsx_report)
    s3_client.upload_file(f"{tenantId}/{tenantId}-{_analysis_result_json_fn}", compressed_json)


@cli.command("download-load-json")
@click.option(
    "--out-file",
    "out_file",
    type=click.Path(exists=False, writable=True),
    default="okapi-permissions.json",
)
def download_load_json(out_file):
    permission_data = __load_tenant_json("okapi-permissions")
    json_utils.to_formatted_json_file(permission_data, file=out_file)


@cli.command("run-eureka-migration")
def run_eureka_migration():
    """Create Eureka roles based on Okapi permissions."""
    analysis_result = AnalysisResult(**__load_tenant_json("analysis-result"))
    eureka_service.migrate_to_eureka(analysis_result)
    _log.info("Starting creation of Eureka roles based on Okapi permissions...")


def __load_tenant_json(json_name):
    tenant_id = env.get_tenant_id()
    file_path = f"{tenant_id}/{tenant_id}-{json_name}.json.gz"
    _log.info(f"Loading JSON from s3: {file_path}")
    return s3_client.read_json_gz_object(file_path)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        _log.error(f"Failed to execute CLI command: {e}")
        raise Exception(e)
