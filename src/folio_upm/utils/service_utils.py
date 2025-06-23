from collections import OrderedDict
from typing import Callable, Any, List, Optional, Iterable

from folio_upm.utils import log_factory, env
from folio_upm.utils.common_utils import IterableUtils


class ServiceUtils:

    @staticmethod
    def is_system_permission(permission: str) -> bool:
        return permission.startswith("SYS#")

    @staticmethod
    def unique_values(iterable):
        return list(OrderedDict.fromkeys(iterable).keys())


class PagedDataLoader:

    def __init__(
        self,
        resource: str,
        loader_func: Callable[[str, int, int], List[Any]],
        query: str = "cql.allRecords=1",
        batch_limit: int = 500,
    ):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._resource = resource
        self._query = query
        self._loader_func = loader_func
        self._batch_limit = batch_limit

    def load(self) -> List[Any]:
        self._log.info("Loading paged data for '%s' and query: '%s'...", self._resource, self._query)
        result = []
        last_offset = 0

        while True:
            page = self._loader_func(self._query, self._batch_limit, last_offset)
            last_load_size = len(page)
            result += page
            last_offset += self._batch_limit
            if last_load_size < self._batch_limit:
                self._log.info("Paged data loading finished for '%s': total=%s", self._resource, len(result))
                break

        return result


class PartitionedDataLoader:

    def __init__(
        self,
        resource: str,
        data: Iterable[Any],
        data_loader: Callable[[str], List[Any]],
        query_builder=Callable[[List[Any]], str],
        partition_size: Optional[int] = None,
    ):
        _partition_size = partition_size or int(env.get_env("DEFAULT_API_CHUNK_SIZE", default_value=50))
        self._resource = resource
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._partitioned_data = IterableUtils.partition(data, _partition_size)
        self._data_loader = data_loader
        self._query_builder = query_builder

    def load(self) -> List[Any]:
        result = []

        self._log.info("Loading partitioned data for: %s ...", self._resource)
        for partition in self._partitioned_data:
            query = self._query_builder(partition)
            self._log.info("Loading partitioned data ('%s') for query: %s..", self._resource, query)
            loaded_data = self._data_loader(query)
            result += loaded_data
        self._log("Partitioned data loading finished for '%s': total=%d", self._resource, len(result))
        return result
