"""Beginner-friction guardrails: Funnel enablement + passcode gravity.

Two things silently stall a first install:

1. Tailscale ships with Funnel OFF and only the admin console can turn it on.
   The installer used to check only that the `tailscale` CLI existed, so a
   beginner got a working app, no public URL, no QR code and no explanation.
2. One short numeric passcode gates a real shell (terminal, files, updater),
   which first-timers routinely underrate.

These tests fail if the guidance is dropped or stops naming what the passcode
protects. They assert on copy, not on behaviour, so they stay cheap.
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FUNNEL_ADMIN_URL = 'https://login.tailscale.com/admin/settings/funnel'

# Every surface a first-timer might read before giving up.
FUNNEL_GUIDANCE_FILES = [
    'decloud',
    'install.sh',
    'setup.ps1',
    'README.md',
    'docs/PERMANENT_TUNNEL.md',
    'templates/index.html',
]


@pytest.mark.parametrize('name', FUNNEL_GUIDANCE_FILES)
def test_funnel_enablement_points_at_the_admin_console(name):
    text = (ROOT / name).read_text(encoding='utf-8')
    assert FUNNEL_ADMIN_URL in text, f'{name} must say where Funnel is enabled'


def test_decloud_reports_disabled_funnel_instead_of_failing_silently():
    text = (ROOT / 'decloud').read_text(encoding='utf-8')
    # The preflight reads funnel status and matches Tailscale's wording.
    assert 'tailscale funnel status 2>&1' in text
    assert 'not enabled' in text
    # And there is a way to re-read the walkthrough later.
    assert 'funnel-help|funnel)' in text
    assert 'funnel_help' in text


def test_installer_walks_through_success_criteria():
    text = (ROOT / 'install.sh').read_text(encoding='utf-8')
    assert 'not enabled' in text  # detects the disabled tailnet early
    assert 'Funnel on' in text  # what success looks like
    assert 'funnel-help' in text  # pointer to the full walkthrough


def test_settings_state_what_the_passcode_protects():
    html = (ROOT / 'templates' / 'index.html').read_text(encoding='utf-8')
    assert 'id="passcode-warning"' in html
    # Not a "view-only" password: name the shell and the destructive bits.
    warning = html.split('id="passcode-warning"', 1)[1].split('</div>', 1)[0]
    assert 'unlocks a shell' in warning
    assert 'terminal' in warning
    assert 'file browser' in warning


def test_onboarding_lists_what_the_passcode_unlocks():
    html = (ROOT / 'templates' / 'index.html').read_text(encoding='utf-8')
    step = html.split('data-step="2"', 1)[1].split('data-step="3"', 1)[0]
    assert 'What this one code unlocks' in step
    for surface in ('terminal', 'files', 'Settings'):
        assert surface in step
    # Stronger option is documented without changing the auth model.
    assert '10 digits' in step


def test_onboarding_funnel_tip_is_wired_to_the_local_host_only():
    js = (ROOT / 'static' / 'js' / 'modules' / 'onboarding.js').read_text(encoding='utf-8')
    assert 'onboarding-funnel-tip' in js
    # Shown when browsing on the machine itself (no public URL to scan yet).
    body = js.split('function generateOnboardingQRs', 1)[1]
    assert "tip.style.display = ''" in body
    assert "tip.style.display = 'none'" in body
