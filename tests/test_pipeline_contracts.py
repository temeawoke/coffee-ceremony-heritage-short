from pipeline.contracts import load_storyboard, shot_output_path


def test_contract_loader_reads_project_title():
    storyboard = load_storyboard()
    assert storyboard["project"]["title"] == "The Ethiopian Coffee Ceremony"


def test_shot_output_path_is_inside_outputs(tmp_path, monkeypatch):
    import pipeline.contracts as contracts
    monkeypatch.setattr(contracts, "OUTPUTS_DIR", tmp_path)
    path = shot_output_path("images", "shot_01", ".png")
    assert path == tmp_path / "images" / "shot_01.png"
    assert path.parent.exists()


def test_shot_output_path_rejects_invalid_id():
    import pytest
    with pytest.raises(ValueError):
        shot_output_path("images", "../../secret", ".png")
