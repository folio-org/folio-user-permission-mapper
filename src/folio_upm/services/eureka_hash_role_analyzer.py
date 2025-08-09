import re
from typing import Any, Callable, Dict, List, Optional

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.model.cleanup.user_capabilities import UserCapabilities
from folio_upm.model.eureka.role import Role
from folio_upm.model.eureka.role_capability_or_set import RoleCapabilityOrSet
from folio_upm.model.eureka.user_roles import UserRoles
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.model.result.hash_roles_analysis_result import HashRolesAnalysisResult
from folio_upm.model.stats.eureka_role_stats import EurekaRoleStats
from folio_upm.model.stats.eureka_user_stats import EurekaUserStats
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import IterableUtils
from folio_upm.utils.ordered_set import OrderedSet


class EurekaHashRoleAnalyzer:

    def __init__(self, eureka_load_result: EurekaLoadResult):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._lr = eureka_load_result
        self._roles_by_id = self.__get_roles_by_id()
        self._hash_role_ids = self._get_hash_role_ids()
        self._capabilities_by_id = {cap.id: cap for cap in self._lr.capabilities}
        self._capability_sets_by_id = {cs.id: cs for cs in self._lr.capabilitySets}
        self._rc = self.__get_as_dict(self._lr.roleCapabilities, lambda v: v.roleId, lambda v: v.capabilityId)
        self._rcs = self.__get_as_dict(self._lr.roleCapabilitySets, lambda v: v.roleId, lambda v: v.capabilitySetId)
        self._user_roles = self.__get_as_dict(self._lr.roleUsers, lambda v: v.userId, lambda v: v.roleId)
        self._role_users = self.__get_as_dict(self._lr.roleUsers, lambda v: v.roleId, lambda v: v.userId)
        self._users_capabilities = self.__get_users_capabilities()
        self._result = self.__analyze_eureka_resources()

    def get_result(self) -> HashRolesAnalysisResult:
        return self._result

    def __get_roles_by_id(self) -> Dict[str, Role]:
        return {role.id: role for role in self._lr.roles if role.id}

    def __analyze_eureka_resources(self) -> HashRolesAnalysisResult:
        return HashRolesAnalysisResult(
            roleStats=self.__get_role_stats(),
            userStats=self.__get_user_stats(),
            userRoles=self.__get_user_roles_for_ws(),
            roleCapabilities=self.__get_role_capabilities_for_ws(),
            hashRoleCleanupRecords=self.__get_remaining_hash_role_capabilities(),
        )

    def __get_role_stats(self):
        role_stats = []
        for role in self._lr.roles:
            role_id = role.id
            role_stats.append(
                EurekaRoleStats(
                    roleId=role.id,
                    roleName=role.name,
                    isHashRole=role.id in self._hash_role_ids,
                    totalUsers=len(self.__get_or_empty(self._role_users, role_id)),
                    capabilitiesNum=len(self.__get_or_empty(self._rc, role_id)),
                    capabilitySetsNum=len(self.__get_or_empty(self._rcs, role_id)),
                )
            )
        return role_stats

    def __get_user_stats(self) -> List[EurekaUserStats]:
        users_stats = []
        empty_user_capabilities = UserCapabilities()
        for user_id, role_ids in self._user_roles.items():
            user_capabilities = self._users_capabilities.get(user_id, empty_user_capabilities)
            hash_role_ids = [role_id for role_id in role_ids if role_id in self._hash_role_ids]
            user_stats = EurekaUserStats(
                userId=user_id,
                totalRoles=len(role_ids),
                hashRoles=len(hash_role_ids),
                allCapabilities=len(user_capabilities.allCapabilities),
                allCapabilitySets=len(user_capabilities.allCapabilitySets),
                roleCapabilities=len(user_capabilities.roleCapabilities),
                roleCapabilitySets=len(user_capabilities.roleCapabilitySets),
                hashRoleCapabilities=len(user_capabilities.hashRoleCapabilities),
                hashRoleCapabilitySets=len(user_capabilities.hashRoleCapabilitySets),
            )
            users_stats.append(user_stats)
        return users_stats

    def __get_users_capabilities(self) -> Dict[str, UserCapabilities]:
        user_capabilities = {}
        for user_id, role_ids in self._user_roles.items():
            user_capabilities[user_id] = self.__get_user_capabilities(role_ids)
        return user_capabilities

    def __get_user_capabilities(self, role_ids: List[str]) -> UserCapabilities:
        role_capabilities = OrderedSet()
        role_capability_sets = OrderedSet()
        all_role_capabilities = OrderedSet()
        all_role_capability_sets = OrderedSet()
        hash_role_capabilities = OrderedSet()
        hash_role_capability_sets = OrderedSet()

        for roleId in role_ids:
            all_role_capabilities.add_all(self._rc.get(roleId, []))
            all_role_capability_sets.add_all(self._rcs.get(roleId, []))
            if roleId in self._hash_role_ids:
                hash_role_capabilities.add_all(self._rc.get(roleId, []))
                hash_role_capability_sets.add_all(self._rcs.get(roleId, []))
            else:
                role_capabilities.add_all(self._rc.get(roleId, []))
                role_capability_sets.add_all(self._rcs.get(roleId, []))

        return UserCapabilities(
            roleCapabilities=role_capabilities.to_list(),
            roleCapabilitySets=role_capability_sets.to_list(),
            allCapabilities=all_role_capabilities.to_list(),
            allCapabilitySets=all_role_capability_sets.to_list(),
            hashRoleCapabilities=hash_role_capabilities.to_list(),
            hashRoleCapabilitySets=hash_role_capability_sets.to_list(),
        )

    def _get_hash_role_ids(self) -> OrderedSet[str]:
        hash_role_ids = OrderedSet()
        for role in self._lr.roles:
            if self.__is_sha1_hash(role.name):
                if role.id:
                    hash_role_ids.add(role.id)
                else:
                    self._log.warning("Role with SHA1 hash name does not have an ID: %s", role.name)
        return hash_role_ids

    def __get_role_capabilities_for_ws(self):
        result = []
        for role in self._lr.roles:
            result += [self.__create_rcs(role, "capability", x) for x in self.__get_or_empty(self._rc, role.id)]
            result += [self.__create_rcs(role, "capability-set", x) for x in self.__get_or_empty(self._rcs, role.id)]
        return result

    def __create_rcs(self, role, c_type, capabilityOrSetId: str) -> RoleCapabilityOrSet:
        if c_type == "capability":
            capabilityOrSet = self._capabilities_by_id.get(capabilityOrSetId)
        else:
            capabilityOrSet = self._capability_sets_by_id.get(capabilityOrSetId)
        return RoleCapabilityOrSet(role=role, capabilityOrSet=capabilityOrSet)

    def __get_user_roles_for_ws(self) -> List[UserRoles]:
        user_roles = []
        for user_id, role_ids in self._user_roles.items():
            role_names = [self._roles_by_id[role_id].name for role_id in role_ids]
            role_names = [name for name in role_names if name is not None]
            user_roles.append(UserRoles(userId=user_id, roles=role_names))
        return user_roles

    def __get_remaining_hash_role_capabilities(self) -> List[FullHashRoleCleanupRecord]:
        result = []
        for role_id, users_ids in self._role_users.items():
            if role_id not in self._hash_role_ids:
                continue

            hash_role_id = role_id
            hash_role_set_ids = set(self._rcs.get(hash_role_id, self.__get_empty_list()))
            hash_role_capability_ids = set(self._rc.get(hash_role_id, self.__get_empty_list()))

            users_capability_set_ids = []
            users_capability_ids = []
            for user_id in users_ids:
                role_capability_ids, role_capability_set_ids = self.__get_assigned_capabilities(user_id)
                users_capability_set_ids.append(role_capability_set_ids)
                users_capability_ids.append(role_capability_ids)

            shared_set_ids = IterableUtils.intersection(users_capability_set_ids)
            shared_capability_ids = IterableUtils.intersection(users_capability_ids)
            remaining_set_ids = hash_role_set_ids - shared_set_ids
            remaining_capability_ids = hash_role_capability_ids - shared_capability_ids

            cleaned_hash_role = FullHashRoleCleanupRecord(
                role=self._roles_by_id[role_id],
                capabilities=[self._capabilities_by_id[x] for x in remaining_capability_ids],
                capabilitySets=[self._capability_sets_by_id[x] for x in remaining_set_ids],
            )

            result.append(cleaned_hash_role)

        return result

    def __get_assigned_capabilities(self, user_id):
        user_capabilities = self._users_capabilities.get(user_id, UserCapabilities())
        role_capability_set_ids = OrderedSet[str](user_capabilities.roleCapabilitySets)
        all_role_capability_ids = OrderedSet[str](user_capabilities.roleCapabilities)
        for capability_set_id in role_capability_set_ids:
            set_by_id = self._capability_sets_by_id.get(capability_set_id)
            if set_by_id is not None:
                all_role_capability_ids.add_all(set_by_id.capabilities)
        return all_role_capability_ids.to_list(), role_capability_set_ids.to_list()

    @staticmethod
    def __is_sha1_hash(s: Optional[str]) -> bool:
        if s is None:
            return False
        return bool(re.fullmatch(r"[a-fA-F0-9]{40}", s))

    @staticmethod
    def __get_as_dict(
        iterable_obj: List[Any], key_extractor: Callable[[Any], str], value_extractor: Callable[[Any], Any]
    ) -> Dict[str, List[str]]:
        result_dict: Dict[str, OrderedSet[str]] = {}
        for value in iterable_obj:
            key = key_extractor(value)
            if key not in result_dict:
                result_dict[key] = OrderedSet[str]()
            result_dict[key].add(value_extractor(value))
        return {x: y.to_list() for x, y in result_dict.items()}

    @staticmethod
    def __get_empty_list() -> List[str]:
        empty_list: List[str] = []
        return empty_list

    @staticmethod
    def __get_or_empty(values_dict: Dict[str, List[str]], key: Optional[str]) -> List[str]:
        if key is None:
            return []
        if not values_dict:
            return []
        value_by_key = values_dict.get(key)
        return value_by_key if value_by_key is not None else []
