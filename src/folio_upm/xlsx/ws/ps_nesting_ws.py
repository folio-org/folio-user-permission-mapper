from folio_upm.xlsx.abstract_ws import AbstractWorksheet


class PermissionNestingWorksheet(AbstractWorksheet):
    _title = "PS Nesting"
    _columns = [
        Column[AnalyzedRole](w=40, n="PS", f=lambda x: x.role.id),
        Column[AnalyzedRole](w=60, n="Parent PS", f=lambda x: x.role.name),
        Column[AnalyzedRole](w=60, n="PS Type", f=lambda x: x.role.name)
    ]

    def __init__(self, ws: Worksheet, data: OrdDict[str, AnalyzedRole]):
        super().__init__(ws, self._title, data, self._columns)


    @override
    def _get_iterable_data(self):
        return self._data.sourcedPermissionSet()

    @override
    def _get_row_fill_color(self, value: AnalyzedRole) -> Optional[PatternFill]:
        return constants.almost_white_fill
