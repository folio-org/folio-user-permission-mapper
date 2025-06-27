import json
from collections import OrderedDict

from folio_upm.dto.results import AnalysisResult
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.ordered_set import OrderedSet


def test_test():
    assert 1 != 2


def test_ordered_set():
    ordered_set = OrderedSet[str](["s1", "s2", "s3"])
    ordered_set.append("s4")
    ordered_set.append(["s6", "s7", "s2"])
    ordered_set.remove("s2")
    assert json.dumps(ordered_set.to_list()) == '["s1", "s3", "s4", "s6", "s7"]'


def test_replace_users():
    tenant = "diku"
    prefix = "D:/projects/folio/folio-user-permission-mapper/.temp"
    with open(f"{prefix}/{tenant}/{tenant}-analysis-result.json", "r") as file:
        analysis_result = json.load(file)

    with open(f"{prefix}/{tenant}/users.json", "r") as file:
        users = json.load(file)

    analysis_result = AnalysisResult(**analysis_result)
    uq_user_ids = list(OrderedSet([user_id for ru in analysis_result.roleUsers[:2] for user_id in ru.userIds]))
    replacement_map = OrderedDict()
    for idx in range(len(uq_user_ids)):
        replacement_map[uq_user_ids[idx]] = users[idx]

    new_role_users = []
    for ru in analysis_result.roleUsers[:2]:
        new_user_ids = []
        for user_id in ru.userIds:
            if user_id in replacement_map:
                new_user_ids.append(replacement_map[user_id])
        ru.userIds = new_user_ids
        new_role_users.append(ru)

    analysis_result.roleUsers = new_role_users
    json_bytes = JsonUtils.to_json_gz(analysis_result.model_dump())
    with open(f"{prefix}/{tenant}/{tenant}-analysis-result.json.gz", "wb") as file:
        file.write(json_bytes.getbuffer())
    print(new_role_users)
