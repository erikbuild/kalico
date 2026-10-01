from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import typing

import pytest

import klippy.chelper

# Ensure chelper is built
klippy.chelper.get_ffi()


ROOT = pathlib.Path(__file__).parent.parent
KLIPPY_PLUGINS = ROOT / "klippy" / "plugins"
TESTING_PLUGIN = ROOT / "test" / "klippy_testing_plugin.py"

sys.path.insert(0, str(ROOT / "lib" / "kconfiglib"))
import kconfiglib  # noqa: E402

KCONFIG = str(ROOT / "src" / "Kconfig")


def pytest_addoption(parser):
    parser.addoption(
        "--dictdir",
        action="store",
        default=os.environ.get("DICTDIR", "dict"),
        help="Klipper build dictionary path",
    )


@pytest.fixture(scope="module")
def kconfig_tree():
    # src/Kconfig sources the generated, gitignored src/extras/Kconfig,
    # and kconfiglib resolves "source" paths relative to cwd, not the
    # Kconfig file's location. Regenerate src/extras/ and run from the
    # repo root so this doesn't depend on `make` having already run.
    previous = os.getcwd()
    os.chdir(ROOT)
    subprocess.run(
        ["bash", str(ROOT / "scripts" / "find-firmware-extras.sh")],
        cwd=ROOT,
        check=True,
    )
    try:
        yield lambda: kconfiglib.Kconfig(KCONFIG, suppress_traceback=True)
    finally:
        os.chdir(previous)


def pytest_sessionstart(session):
    link_path = KLIPPY_PLUGINS / "testing.py"
    if link_path.exists():
        return

    os.symlink(TESTING_PLUGIN, link_path)

    @session.config.add_cleanup
    def clean_symlink():
        os.unlink(link_path)


@pytest.fixture
def config_root(request, tmp_path):
    """
    This abuses type hinting to allow fixture usages to specify the source directory

    def test_foo(config_root: Annotated[pathlib.Path, "relative/path/to/my_config"]):
    """

    test_hints = typing.get_type_hints(request.function, include_extras=True)
    my_hint = test_hints[request.fixturename]
    _, src = typing.get_args(my_hint)
    src = pathlib.Path(request.node.fspath).parent / pathlib.Path(src)

    tmp_config_root = tmp_path / "printer"
    shutil.copytree(src, tmp_config_root)
    yield tmp_config_root
