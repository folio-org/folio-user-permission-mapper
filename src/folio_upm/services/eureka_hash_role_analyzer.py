import re
from typing import Dict, List

from folio_upm.dto.clean_up import HashRolesAnalysisResult, EurekaUserStats, EurekaRoleStats, UserCapabilities
from folio_upm.dto.results import EurekaLoadResult
from folio_upm.utils.ordered_set import OrderedSet


class EurekaHashRoleAnalyzer:

    def __init__(self, eureka_load_result: EurekaLoadResult):
        self._lr = eureka_load_result
        self._roles_by_id = self._get_roles_by_id()
        self._hash_role_ids = self._get_hash_role_ids()
        self._rc = self.get_as_dict(self._lr.roleCapabilities, lambda v: v.roleId, lambda v: v.capabilityId)
        self._rcs = self.get_as_dict(self._lr.roleCapabilitySets, lambda v: v.roleId, lambda v: v.capabilitySetId)
        self._user_roles = self.get_as_dict(self._lr.roleUsers, lambda v: v.userId, lambda v: v.roleId)
        self._role_users = self.get_as_dict(self._lr.roleUsers, lambda v: v.roleId, lambda v: v.userId)
        self._users_capabilities = self.__get_users_capabilities()
        self._result = self.__analyze_eureka_resources()

    def get_result(self) -> HashRolesAnalysisResult:
        return self._result

    def __get_user_roles(self) -> Dict[str, List[str]]:
        return self.get_as_dict(
            self._lr,
            lambda v: v.userId,
            lambda v: v.roleId,
        )

    def __get_role_capabilities(self) -> Dict[str, List[str]]:
        return self.get_as_dict(
            self._lr.roleCapabilities,
            lambda v: v.roleId,
            lambda v: v.capabilityId,
        )

    def __get_role_capability_sets(self) -> Dict[str, List[str]]:
        return self.get_as_dict(
            self._lr.roleCapabilitySets,
            lambda v: v.roleId,
            lambda v: v.capabilitySetId,
        )

    def _get_roles_by_id(self) -> Dict[str, str]:
        return {role.id: role.name for role in self._lr.roles}

    @staticmethod
    def get_as_dict(iterable_obj, key_extractor, value_extractor) -> Dict[str, List[str]]:
        result_dict = {}
        for value in iterable_obj:
            key = key_extractor(value)
            if key not in result_dict:
                result_dict[key] = OrderedSet()
            result_dict[key].add(value_extractor(value))
        return {x: y.to_list() for x, y in result_dict.items()}

    def __analyze_eureka_resources(self) -> HashRolesAnalysisResult:
        return HashRolesAnalysisResult(
            roleStats=self.__get_role_stats(),
            userStats=self.__get_user_stats(),
            # todo: implement roles, roleCapabilities, and roleCapabilitySets
            roles=[],
            roleCapabilities=[],
            roleCapabilitySets=[],
        )

    def __get_role_stats(self):
        role_stats = []
        for role in self._lr.roles:
            role_stats.append(
                EurekaRoleStats(
                    roleId=role.id,
                    roleName=role.name,
                    isHashRole=role.id in self._hash_role_ids,
                    totalUsers=len(self._role_users.get(role.id, [])),
                    capabilitiesNum=len(self._rc.get(role.id, [])),
                    capabilitySetsNum=len(self._rcs.get(role.id, [])),
                )
            )
        return role_stats

    def __get_user_stats(self) -> List[EurekaUserStats]:
        users_stats = []
        empty_user_capabilities = UserCapabilities()
        for user_id, role_ids in self._user_roles.items():
            user_capabilities = self._users_capabilities.get(user_id, empty_user_capabilities)
            user_stats = EurekaUserStats(
                userId=user_id,
                totalRoles=len(role_ids),
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

    def __get_user_capabilities(self, role_ids):
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
            if self.is_sha1_hash(role.name):
                hash_role_ids.add(role.id)

        return hash_role_ids

    @staticmethod
    def is_sha1_hash(s: str) -> bool:
        return bool(re.fullmatch(r"[a-fA-F0-9]{40}", s))
