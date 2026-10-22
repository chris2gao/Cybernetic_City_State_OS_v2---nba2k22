from .coverage import assess
from .models import module_result


def check_field(policy, field, value):
    from coach_codec import load_profile, validate_value
    definition=load_profile()["fields"].get(field)
    if not definition or field.startswith("poe_") or definition.get('gm_control_enabled') is False:
        return {"valid":False,"reason":"LEGACY_OR_UNKNOWN_TACTICAL_FIELD","execution_ready":False}
    try:
        validate_value(definition,value,target=True)
    except ValueError as exc:
        return {"valid":False,"reason":str(exc),"execution_ready":False}
    return {"valid":True,"reason":None,"execution_ready":False,
            "enum_status":definition["readiness"],"snapshot_validation_required":True}


def analyze(data, team, side):
    availability = assess(data, team, side)
    missing = availability["missing_data"] + ["阵容角色、轮换、比赛效率和对手表现，尚不足以确认战术优劣"]
    if side == "defense":
        missing.append("指定对手整体防守须读取对应coaching/opponents来源及认证状态，不能用默认POE代替")
    return module_result(side, availability["values"],
                         ["仅同批原生coaching_tactics作为战术事实；历史poe_*语义撤销。比赛效果不作为技术可用的前提。"], missing,
                         ["按19项默认字段及指定对手整体防守目录提出具体批次；五项Sim不允许GM修改。"])
