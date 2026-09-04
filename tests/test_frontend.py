from pathlib import Path


APP_JS = Path(__file__).parents[1] / "src" / "static" / "app.js"


def test_frontend_supports_participant_removal_and_refresh():
    source = APP_JS.read_text()

    assert 'class="participant-remove"' in source
    assert 'method: "DELETE"' in source
    assert 'await fetchActivities();' in source
