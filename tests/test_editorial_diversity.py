"""Auditoría de sesgos (sept 2026): la config de diversidad editorial es coherente
y no vuelve a existir una regla de longitud contradictoria."""

import json

from idiem.loader import CONFIG_DIR, load_editorial_style


def _div() -> dict:
    return json.loads((CONFIG_DIR / "editorial_diversity.json").read_text(encoding="utf-8"))


def test_length_is_single_source_in_characters():
    div, style = _div(), load_editorial_style()
    assert div["length"]["unit"] == style["length"]["unit"] == "characters"
    for k in ("max_chars", "target_chars_min", "target_chars_max"):
        assert div["length"][k] == style["length"][k], f"{k} diverge entre archivos"
    assert "target_words_min" not in style["length"], "regla antigua en palabras no debe volver"
    assert div["length"]["emojis_per_paragraph_max"] <= 2


def test_enough_distinct_archetypes_and_types():
    div = _div()
    ids = [a["id"] for a in div["archetypes"]]
    assert 6 <= len(ids) <= 8 and len(set(ids)) == len(ids)
    assert sum(1 for a in div["archetypes"] if a["opens_with_service"]) <= 1
    assert len({h["id"] for h in div["hook_types"]}) >= 5
    assert len({c["id"] for c in div["cta_types"]}) >= 5


def test_contact_is_not_default_cta():
    div = _div()
    contact = [c for c in div["cta_types"] if c["id"] == "commercial_contact"][0]
    assert contact.get("default") is False
    assert not any(c.get("default") for c in div["cta_types"])


def test_limits_force_real_diversity_in_a_12_post_month():
    lim = _div()["limits_per_month"]
    # Con 12 posts, el máximo por arquetipo obliga a usar >= 6 arquetipos.
    assert lim["max_posts_per_archetype"] * lim["min_distinct_archetypes"] >= 12
    assert lim["max_posts_per_cta_type"] < 9, "octubre tuvo 9/12 contact: el límite debe impedirlo"


def test_fingerprint_separates_hook_from_pain_point():
    fp = _div()["fingerprint_fields"]
    for f in ("pain_point", "main_claim", "archetype", "hook_type", "cta_type", "structure"):
        assert f in fp
    assert "hook_type" != "pain_point" and fp.index("hook_type") != fp.index("pain_point")


def test_publication_classification_labels():
    assert set(_div()["data_classification"]) == {"SAFE", "VERIFY", "INTERNAL", "DO_NOT_PUBLISH"}
