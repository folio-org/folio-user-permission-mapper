from typing import List, Optional, Any, TypeVar, Generic

from black.lines import Callable
from openpyxl.styles import Alignment, PatternFill
from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.utils import log_factory
from folio_upm.xlsx import constants


T = TypeVar("T")


class Column(BaseModel, Generic[T]):
    n: str
    w: int
    f: Callable[[T], Optional[Any]]


class AbstractWorksheet:

    def __init__(self, ws: Worksheet, title: str, data: Any, columns: List[Column]):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._ws = ws
        self._data = data
        self._ws.title = title
        self._columns = columns
        self._row_num = 1

    def fill(self):
        self._log.debug("Worksheet fill initialized: '%s'...", self._ws.title)
        self._populate_headers()
        self._fill_rows()
        self._ws.auto_filter.ref = self._ws.dimensions
        self._log.debug("Worksheet filled with data: '%s'", self._ws.title)

    def _populate_headers(self):
        for col_num, header in enumerate(self._columns, start=1):
            cell = self._ws.cell(column=col_num, row=self._row_num, value=header.n)
            cell.font = constants.header_font
            cell.border = constants.thin_border
            cell.alignment = constants.header_cell_alignment
            cell.fill = constants.light_gray_fill
            self._ws.column_dimensions[cell.column_letter].width = header.w
            self._ws.row_dimensions[self._row_num].height = 20
        self._row_num += 1

    def _fill_rows(self):
        for value in self._get_iterable_data():
            fill = self._get_row_fill_color(value)
            self._add_row(self._map_value(value), fill=fill)

    def title(self):
        return self._ws.title

    def _map_value(self, value: Any):
        return [col.f(value) for col in self._columns]

    def _get_iterable_data(self) -> List[Any]:
        return self._data

    def _add_row(self, row: List[Optional[Any]], fill: PatternFill = None):
        for col_num, cell_value in enumerate(row, start=1):
            cell = self._ws.cell(column=col_num, row=self._row_num, value=cell_value)
            cell.font = constants.data_font
            cell.border = constants.thin_border
            cell.alignment = constants.data_cell_alignment
            if fill:
                cell.fill = fill
        self._row_num += 1

    def _get_row_fill_color(self, value) -> Optional[PatternFill]:
        return constants.almost_white_fill
