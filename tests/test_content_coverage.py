"""Content coverage — temas frescos por célula, con cooldown y CONTENT_GAP."""

from idiem.content_coverage import coverage, coverage_report


def _by_cell(rows):
    return {r.cell: r for r in rows}


def test_transporte_is_content_gap(kb):
    rows = _by_cell(coverage(kb))
    assert rows["INFRA CRÍTICA TRANSPORTE"].status == "CONTENT_GAP"


def test_cooldown_reduces_fresh(kb):
    # Sin mes: nada en cooldown. Con mes (tras Sept+Oct): algunos ítems en cooldown.
    no_month = _by_cell(coverage(kb))
    with_month = _by_cell(coverage(kb, month="2026-11"))
    assert no_month["INFRA OPERACIÓN MINERA"].on_cooldown == 0
    assert with_month["INFRA OPERACIÓN MINERA"].on_cooldown > 0
    assert with_month["INFRA OPERACIÓN MINERA"].fresh < no_month["INFRA OPERACIÓN MINERA"].fresh


def test_low_cell_flagged(kb):
    rows = _by_cell(coverage(kb, month="2026-11"))
    # IHA queda con pocos temas frescos tras el uso reciente.
    assert rows["INFRA HOSPITALARIA Y ASISTENCIAL"].status in {"LOW", "CONTENT_GAP"}


def test_report_renders(kb):
    txt = coverage_report(kb, month="2026-11")
    assert "cobertura editorial" in txt.lower()
    assert "CONTENT_GAP" in txt
