# ABOUTME: Unit tests for scripts/flash_usb.py: which flashing routine each
# ABOUTME: mcu type maps to when running `make flash`.
import importlib.util
import pathlib
import types

import pytest

ROOT = pathlib.Path(__file__).parent.parent
_spec = importlib.util.spec_from_file_location(
    "flash_usb", ROOT / "scripts" / "flash_usb.py"
)
flash_usb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(flash_usb)


def run_make_flash(monkeypatch, mcutype, start):
    # Dispatch `make flash` for an mcu type and record which external
    # flashing tool it runs, without running the tool
    calls = []

    def record_dfuutil(device, binfile, extra_flags=None, sudo=True):
        calls.append(("dfu-util", extra_flags))

    def record_hidflash(device, binfile, sudo=True):
        calls.append(("hid-flash", None))

    monkeypatch.setattr(flash_usb, "flash_dfuutil", record_dfuutil)
    monkeypatch.setattr(flash_usb, "flash_hidflash", record_hidflash)
    options = types.SimpleNamespace(
        mcutype=mcutype, device="0483:df11", start=start, sudo=False
    )
    flash_usb.lookup_flash_func(mcutype)(options, "out/klipper.bin")
    return calls


@pytest.mark.parametrize("mcutype", ["stm32c551xx", "stm32c552xx"])
@pytest.mark.parametrize("start", [0x8000000, 0x8002000, 0x8004000], ids=hex)
def test_stm32c5_uses_dfu_flashing(monkeypatch, mcutype, start):
    calls = run_make_flash(monkeypatch, mcutype, start)
    dfu_flags = ["-R", "-a", "0", "-s", "0x%x:leave" % (start,)]
    assert calls == [("dfu-util", dfu_flags)]


def test_existing_types_keep_their_flashing_routine():
    assert flash_usb.lookup_flash_func("stm32g0b1xx") is flash_usb.flash_stm32f4
    assert flash_usb.lookup_flash_func("stm32f103xe") is flash_usb.flash_stm32f1


def test_stm32f4_16kib_offset_keeps_hid_flashing(monkeypatch):
    calls = run_make_flash(monkeypatch, "stm32f407xx", 0x8004000)
    assert calls == [("hid-flash", None)]


def test_stm32f4_other_offsets_keep_dfu_flashing(monkeypatch):
    calls = run_make_flash(monkeypatch, "stm32f407xx", 0x8008000)
    assert calls == [("dfu-util", ["-R", "-a", "0", "-s", "0x8008000:leave"])]


def test_unknown_type_has_no_flashing_routine():
    assert flash_usb.lookup_flash_func("not-an-mcu") is None
