import os
import tempfile
from collections.abc import Mapping
from subprocess import (
    PIPE,
    CalledProcessError,
    run,
)


class AmtoolResult:
    """This class represents a amtool command execution result"""

    def __init__(self, is_ok: bool, message: str) -> None:
        self.is_ok = is_ok
        self.message = message

    def __str__(self) -> str:
        return str(self.message).replace("\n", "")

    def __bool__(self) -> bool:
        return self.is_ok


def check_config(yaml_config: str, amtool_version: str) -> AmtoolResult:
    """Run amtool check rules on the given yaml string"""
    if not (version_check := check_amtool_version(amtool_version)):
        return version_check

    with tempfile.NamedTemporaryFile(mode="w+") as fp:
        fp.write(yaml_config)
        fp.flush()
        cmd = [f"amtool-{amtool_version}", "check-config", fp.name]
        result = _run_cmd(cmd)

    return result


def config_routes_test(yaml_config: str, labels: Mapping[str, str], amtool_version : str="0.24.0") -> AmtoolResult:
    if not (version_check := check_amtool_version(amtool_version)):
        return version_check

    labels_lst = [f"{key}={value}" for key, value in labels.items()]
    with tempfile.NamedTemporaryFile(mode="w+") as fp:
        fp.write(yaml_config)
        fp.flush()
        cmd = [f"amtool-{amtool_version}", "config", "routes", "test", "--config.file", fp.name]
        cmd.extend(labels_lst)
        result = _run_cmd(cmd)

    return result


def versions() -> list[AmtoolResult]:
    """Returns the available versions of amtool"""
    available_versions = []
    for path in os.environ["PATH"].split(os.pathsep):
        files = os.listdir(path)
        for file in files:
            filename = os.path.basename(file)
            if filename.startswith("amtool-"):
                version = filename.split("-")[1]
                available_versions.append(AmtoolResult(True, version))
    return available_versions


def check_amtool_version(version: str) -> AmtoolResult:
    """Checks if a given version of amtool is present"""
    all_versions = versions()
    if version not in map(str, all_versions):
        return AmtoolResult(False, f"Could not find amtool {version}. Available: {all_versions}")
    return AmtoolResult(True, version)


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
