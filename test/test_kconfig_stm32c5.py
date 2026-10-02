# ABOUTME: Checks the stm32c5 entries in the stm32 Kconfig menus: the values
# ABOUTME: derived for each part and the options offered or hidden for it.
import pytest

STM32C5_PARTS = [
    ("MACH_STM32C551", "stm32c551xx"),
    ("MACH_STM32C552", "stm32c552xx"),
]


def _select(kconfig_tree, mach, *extra):
    kconf = kconfig_tree()
    for name in ("LOW_LEVEL_OPTIONS", "MACH_STM32", mach) + extra:
        kconf.syms[name].set_value(2)
    return kconf


def _visible(kconf, name):
    return kconf.syms[name].visibility > 0


@pytest.mark.parametrize("mach,mcu", STM32C5_PARTS)
def test_stm32c5_part_values(kconfig_tree, mach, mcu):
    kconf = _select(kconfig_tree, mach)
    assert kconf.syms["MCU"].str_value == mcu
    assert kconf.syms["CLOCK_FREQ"].str_value == "144000000"
    assert kconf.syms["FLASH_SIZE"].str_value == "0x40000"
    assert kconf.syms["RAM_SIZE"].str_value == "0x20000"


def test_stm32c5_crystal_choices(kconfig_tree):
    kconf = _select(kconfig_tree, "MACH_STM32C552")
    for name in ("8M", "16M", "24M", "INTERNAL"):
        assert _visible(kconf, "STM32_CLOCK_REF_" + name), name
    for name in ("12M", "20M", "25M"):
        assert not _visible(kconf, "STM32_CLOCK_REF_" + name), name


def test_stm32c5_serial_choices(kconfig_tree):
    kconf = _select(kconfig_tree, "MACH_STM32C552")
    offered = [
        "STM32_SERIAL_USART1",
        "STM32_SERIAL_USART1_ALT_PB7_PB6",
        "STM32_SERIAL_USART2",
        "STM32_SERIAL_USART2_ALT_PD6_PD5",
        "STM32_SERIAL_USART3_ALT_PD9_PD8",
        "STM32_SERIAL_UART4",
    ]
    hidden = [
        "STM32_SERIAL_USART3",  # PB11 does not exist on stm32c5
        "STM32_SERIAL_USART2_ALT_PA15_PA14",
        "STM32_SERIAL_USART2_ALT_PB4_PB3",
        "STM32_SERIAL_USART3_ALT_PC11_PC10",
        "STM32_SERIAL_USART5",
        "STM32_SERIAL_USART6",
    ]
    for name in offered:
        assert _visible(kconf, name), name
    for name in hidden:
        assert not _visible(kconf, name), name


def test_stm32c5_bootloader_offsets(kconfig_tree):
    kconf = _select(kconfig_tree, "MACH_STM32C552")
    for name in ("2000", "4000", "0000"):
        assert _visible(kconf, "STM32_FLASH_START_" + name), name
    for name in ("800", "1000", "5000", "8000", "C000", "10000", "20000"):
        assert not _visible(kconf, "STM32_FLASH_START_" + name), name


@pytest.mark.parametrize("mach,mcu", STM32C5_PARTS)
def test_stm32c5_offers_usb(kconfig_tree, mach, mcu):
    kconf = _select(kconfig_tree, mach)
    assert _visible(kconf, "STM32_USB_PA11_PA12")
    assert kconf.syms["STM32_USB_PA11_PA12"].str_value == "y"
    assert kconf.syms["STM32_DFU_ROM_ADDRESS"].str_value == "0x0bf80000"


STM32C5_CAN_PINS = ["PB8_PB9", "PB5_PB6", "PB12_PB13", "PD0_PD1"]
OTHER_CAN_PINS = ["PB0_PB1", "PD12_PD13", "PC2_PC3", "PH13_PH14"]


def test_stm32c552_can_choices(kconfig_tree):
    kconf = _select(kconfig_tree, "MACH_STM32C552")
    for name in ["STM32_CANBUS_PA11_PA12", "STM32_CANBUS_PA11_PB9"]:
        assert _visible(kconf, name), name
    for pins in STM32C5_CAN_PINS:
        assert _visible(kconf, "STM32_MMENU_CANBUS_" + pins), pins
    for pins in OTHER_CAN_PINS + ["PI9_PH13"]:
        assert not _visible(kconf, "STM32_MMENU_CANBUS_" + pins), pins
    assert _visible(kconf, "STM32_USBCANBUS_PA11_PA12")


def test_stm32c552_bridge_can_choices(kconfig_tree):
    kconf = _select(kconfig_tree, "MACH_STM32C552", "STM32_USBCANBUS_PA11_PA12")
    for pins in STM32C5_CAN_PINS:
        assert _visible(kconf, "STM32_CMENU_CANBUS_" + pins), pins
    for pins in OTHER_CAN_PINS + ["PI9_PH13"]:
        assert not _visible(kconf, "STM32_CMENU_CANBUS_" + pins), pins


def test_stm32c551_has_no_can(kconfig_tree):
    kconf = _select(kconfig_tree, "MACH_STM32C551")
    assert kconf.syms["HAVE_STM32_FDCANBUS"].str_value == "n"
    for name in ["STM32_CANBUS_PA11_PA12", "STM32_USBCANBUS_PA11_PA12"]:
        assert not _visible(kconf, name), name
