import pathlib
import types

import kconfiglib
import pytest

ROOT = pathlib.Path(__file__).parent.parent
CONFIGS = sorted((ROOT / "test" / "configs").glob("*.config")) + sorted(
    (ROOT / "board_configs").glob("*.config")
)


@pytest.mark.parametrize("config_path", CONFIGS, ids=lambda p: p.stem)
def test_defconfig_roundtrip_reproduces_expanded_config(
    config_path, tmp_path, kconfig_tree
):
    # Loading a minimized defconfig into a fresh Kconfig instance must
    # expand back to the config that produced it. Compare canonical
    # write_config() output, not raw defconfig text.
    kconf = kconfig_tree()
    kconf.load_config(str(config_path), replace=True)

    expanded_path = tmp_path / "expanded.config"
    kconf.write_config(str(expanded_path), save_old=False)
    expanded_before = expanded_path.read_text()

    defconfig_path = tmp_path / "defconfig"
    kconf.write_min_config(str(defconfig_path))

    kconf2 = kconfig_tree()
    kconf2.load_config(str(defconfig_path), replace=True)
    # kconfiglib silently drops assignments to symbols the tree doesn't
    # define — assert there are none for a same-tree round trip.
    assert kconf2.missing_syms == []

    replayed_path = tmp_path / "replayed.config"
    kconf2.write_config(str(replayed_path), save_old=False)
    assert replayed_path.read_text() == expanded_before


def test_handlekconfig_accepts_a_real_all_defaults_board_config(
    tmp_path, kconfig_tree
):
    # atmega2560.config matches the Kconfig tree's defaults exactly, so
    # write_min_config() produces a zero-byte defconfig for it.
    # HandleKConfig must accept that, not treat it as a failure.
    from scripts import buildcommands

    kconf = kconfig_tree()
    kconf.load_config(
        str(ROOT / "test" / "configs" / "atmega2560.config"), replace=True
    )
    defconfig_path = tmp_path / "defconfig"
    kconf.write_min_config(str(defconfig_path))

    # Verify the empty case actually occurs rather than assuming it.
    assert defconfig_path.read_text() == ""

    handler = buildcommands.HandleKConfig()
    options = types.SimpleNamespace(kconfig=str(defconfig_path))
    handler.generate_code(options)  # must not raise

    data = {}
    handler.update_data_dictionary(data)
    assert data == {"kconfig": defconfig_path.read_text()}


@pytest.mark.parametrize(
    "low_level, custom, expected",
    [(0, None, "rp2040"), (2, None, "rp2040"), (2, "INDX", "INDX")],
)
def test_usb_product_follows_mcu_across_arch_switch(
    low_level, custom, expected, tmp_path, kconfig_tree
):
    # A .config saved for one USB MCU and reused for another must not
    # keep the old MCU name as the USB product, while an explicit custom
    # product must survive the switch (issue #970).
    config_path = str(tmp_path / ".config")
    kconf = kconfig_tree()
    kconf.syms["LOW_LEVEL_OPTIONS"].set_value(low_level)
    kconf.syms["MACH_STM32"].set_value(2)
    kconf.syms["MACH_STM32F446"].set_value(2)
    if custom is not None:
        kconf.syms["USB_PRODUCT_FROM_MCU"].set_value(0)
        kconf.syms["USB_PRODUCT"].set_value(custom)
    kconf.write_config(config_path, save_old=False)

    kconf = kconfig_tree()
    kconf.load_config(config_path)
    kconf.syms["MACH_RPXXXX"].set_value(2)
    kconf.syms["MACH_RP2040"].set_value(2)
    assert kconf.syms["USB_PRODUCT"].str_value == expected


def config_assignments(config_path):
    # Yield (symbol, value) for each assignment line of a .config file
    for line in config_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("CONFIG_") and "=" in line:
            name, value = line[len("CONFIG_") :].split("=", 1)
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = kconfiglib.unescape(value[1:-1])
            yield name, value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            yield line[len("# CONFIG_") : -len(" is not set")], "n"


def wrong_assignments(kconf, config_path):
    # List (symbol, wanted, got) for assignments the loaded tree ignored
    wrong = []
    for name, wanted in config_assignments(config_path):
        sym = kconf.syms.get(name)
        got = sym.str_value if sym is not None and sym.nodes else None
        if got != wanted:
            wrong.append((name, wanted, got))
    return wrong


@pytest.mark.parametrize("config_path", CONFIGS, ids=lambda p: p.stem)
def test_config_assignments_take_effect(config_path, kconfig_tree):
    # kconfiglib silently drops assignments to undefined or hidden
    # symbols, so a stale test config would build a different firmware
    # than the one it names. Every assignment must survive loading.
    kconf = kconfig_tree()
    kconf.load_config(str(config_path), replace=True)
    assert wrong_assignments(kconf, config_path) == []


def test_wrong_assignments_reports_undefined_symbol(tmp_path, kconfig_tree):
    config_path = tmp_path / "dead.config"
    config_path.write_text(
        "CONFIG_MACH_STM32=y\nCONFIG_WANT_DOES_NOT_EXIST=n\n"
    )
    kconf = kconfig_tree()
    kconf.load_config(str(config_path), replace=True)
    assert wrong_assignments(kconf, config_path) == [
        ("WANT_DOES_NOT_EXIST", "n", None)
    ]


@pytest.mark.parametrize(
    "written, loaded",
    [(r"Erik\"board", 'Erik"board'), (r"Erik\\board", "Erik\\board")],
    ids=["quote", "backslash"],
)
def test_wrong_assignments_accepts_escaped_string_values(
    written, loaded, tmp_path, kconfig_tree
):
    # A .config escapes " and \ inside string values, and the loaded
    # symbol holds the unescaped string; that is a match, not a drop.
    config_path = tmp_path / "escaped.config"
    config_path.write_text(
        "CONFIG_LOW_LEVEL_OPTIONS=y\nCONFIG_MACH_STM32=y\n"
        f'CONFIG_USB_MANUFACTURER="{written}"\n'
    )
    kconf = kconfig_tree()
    kconf.load_config(str(config_path), replace=True)
    assert kconf.syms["USB_MANUFACTURER"].str_value == loaded
    assert wrong_assignments(kconf, config_path) == []
