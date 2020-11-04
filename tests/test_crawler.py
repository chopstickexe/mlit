from mlit.crawler import Normalizer

def test_normalizer_remove_spaces():
    txt = "ブレーキが   効かないことがある。\
    "
    txt = Normalizer.remove_spaces(txt)
    assert txt == "ブレーキが効かないことがある。"