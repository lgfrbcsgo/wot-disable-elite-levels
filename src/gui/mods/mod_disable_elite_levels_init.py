from debug_utils import LOG_CURRENT_EXCEPTION


def init():
    try:
        import mod_disable_elite_levels
    except Exception:
        LOG_CURRENT_EXCEPTION()


def fini():
    pass
