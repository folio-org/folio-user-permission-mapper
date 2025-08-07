import inspect
from typing import Optional

from openpyxl import Workbook

from folio_upm.utils import log_factory


class WsDef:

    def __init__(self, ws_class, data_extractor, title: Optional[str] = None):
        self.ws_class = ws_class
        self.data_extractor = data_extractor
        self.title = title


class AbstractReportProvider:
    def __init__(self, data, worksheet_defs):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Initializing XlsxReportGenerator...")
        self._data = data
        self._worksheet_defs = worksheet_defs
        self._wb = self.__generate_workbook()

    def generate(self) -> Workbook:
        return self._wb

    def __generate_workbook(self):
        self._log.info("Generating XLSX report...")
        wb = Workbook()
        wb.remove(wb.active)
        for ws_def in self._worksheet_defs:
            ws_class = ws_def.ws_class
            data_extractor = ws_def.data_extractor
            self._log.debug("Processing worksheet in '%s'", ws_class.__name__)

            sig = inspect.signature(ws_class.__init__)
            kwargs = {}
            title = ws_def.title
            if title is not None and "title" in sig.parameters:
                kwargs["title"] = title

            ws_generator = ws_class(wb.create_sheet(), data_extractor(self._data), **kwargs)
            ws_generator.fill()
        self._log.info("XLSX report generated successfully.")
        return wb
