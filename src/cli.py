#!/usr/bin/env python
import os
from collections import OrderedDict

import click
import dotenv

from integrations import s3_client
from services import permission_service, xlsx_service, okapi_service
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
    all_perms = permission_service.load_all_permissions_by_query("cql.allRecords=1")
    all_permUsers = permission_service.load_permission_users(all_perms)
    enriched_all_perms = permission_service.enrich_permissions(all_perms, all_permUsers)
    result_object = OrderedDict({
        'okapiPermissions': okapi_permissions,
        'allPermissions': enriched_all_perms,
        'allPermissionUsers': all_permUsers,
    })

    path = f"{env.get_tenant_id()}/{_analysis_result_json_fn}"
    compressed_json = json_utils.to_gz_json(result_object)
    s3_client.upload_file(path, compressed_json)
    _log.info("Permission loading finished successfully.")


@cli.command("generate-excel")
def generate_excel():
    path = f"{env.get_tenant_id()}/{_analysis_result_json_fn}"
    analysis_report = s3_client.read_json_gz_object(path)
    xlsx_report = xlsx_service.generate_report(analysis_report)

    xlsx_path = f"{env.get_tenant_id()}/{_analysis_result_xlsx_fn}"
    s3_client.upload_file(xlsx_path, xlsx_report)


@cli.command("download-analysis-json")
@click.option("--out-file", "out_file",
              type=click.Path(exists=False, writable=True),
              default="analysis-result.json")
def download_analysis_json(out_file):
    path = f"{env.get_tenant_id()}/{_analysis_result_json_fn}"
    analysis_result = s3_client.read_json_gz_object(path)
    json_utils.to_formatted_json_file(analysis_result, file=out_file)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        _log.error(f"Failed to execute CLI command: {e}")
        raise Exception(e)
