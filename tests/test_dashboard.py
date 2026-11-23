"""Smoke test: the site and every page render without an exception (headless, bundled data, offline)."""
from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")
ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("page", ["volselect_app.py", "views/overview.py", "views/live_market.py", "views/research.py"])
def test_page_renders(page, monkeypatch):
    monkeypatch.chdir(ROOT)
    at = st_testing.AppTest.from_file(str(ROOT / page), default_timeout=180).run()
    assert not at.exception, [e.message for e in at.exception]
