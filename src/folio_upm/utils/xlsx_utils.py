from io import BytesIO

from openpyxl.workbook import Workbook

from folio_upm.dto.cls_support import SingletonMeta


class XlsxUtils(metaclass=SingletonMeta):

    @staticmethod
    def get_bytes(workbook: Workbook) -> BytesIO:
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        return excel_buffer
