from sigmoid2025 import greet


def test_greet_returns_expected_message():
    assert greet("world") == "Hello, world!"
