import io

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet

from utils import log_factory

_log = log_factory.get_logger(__name__)


def generate_report(analysis_json):
    _log.info("generating XLSX report...")
    wb = Workbook()


    __fill_permission_set_nesting_ws(analysis_json, wb.active)
    __fill_users_permission_sets_ws(analysis_json, wb.create_sheet())
    __fill_permission_permission_sets_ws(analysis_json, wb.create_sheet())

    __format_spreadsheet(wb)

    return __to_byte_doc(wb)


def __fill_permission_set_nesting_ws(analysis_json, ws: Worksheet):
    ws.title = "PermissionSets Nesting"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["PS", "PS Parent"])
    permissions = analysis_json['allPermissions']
    for permission in permissions:
        if not permission.get('mutable', False):
            continue
        permission_name = permission['permissionName']
        parent_permissions = permission.get('childOf', [])
        if not parent_permissions:
            ws.append([permission_name, 'null'])
        else:
            for perm in parent_permissions:
                ws.append([permission_name, perm])
    _log.info(f"Worksheet finished: {ws.title}")


def __fill_users_permission_sets_ws(analysis_json, ws: Worksheet):
    ws.title = "Users-PermissionSets"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["User UUID", "PS"])

    mutable_permission_names = __get_mutable_permission_names(analysis_json)

    permission_users = analysis_json.get('allPermissionUsers', [])
    for permission_user in permission_users:
        user_id = permission_user.get('userId')
        permissions = permission_user.get('permissions', [])
        for permission in permissions:
            if permission in mutable_permission_names:
                ws.append([user_id, permission])
    _log.info(f"Worksheet finished: {ws.title}")


def __fill_permission_permission_sets_ws(analysis_json, ws: Worksheet):
    ws.title = "PermissionSet-PermissionSets"
    _log.info(f"Filling worksheet: {ws.title}...")
    ws.append(["PS", "Child PS"])
    permissions = analysis_json.get('allPermissions', [])
    for permission in permissions:
        permission_name = permission['permissionName']
        sub_permissions = permission.get('subPermissions', [])
        if not sub_permissions:
            ws.append([permission_name, 'null'])
        else:
            for sub_permission in sub_permissions:
                ws.append([permission_name, sub_permission])
    _log.info(f"Worksheet finished: {ws.title}")


def __get_mutable_permission_names(analysis_json):
    mutable_permissions = analysis_json.get('allPermissions', [])
    return set([x.get('permissionName') for x in mutable_permissions if x.get('mutable', False)])


def __format_spreadsheet(wb: Workbook):
    header_font = Font(bold=True, italic=True)
    ws_names = wb.sheetnames
    for ws_name in ws_names:
        ws = wb[ws_name]
        ws.column_dimensions['A'].width = 40
        ws.column_dimensions['B'].width = 60
        __apply_font_for_cells(ws, "A1:B1", header_font)


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
