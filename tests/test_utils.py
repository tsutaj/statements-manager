from statements_manager.src.utils import find_in_parents


def test_find_in_parents(tmp_path):
    """
    tmp_path --- sub1 --- sub2 --- sub3
              |        |
              |        -- filename
              |
              -- sub4
    """
    dir_sub1 = tmp_path / "sub1"
    dir_sub2sub3 = dir_sub1 / "sub2" / "sub3"
    dir_sub2sub3.mkdir(parents=True)
    dir_sub4 = tmp_path / "sub4"
    dir_sub4.mkdir(parents=True)
    file = dir_sub1 / "filename"
    file.touch()
    assert find_in_parents(tmp_path / "sub1" / "filename") == file
    assert find_in_parents(tmp_path / "sub1" / "sub2" / "filename") == file
    assert find_in_parents(tmp_path / "sub1" / "sub2" / "sub3" / "filename") == file
    assert find_in_parents(tmp_path / "filename") is None
    assert find_in_parents(tmp_path / "sub4" / "filename") is None
    assert find_in_parents(tmp_path / "sub5" / "filename") is None
