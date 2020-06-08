try:
    from . import dmp_monkey
except ImportError:
    from . import dmp_monkey

dmp_monkey.monkey_patch()

try:
    from . import diff_match_patch
except ImportError:
    from . import diff_match_patch

DMP = diff_match_patch.diff_match_patch()
