import pytest
from ghost_healer.adapters.playwright import protect_page

@pytest.fixture(autouse=True)
def ghost_mode(page):
    protect_page(page)
    yield
