"""
Smoke tests: every page route renders without server error in every supported
language. Catches Jinja template errors, missing i18n keys that crash render,
and broken context fixtures.

These tests don't assert content — only that the page returns HTTP 200 and
non-empty body. Content correctness is the job of dedicated test files.
"""

import pytest

PAGES = [
    '/',
    '/search',
    '/about',
    '/browse',
    '/parallel',
    '/concordance',
    '/diachronic',
    '/hapax',
    '/heatmap',
    '/parse',
    '/collocations',
    '/semantic-fields',
    '/passage-profile',
    '/bookmarks',
    '/annotations',
    '/api-docs',
    '/privacy',
]

LANGS = ['en', 'es', 'he', 'ar']


@pytest.mark.parametrize('path', PAGES)
def test_page_renders_in_english(client, path):
    r = client.get(path)
    assert r.status_code == 200, f'{path} returned {r.status_code}'
    assert len(r.data) > 100, f'{path} returned suspiciously short body'


@pytest.mark.parametrize('lang', LANGS)
def test_homepage_renders_in_each_language(client, lang):
    r = client.get(f'/?lang={lang}')
    assert r.status_code == 200
    body = r.data.decode('utf-8')
    expected_dir = 'rtl' if lang in ('he', 'ar') else 'ltr'
    assert f'dir="{expected_dir}"' in body, f'lang={lang} did not set dir={expected_dir}'
    assert f'lang="{lang}"' in body


@pytest.mark.parametrize('lang', LANGS)
def test_about_page_renders_in_each_language(client, lang):
    r = client.get(f'/about?lang={lang}')
    assert r.status_code == 200
    assert len(r.data) > 1000


@pytest.mark.parametrize('lang', LANGS)
def test_privacy_page_renders_in_each_language(client, lang):
    r = client.get(f'/privacy?lang={lang}')
    assert r.status_code == 200
    body = r.data.decode('utf-8')
    # Must mention the GA property ID and provide opt-out controls
    assert 'G-XWZC618EC4' in body
    assert 'aramaicAnalyticsOptOut' in body or 'aramaicAnalyticsOptIn' in body


def test_robots_txt(client):
    r = client.get('/robots.txt')
    assert r.status_code == 200
    body = r.data.decode('utf-8')
    assert 'User-agent: *' in body
    assert 'Sitemap: ' in body


def test_sitemap_xml(client):
    r = client.get('/sitemap.xml')
    assert r.status_code == 200
    assert r.headers['Content-Type'].startswith('application/xml')
    body = r.data.decode('utf-8')
    assert '<?xml' in body
    assert '<urlset' in body
    # All public pages should appear in sitemap
    assert '<loc>https://aramaic-root-atlas.onrender.com/</loc>' in body
    assert '<loc>https://aramaic-root-atlas.onrender.com/about</loc>' in body


def test_homepage_has_seo_meta(client):
    """Open Graph + Twitter Card + JSON-LD must be present on every page."""
    body = client.get('/?lang=en').data.decode('utf-8')
    assert 'og:title' in body
    assert 'og:image' in body
    assert 'twitter:card' in body
    assert '"@type": "SoftwareApplication"' in body
    assert 'citation_title' in body


def test_homepage_has_canonical_link(client):
    body = client.get('/?lang=en').data.decode('utf-8')
    assert '<link rel="canonical"' in body


def test_homepage_does_not_auto_load_ga(client):
    """Privacy gate: GA script must NOT be served by default; only the
    consent-gated injector function should mention googletagmanager.com."""
    body = client.get('/?lang=en').data.decode('utf-8')
    # An auto-loaded <script src="...googletagmanager...> is the violation.
    # The string can appear inside the consent-gated function declaration.
    import re
    auto_loaded = re.search(
        r'<script[^>]+src=["\']https?://www\.googletagmanager\.com',
        body,
    )
    assert auto_loaded is None, 'Google Analytics is being auto-loaded; should be opt-in only'


def test_visualize_page_renders_with_root_key(client):
    r = client.get('/visualize/sh-l-m?lang=en')
    assert r.status_code == 200


def test_read_page_renders_with_book_chapter(client):
    r = client.get('/read/Genesis/1?lang=en')
    assert r.status_code == 200


def test_constellation_page_renders(client):
    r = client.get('/constellation?book=Matthew&chapter=5&v_start=1&v_end=5&lang=en')
    assert r.status_code == 200
