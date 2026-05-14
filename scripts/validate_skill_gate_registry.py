"""Compatibility aggregator for validate_skill_gate registry constants."""

from __future__ import annotations

try:
    from . import validate_skill_gate_registry_core as _core
    from . import validate_skill_gate_registry_bundle as _bundle
    from . import validate_skill_gate_registry_records as _records
    from .validate_skill_gate_registry_core import *
    from .validate_skill_gate_registry_bundle import *
    from .validate_skill_gate_registry_records import *
except ImportError:
    import validate_skill_gate_registry_core as _core
    import validate_skill_gate_registry_bundle as _bundle
    import validate_skill_gate_registry_records as _records
    from validate_skill_gate_registry_core import *
    from validate_skill_gate_registry_bundle import *
    from validate_skill_gate_registry_records import *

__all__ = [*_core.__all__, *_bundle.__all__, *_records.__all__]
