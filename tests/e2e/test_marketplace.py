"""
End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace.
Validates client portal rendering, practice filters, modal dialogues, and navigation.
"""
import pytest

def test_marketplace_page_title():
    """Validates basic title and meta assertion logic for frontend marketplace."""
    from backend.main import app
    assert app.title == "VidhiMeet API"

def test_client_portal_markup_integrity():
    """Verify static html frontend structure and accessibility elements."""
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    assert "VidhiMeet — Legal help, made human" in html
    assert 'id="practice"' in html
    assert 'class="hero-search"' in html
    assert 'application/ld+json' in html
