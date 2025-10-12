import sys
import types
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model_utils import HardwareSettings, ModelManager


@pytest.fixture
def manager(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Prevent GPU discovery side effects
    monkeypatch.setattr('GPUtil.getGPUs', lambda: [], raising=False)

    return ModelManager(workspace_dir=str(tmp_path / "workspace"))


def mock_cuda(monkeypatch, available: bool, bf16: bool = False):
    monkeypatch.setattr('torch.cuda.is_available', lambda: available, raising=False)
    if hasattr(__import__('torch').cuda, 'is_bf16_supported'):
        monkeypatch.setattr('torch.cuda.is_bf16_supported', lambda: bf16, raising=False)
    if available:
        monkeypatch.setattr(torch.cuda, 'device_count', lambda: 1, raising=False)
        monkeypatch.setattr(torch.cuda, 'current_device', lambda: 0, raising=False)
        monkeypatch.setattr(torch.cuda, 'set_device', lambda *args, **kwargs: None, raising=False)
        cuda_init = getattr(torch._C, '_cuda_init', None)
        if cuda_init is not None:
            monkeypatch.setattr(torch._C, '_cuda_init', lambda: None, raising=False)


def mock_mps(monkeypatch, available: bool):
    if hasattr(torch.backends, 'mps'):
        monkeypatch.setattr(torch.backends.mps, 'is_available', lambda: available, raising=False)
    else:
        mps_backend = types.SimpleNamespace(is_available=lambda: available)
        monkeypatch.setattr(torch.backends, 'mps', mps_backend, raising=False)


def test_hardware_settings_auto_cpu(manager, monkeypatch):
    mock_cuda(monkeypatch, available=False)
    mock_mps(monkeypatch, available=False)

    settings = manager.get_hardware_settings('auto', 'toy')

    assert isinstance(settings, HardwareSettings)
    assert settings.device == 'cpu'
    assert settings.training_overrides['per_device_train_batch_size'] == 1
    assert settings.training_overrides['gradient_checkpointing'] is True
    assert settings.precision == 'fp32'


def test_hardware_settings_prefers_cuda(manager, monkeypatch):
    mock_cuda(monkeypatch, available=True, bf16=True)
    mock_mps(monkeypatch, available=True)

    settings = manager.get_hardware_settings('windows_nvidia', 'base')

    assert settings.device == 'cuda'
    assert settings.training_overrides['fp16'] is True
    assert settings.training_overrides['bf16'] is True
    assert settings.training_overrides['dataloader_pin_memory'] is True
    assert settings.precision == 'bf16'


def test_hardware_settings_prefers_mps(manager, monkeypatch):
    mock_cuda(monkeypatch, available=False)
    mock_mps(monkeypatch, available=True)

    settings = manager.get_hardware_settings('apple_silicon', '1b')

    assert settings.device == 'mps'
    assert settings.training_overrides['per_device_train_batch_size'] == 1
    assert settings.training_overrides['gradient_accumulation_steps'] >= 16
    assert settings.training_overrides['gradient_checkpointing'] is True


def test_training_arguments_reflect_overrides(manager, monkeypatch, tmp_path):
    mock_cuda(monkeypatch, available=False)
    mock_mps(monkeypatch, available=False)

    overrides = {
        'per_device_train_batch_size': 3,
        'gradient_accumulation_steps': 5,
        'dataloader_pin_memory': False,
        'fp16': False,
        'bf16': False,
        'tf32': False,
        'gradient_checkpointing': True,
    }

    args = manager._build_training_arguments(
        project_slug='demo',
        epochs=3,
        learning_rate=2e-5,
        overrides=overrides,
    )

    assert args.per_device_train_batch_size == overrides['per_device_train_batch_size']
    assert args.gradient_accumulation_steps == overrides['gradient_accumulation_steps']
    assert args.fp16 is False
    assert args.tf32 is False
    assert args.gradient_checkpointing is True
    assert args.num_train_epochs == 3


def test_system_info_reports_profiles(manager, monkeypatch):
    mock_cuda(monkeypatch, available=False)
    mock_mps(monkeypatch, available=True)

    info = manager.get_system_info()

    assert 'hardware_profiles' in info
    assert info['hardware_profiles']['apple_silicon']['available'] is True
    assert info['hardware_profiles']['windows_nvidia']['available'] is False
    assert 'precision' in info
