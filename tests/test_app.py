import os
import importlib
import streamlit as st


def setup_module(module):
    # Ensure test mode before importing the app
    os.environ["ST_TESTING"] = "1"


def teardown_module(module):
    os.environ.pop("ST_TESTING", None)


def reload_app():
    # (re)import app with test guard by loading the source file directly
    root = os.path.dirname(os.path.dirname(__file__))
    app_path = os.path.join(root, "app.py")
    # Always load a fresh module instance from the file to ensure test isolation
    spec = importlib.util.spec_from_file_location("app", app_path)
    module = importlib.util.module_from_spec(spec)
    # Ensure module is available in sys.modules so importlib.reload works on subsequent calls
    import sys
    module.__spec__ = spec
    sys.modules["app"] = module
    # Ensure missing external modules are stubbed so the app import doesn't fail in tests
    import sys, types
    if "openai" not in sys.modules:
        fake_openai = types.ModuleType("openai")
        # Minimal OpenAI client placeholder
        class _FakeClient:
            def __init__(self, api_key=None):
                self.api_key = api_key
                self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda *args, **kwargs: None))
        fake_openai.OpenAI = _FakeClient
        sys.modules["openai"] = fake_openai
    if "gmail_send" not in sys.modules:
        fake_gmail = types.ModuleType("gmail_send")
        def _fake_send_email(to_email, subject, body):
            # no-op for tests
            return True
        fake_gmail.send_email = _fake_send_email
        sys.modules["gmail_send"] = fake_gmail
    spec.loader.exec_module(module)
    globals()["app"] = module
    return module


def test_confirm_send_success(monkeypatch):
    app = reload_app()

    # set initial session state
    st.session_state.clear()
    st.session_state["recipient"] = "user@example.com"
    st.session_state["drafts"] = []
    st.session_state["sent_history"] = []

    called = {"ok": False}

    def fake_send_email(to_email, subject, body):
        called["ok"] = True
        assert to_email == "user@example.com"
        assert "body" in body or isinstance(body, str)

    monkeypatch.setattr(app, "send_email", fake_send_email)

    # Call confirm send
    app._confirm_send("This is a test")

    assert called["ok"] is True
    assert st.session_state.get("send_result") == "success"
    assert len(st.session_state.get("sent_history", [])) == 1
    assert st.session_state.get("recipient") == ""
    assert st.session_state.get("prompt") == ""


def test_confirm_send_failure(monkeypatch):
    app = reload_app()

    st.session_state.clear()
    st.session_state["recipient"] = "user@example.com"
    st.session_state["sent_history"] = []

    def fake_send_email(to_email, subject, body):
        raise RuntimeError("SMTP down")

    monkeypatch.setattr(app, "send_email", fake_send_email)

    app._confirm_send("Test failure")

    assert st.session_state.get("send_result", "").startswith("error:")
    assert len(st.session_state.get("sent_history", [])) == 0
    assert st.session_state.get("recipient") == ""


def test_load_and_delete_draft():
    app = reload_app()

    st.session_state.clear()
    st.session_state["drafts"] = [{"to": "a@b.com", "body": "hello"}]

    app.load_draft(0)
    assert st.session_state.get("recipient") == "a@b.com"
    assert st.session_state.get("prompt") == "hello"

    app.delete_draft(0)
    assert st.session_state.get("drafts") == []


def test_render_styles_does_not_raise():
    app = reload_app()
    # Should not raise
    app.render_styles(dark=True)
    app.render_styles(dark=False)
