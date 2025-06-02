import io

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet

from dto.models import AnalysisResult
from utils import log_factory

_log = log_factory.get_logger(__name__)


def generate_report(analysis_result: AnalysisResult):
    _log.info("generating XLSX report...")
    wb = Workbook()

    __fill_permission_set(analysis_result, wb.active)
    __fill_permission_set_nesting_ws(analysis_result, wb.create_sheet())
    __fill_users_permission_sets_ws(analysis_result, wb.create_sheet())
    # __fill_permission_sets_users(analysis_result, wb.create_sheet())
    __fill_permission_permission_sets_ws(analysis_result, wb.create_sheet())

    return __to_byte_doc(wb)


def __fill_permission_set(analysis_result: AnalysisResult, ws: Worksheet):
    ws.title = "PS"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["Name", "Description"])

    permissions = analysis_result.permissionSets.items()
    for permission_name, permission in permissions:
        if permission.mutable:
            ws.append([permission_name, permission.description])

    __format_worksheet(ws, [('A', 40), ('B', 100)])
    _log.info(f"Worksheet finished: {ws.title}")


def __fill_permission_set_nesting_ws(analysis_result: AnalysisResult, ws: Worksheet):
    ws.title = "PermissionSets Nesting"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["PS", "PS Parent"])

    nested_perms_items = analysis_result.permissionSetsNesting.items()
    for permission_name, parent_permission_names in nested_perms_items:
        if not parent_permission_names:
            ws.append([permission_name, 'null'])
        else:
            for perm in parent_permission_names:
                ws.append([permission_name, perm])

    __format_worksheet(ws, [('A', 40), ('B', 40)])
    _log.info(f"Worksheet finished: {ws.title}")


def __fill_users_permission_sets_ws(analysis_result: AnalysisResult, ws: Worksheet):
    ws.title = "Users-PermissionSets"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["User UUID", "PS"])

    permission_users = analysis_result.usersPermissionSets.items()
    for user_id, permission_names in permission_users:
        for permission in permission_names:
            ws.append([user_id, permission])

    __format_worksheet(ws, [('A', 40), ('B', 40)])
    _log.info(f"Worksheet finished: {ws.title}")


def __fill_permission_sets_users(analysis_result: AnalysisResult, ws: Worksheet):
    ws.title = "PermissionSets-Users"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["Permission Name", "User UUID"])

    permission_users = analysis_result.permissionSetUsers.items()
    for permission_name, user_ids in permission_users:
        for user_id in user_ids:
            ws.append([permission_name, user_id])

    __format_worksheet(ws, [('A', 40), ('B', 40)])
    _log.info(f"Worksheet finished: {ws.title}")


def __fill_permission_permission_sets_ws(analysis_result: AnalysisResult, ws: Worksheet):
    ws.title = "PermissionSet-PermissionSets"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["PS", "Child PS"])

    items = analysis_result.permissionPermissionSets.items()
    for permission_name, sub_permission_names in items:
        if not sub_permission_names:
            ws.append([permission_name, 'null'])
        else:
            for sub_permission in sub_permission_names:
                ws.append([permission_name, sub_permission])
    __format_worksheet(ws, [('A', 80), ('B', 80)])
    _log.info(f"Worksheet finished: {ws.title}")


def __get_mutable_permission_names(analysis_json):
    mutable_permissions = analysis_json.get('allPermissions', [])
    return set([x.get('permissionName') for x in mutable_permissions if x.get('mutable', False)])


def __format_worksheet(ws: Worksheet, dimensions):
    for dimension in dimensions:
        columnName = dimension[0]
        columnWidth = dimension[1]
        ws.column_dimensions[columnName].width = columnWidth

    header_font = Font(bold=True, italic=True)
    __apply_font_for_cells(ws, "A1:C1", header_font)


def __to_byte_doc(wb):
    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)
    return excel_buffer


def __apply_font_for_cells(ws, key, font):
    """
    Apply the given font to all cells in the worksheet.
    """
    for row in ws[key]:
        for cell in row:
            cell.font = font
