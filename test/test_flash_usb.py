# ABOUTME: Unit tests for scripts/flash_usb.py: which flashing routine each
# ABOUTME: mcu type maps to when running `make flash`.
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
_spec = importlib.util.spec_from_file_location(
    "flash_usb", ROOT / "scripts" / "flash_usb.py"
)
flash_usb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(flash_usb)


def test_stm32c5_uses_dfu_flashing():
    for mcutype in ("stm32c551xx", "stm32c552xx"):
        assert flash_usb.lookup_flash_func(mcutype) is flash_usb.flash_stm32f4


def test_existing_types_keep_their_flashing_routine():
    assert flash_usb.lookup_flash_func("stm32g0b1xx") is flash_usb.flash_stm32f4
    assert flash_usb.lookup_flash_func("stm32f103xe") is flash_usb.flash_stm32f1


def test_unknown_type_has_no_flashing_routine():
    assert flash_usb.lookup_flash_func("not-an-mcu") is None
