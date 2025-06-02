#!/usr/bin/env python
import os
import time
from collections import OrderedDict

import click
import dotenv

from integrations import s3_client
from services import permission_service, xlsx_service, okapi_service, analysis_service, graph_service
from utils import log_factory, env, json_utils

_log = log_factory.get_logger(__name__)
_analysis_result_json_fn = "analysis-result.json.gz"
_analysis_result_xlsx_fn = "analysis-result.xlsx"

dotenv.load_dotenv()
dotenv.load_dotenv(os.getenv('DOTENV', '.env'), override=True)


@click.group()
def cli():
    """A simple CLI tool."""
    pass


@cli.command("collect-permissions")
def collect_permissions():
    _log.info("Starting user permission loading...")
    okapi_permissions = okapi_service.get_okapi_defined_permissions()
    all_perms = permission_service.load_all_permissions_by_query("cql.allRecords=1", expanded=False)
    all_perm_users = permission_service.load_permission_users(all_perms)
    all_perms_enriched = permission_service.enrich_permissions(all_perms, all_perm_users)
    result_object = OrderedDict({
        'okapiPermissions': okapi_permissions,
        'allPermissions': all_perms_enriched,
        'allPermissionUsers': all_perm_users,
    })

    tenant_id = env.get_tenant_id()
    path = f"{tenant_id}/{tenant_id}-{_analysis_result_json_fn}"
    compressed_json = json_utils.to_gz_json(result_object)
    s3_client.upload_file(path, compressed_json)
    _log.info("Permission loading finished successfully.")


@cli.command("generate-excel")
@click.option("--store-locally", "store_locally", is_flag=True, default=False)
def generate_excel(store_locally):
    tenantId = env.get_tenant_id()
    path = f"{tenantId}/{tenantId}-{_analysis_result_json_fn}"
    analysis_result = s3_client.read_json_gz_object(path)
    analysis_report = analysis_service.analyze_results(analysis_result)
    xlsx_report = xlsx_service.generate_report(analysis_report)

    if store_locally:
        directory = f".temp/{tenantId}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(f"{directory}/{tenantId}-analysis-report-{time.time_ns()}.xlsx", "wb") as f:
            f.write(xlsx_report.getbuffer())
            xlsx_report.seek(0)

        graph_service.generate_graph(analysis_report)

    s3_client.upload_file(f"{tenantId}/{tenantId}-{_analysis_result_xlsx_fn}", xlsx_report)


@cli.command("download-analysis-json")
@click.option("--out-file", "out_file",
              type=click.Path(exists=False, writable=True),
              default="analysis-result.json")
def download_analysis_json(out_file):
    tenant_id = env.get_tenant_id()
    path = f"{tenant_id}/{tenant_id}-{_analysis_result_json_fn}"
    analysis_result = s3_client.read_json_gz_object(path)
    json_utils.to_formatted_json_file(analysis_result, file=out_file)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        _log.error(f"Failed to execute CLI command: {e}")
        raise Exception(e)
