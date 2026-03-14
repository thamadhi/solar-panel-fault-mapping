# import streamlit as st
# from dashboard.app_state import init_state


# class DummySessionState(dict):
#     pass


# def test_init_state_sets_defaults(monkeypatch):
#     fake_state = DummySessionState()

#     # Patch streamlit.session_state to the fake dict
#     monkeypatch.setattr(st, "session_state", fake_state, raising=False)

#     init_state()

#     assert fake_state.get("user") is not None
#     assert fake_state.get("history") == []
#     assert fake_state.get("show_ath") is False
#     assert fake_state.get("auth_view") == "login"
#     assert fake_state.get("api_token") is None
