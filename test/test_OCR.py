from torch.cuda import is_available


def test_is_cuda_avaible():
    assert is_available()
