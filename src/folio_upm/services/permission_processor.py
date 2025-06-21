from folio_upm.dto.results import PermissionAnalysisResult, LoadResult
from folio_upm.utils import log_factory

_log = log_factory.get_logger(__name__)


class PermissionProvider:
    def __init__(self, load_result: LoadResult, ps_analysis_result: PermissionAnalysisResult):
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self.__process_permissions()

    def get_user_stats(self):
        """
        Returns a list with an analysis result for user permission sets, including the following fields:
            - user id
            - number of mutable permission sets
            - number of flat permission sets
            - number of okapi permission sets
            - number of all permission sets

        :return: a list with data to generate a report page about user permission sets
        """
        pass

    def get_all_permission_sets(self):
        """
        Returns a list with an analysis result for all permission sets, including the following fields:
            - permission name
            - permission display name
            - description
            - mutable or not
            - deprecated or not
            - number of sub permissions
            - number of flat sub permissions
            - created userId from metadata (if available)
            - how many times defined in the system (to identify duplicates)
            - if permission set is invalid - reason for invalidity

        :return: a list with data to generate a report page about all permission sets
        """
        pass

    def get_user_permission_sets(self):
        """
        Returns a list with an analysis result for user permission sets, including the following fields:
            - user id
            - permission set name
            - permission set source type
            - is permission being mutable
            - is permission being deprecated
            - is permission being valid
            - has sub permissions

        :return: a list with data to generate a report page about user mutable permission sets
        """
        pass

    def get_parent_permission_sets(self):
        """
        Returns a list with an analysis result for parent permission sets, including the following fields:
            - permission name
            - permission is mutable or not
            - parent permission set name
            - parent permission is mutable or not

        :return: a list with data to generate a report page about user mutable permission sets
        """

    def __process_permissions(self):
        _log.info("Extracting permission set data from analysis results...")
        self._all_permission_sets = list()
        self._user_permission_sets = list()
        self._parent_permission_sets = list()
        self._user_stats = list()
        _log.info("Permission set data extracted successfully...")
