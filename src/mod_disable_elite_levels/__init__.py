from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from mod_hooking.strategy import after, override


@after(VehicleArenaInfoVO, "__init__")
def reset_prestige(_, self, *args, **kwargs):
    self.prestigeLevel = 0
    self.prestigeGradeMarkID = 0


@override(VehicleArenaInfoVO, "updatePrestige")
def do_not_invalidate_prestige(orig, self, invalidate=INVALIDATE_OP.NONE, *args, **kwargs):
    return invalidate
