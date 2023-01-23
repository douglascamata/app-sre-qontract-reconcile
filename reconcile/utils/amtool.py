import os
import re
import tempfile
from typing import Optional
from collections.abc import Mapping
from subprocess import (
    PIPE,
    CalledProcessError,
    run,
)

MIN_VERSION = "0.24.0"


class AmtoolResult:
    """This class represents a amtool command execution result"""

    def __init__(self, is_ok: bool, message: str) -> None:
        self.is_ok = is_ok
        self.message = message

    def __str__(self) -> str:
        return str(self.message).replace("\n", "")

    def __bool__(self) -> bool:
        return self.is_ok


class Amtool:
    """This class represents an amtool binary"""

    def __init__(self, bin_path: str, version: str) -> None:
        self.bin_path = bin_path
        self.version = version

    def run_cmd(self, cmd: list[str]) -> AmtoolResult:
        return _run_cmd([self.bin_path, *cmd])


def check_config(yaml_config: str, amtool_version: str = MIN_VERSION) -> AmtoolResult:
    """Run amtool check rules on the given yaml string"""
    amtool, result = get_amtool_version(amtool_version)
    if not result:
        return result
    else:
        assert amtool is not None

    with tempfile.NamedTemporaryFile(mode="w+") as fp:
        fp.write(yaml_config)
        fp.flush()
        result = amtool.run_cmd(["check-config", fp.name])

    return result


def config_routes_test(
    yaml_config: str, labels: Mapping[str, str], amtool_version: str = MIN_VERSION
) -> AmtoolResult:
    amtool, result = get_amtool_version(amtool_version)
    if not result:
        return result
    else:
        assert amtool is not None

    labels_lst = [f"{key}={value}" for key, value in labels.items()]
    with tempfile.NamedTemporaryFile(mode="w+") as fp:
        fp.write(yaml_config)
        fp.flush()
        cmd = [
            "config",
            "routes",
            "test",
            "--config.file",
            fp.name,
        ]
        cmd.extend(labels_lst)
        result = amtool.run_cmd(cmd)

    return result


def versions() -> dict[str, Amtool]:
    """Returns the available versions of amtool"""
    available_versions = {}
    for path in os.environ["PATH"].split(os.pathsep):
        files = os.listdir(path)
        for file in files:
            filename = os.path.basename(file)
            if filename.startswith("amtool"): 
                if result := parse_amtool_version(file):
                    available_versions[result.message] = Amtool(file, result.message)
    return available_versions


def parse_amtool_version(bin_path: str):
    """Returns the am version parsed from the binary by passing --version"""
    result = _run_cmd([bin_path, "--version"])

    pattern = re.compile("^amtool, version (?P<version>[^ ]+) .+")
    if m := pattern.match(result.message):
        return AmtoolResult(True, m.group("version"))
    return AmtoolResult(False, f"Unexpected amtool --version output {result.message}")


def get_amtool_version(version: str) -> tuple[Optional[Amtool], AmtoolResult]:
    """Checks if a given version of amtool is present"""
    all_versions = versions()
    amtool = all_versions.get(version)
    if not amtool:
        return (
            None,
            AmtoolResult(
                False, f"Could not find amtool {version}. Available: {all_versions}"
            ),
        )
    return (amtool, AmtoolResult(True, version))


def _run_cmd(cmd: list[str]) -> AmtoolResult:
    try:
        result = run(cmd, stdout=PIPE, stderr=PIPE, check=True)
    except CalledProcessError as e:
        msg = f'Error running amtool command [{" ".join(cmd)}]'
        if e.stdout:
            msg += f" {e.stdout.decode()}"
        if e.stderr:
            msg += f" {e.stderr.decode()}"

        return AmtoolResult(False, msg)

    # some amtool commands return also in stderr even in non-error
    output = result.stdout.decode() + result.stderr.decode()

    return AmtoolResult(True, output)
