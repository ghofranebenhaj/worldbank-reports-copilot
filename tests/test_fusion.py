from src.fusion import rrf


def test_item_in_both_lists_wins():
    assert rrf([[1, 2], [2, 3]])[0] == 2
