def test_torch_import():
    import torch
    assert torch.__version__ is not None
