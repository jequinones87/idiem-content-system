"""Policy vocabulary and enforcement helpers for the IDIEM 2A.2 library.

These constants and predicates encode the non-negotiable rules from
``CLAUDE.md`` and ``data/04_base_produccion_IDIEM_2A2.json`` -> ``generation_rules``.
They deliberately *fail closed*: an unknown policy is never treated as usable.
"""

from __future__ import annotations

# --- generation_policy values carried by knowledge_items ---------------------
USE_FACTUAL = "USE_FACTUAL"
USE_AUDITED_CORRECTION = "USE_AUDITED_CORRECTION"
USE_WITH_MATIZ = "USE_WITH_MATIZ"
NAME_ONLY_DO_NOT_EXPAND = "NAME_ONLY_DO_NOT_EXPAND"
USE_TECHNICAL_CORE_BLOCK_CLAIMS = "USE_TECHNICAL_CORE_BLOCK_CLAIMS"

GENERATION_POLICIES = frozenset(
    {
        USE_FACTUAL,
        USE_AUDITED_CORRECTION,
        USE_WITH_MATIZ,
        NAME_ONLY_DO_NOT_EXPAND,
        USE_TECHNICAL_CORE_BLOCK_CLAIMS,
    }
)

# Policies under which the item's verified evidence may be stated as fact.
# NAME_ONLY may only be *named* (no expansion). BLOCK_CLAIMS keeps the
# technical core but blocks attached rankings/superlatives.
_EXPANDABLE_POLICIES = frozenset(
    {USE_FACTUAL, USE_AUDITED_CORRECTION, USE_WITH_MATIZ, USE_TECHNICAL_CORE_BLOCK_CLAIMS}
)

# --- auxiliary_evidence production_policy values -----------------------------
SUPPORTING_ATTRIBUTE_WITH_SOURCE = "SUPPORTING_ATTRIBUTE_WITH_SOURCE"
SUPPORTING_CLAIM_WITH_SOURCE = "SUPPORTING_CLAIM_WITH_SOURCE"
STRUCTURAL_CONTEXT_ONLY = "STRUCTURAL_CONTEXT_ONLY"
HISTORICAL_CONTEXT_ONLY = "HISTORICAL_CONTEXT_ONLY"
SECTOR_CONTEXT_ONLY = "SECTOR_CONTEXT_ONLY"
CHECK_VALIDITY_BEFORE_USE = "CHECK_VALIDITY_BEFORE_USE"
CHECK_CURRENT_VALIDITY_BEFORE_USE = "CHECK_CURRENT_VALIDITY_BEFORE_USE"
DO_NOT_USE_AS_FACT = "DO_NOT_USE_AS_FACT"

AUXILIARY_POLICIES = frozenset(
    {
        SUPPORTING_ATTRIBUTE_WITH_SOURCE,
        SUPPORTING_CLAIM_WITH_SOURCE,
        STRUCTURAL_CONTEXT_ONLY,
        HISTORICAL_CONTEXT_ONLY,
        SECTOR_CONTEXT_ONLY,
        CHECK_VALIDITY_BEFORE_USE,
        CHECK_CURRENT_VALIDITY_BEFORE_USE,
        DO_NOT_USE_AS_FACT,
    }
)

# Auxiliary policies whose current validity must be confirmed before publishing
# (GR-13). They may appear in a brief but flagged as "check vigencia".
_AUX_REQUIRES_VALIDITY = frozenset(
    {CHECK_VALIDITY_BEFORE_USE, CHECK_CURRENT_VALIDITY_BEFORE_USE}
)

# Reserve / excluded production policies (never active technical content).
RESERVE_FACTUAL = "RESERVE_FACTUAL"
EXCLUDED_DO_NOT_USE = "EXCLUDED_DO_NOT_USE"


def is_valid_generation_policy(policy: str) -> bool:
    return policy in GENERATION_POLICIES


def may_expand(policy: str) -> bool:
    """True when the item's verified evidence may be stated, not just named."""
    return policy in _EXPANDABLE_POLICIES


def is_name_only(policy: str) -> bool:
    return policy == NAME_ONLY_DO_NOT_EXPAND


def blocks_claims(policy: str) -> bool:
    """USE_TECHNICAL_CORE_BLOCK_CLAIMS: technical core ok, claims blocked (GR-04)."""
    return policy == USE_TECHNICAL_CORE_BLOCK_CLAIMS


def requires_matiz(policy: str) -> bool:
    return policy == USE_WITH_MATIZ


# Standard blocked-claim statements attached to BLOCK_CLAIMS items (GR-04).
BLOCKED_CLAIM_TEMPLATES = (
    "No afirmar rankings mundiales, primacía o unicidad ('único', 'el más grande del mundo').",
    "No afirmar exclusividad ni superlativos no respaldados por la evidencia.",
    "No atribuir resultados, impactos o cifras comparativas no documentadas.",
)


def auxiliary_is_usable(production_policy: str) -> bool:
    """Auxiliary evidence is usable as *supporting* context unless DO_NOT_USE_AS_FACT.

    Fails closed on unknown policies.
    """
    if production_policy not in AUXILIARY_POLICIES:
        return False
    return production_policy != DO_NOT_USE_AS_FACT


def auxiliary_needs_validity_check(production_policy: str) -> bool:
    return production_policy in _AUX_REQUIRES_VALIDITY
