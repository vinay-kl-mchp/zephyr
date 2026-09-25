# Copyright (c) 2017 Linaro Limited.
# Copyright (c) 2021 Espressif Systems (Shanghai) Co., Ltd.
# Copyright (c) 2026 Muhammed Asif P
# SPDX-FileCopyrightText: Copyright (c) 2026 Microchip Technology Inc.
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import platform
import re
import shlex
import shutil
from pathlib import Path

from runners.core import RunnerCaps, RunnerConfig, ZephyrBinaryRunner

MPLABX_COMMON_LOCATIONS = [
    # Windows
    "C:/Program Files/Microchip",
    "C:/Program Files (x86)/Microchip",
    # Linux
    "/opt/microchip",
    "/usr/local/microchip",
    # macOS
    "/Applications/microchip",
]


class MPLABIPEBinaryRunner(ZephyrBinaryRunner):
    """Runner for Flashing Application using Microchip MPLAB IPE"""

    def __init__(
        self,
        cfg: RunnerConfig,
        tool: str,
        part: str,
        dev_id: str | None = None,
        erase: bool = False,
        verify: bool = False,
    ):
        super().__init__(cfg)
        self.tool = tool
        self.part = part
        self.dev_id = dev_id
        self.erase = erase
        self.verify = verify

    @classmethod
    def name(cls):
        return "mplab_ipe"

    @classmethod
    def capabilities(cls):
        return RunnerCaps(commands={"flash"}, erase=True, dev_id=True)

    @classmethod
    def do_add_parser(cls, parser):
        parser.add_argument(
            "--tool",
            required=True,
            help="Programming probe model, e.g. PKOB4. Passed unchanged to the MPLAB IPE",
        )
        parser.add_argument(
            "--part", required=True, help="Target device name, e.g. 32CX1025SG61128"
        )
        parser.add_argument(
            "--verify", action=argparse.BooleanOptionalAction, help="Verify after programming"
        )

    @classmethod
    def do_create(cls, cfg: RunnerConfig, args):
        return MPLABIPEBinaryRunner(
            cfg,
            tool=args.tool,  # probe type
            part=args.part,  # part number of the SoC
            dev_id=args.dev_id,
            erase=args.erase,
            verify=args.verify,
        )

    def do_run(self, command: str, **kwargs):
        if command == "flash":
            self.flash()
        else:
            raise ValueError(f"Unsupported command: {command}")

    def flash(self):
        self.ensure_output('hex')
        hex_file = self.cfg.hex_file

        prefix = self.find_ipecmd_prefix()

        args = [
            f"-P{self.part}",  # part number of the SoC
            f"-F{hex_file}",
            "-M",  # Program all memories
            "-OL",  # Release from reset
            "-OK",  # Silent connect with the tool and hardware
        ]

        if self.dev_id:
            args.append(f"-TS{self.dev_id}")  # Select programmer by serial number
        elif self.tool is not None:
            args.append(f"-TP{self.tool}")  # Select programmer by name of the tool

        if self.erase:
            args.append("-E")

        if self.verify:
            args.append("-V")

        cmd = prefix + args

        self.logger.info("Running: %s", " ".join(shlex.quote(p) for p in cmd))
        self.check_call(cmd)

    def find_ipecmd_prefix(self):
        """Return the command prefix used to invoke ipecmd.

        Checks PATH for ipecmd.exe/ipecmd.sh first, since that's cheap and
        is what repeated invocations (e.g. under Twister) hit most often.
        Only if that fails does it fall back to auto-discovering a MPLAB X
        install under common installation locations (locating ipecmd.exe
        directly on Windows, or ipecmd.jar plus the bundled java binary on
        Linux).
        """
        exe_name = "ipecmd.exe" if os.name == "nt" else "ipecmd.sh"
        exe = shutil.which(exe_name)
        if exe:
            return [exe]

        version_path = self.find_mplabx_version_dir()
        if version_path is not None:
            if platform.system() == "Windows":
                ipecmd_exe = self.find_ipecmd_tool(version_path, "ipecmd.exe")
                if ipecmd_exe:
                    return [str(ipecmd_exe)]
            elif platform.system() == "Linux":
                ipecmd_jar = self.find_ipecmd_tool(version_path, "ipecmd.jar")
                java_bin = self.find_java_bin(version_path)
                if ipecmd_jar and java_bin and os.access(java_bin, os.X_OK):
                    return [str(java_bin), "-jar", str(ipecmd_jar)]

        return [self.require(exe_name)]

    def find_mplabx_base(self):
        """Find the MPLAB X installation directory.

        Only lists each candidate location's immediate children instead
        of recursively walking it, since the mplabx directory is always
        a direct child of one of these locations - a full os.walk() over
        broad roots like C:\\Program Files or /home needlessly traverses
        every unrelated subdirectory on the system.
        """
        for base in MPLABX_COMMON_LOCATIONS:
            base_path = Path(base)
            if not base_path.is_dir():
                continue
            try:
                for candidate in base_path.iterdir():
                    if candidate.is_dir() and candidate.name.lower() == "mplabx":
                        return candidate
            except PermissionError:
                self.logger.debug(f"Permission denied scanning {base_path} for MPLAB X")
                continue
        return None

    def find_mplabx_version_dir(self):
        mplabx_base = self.find_mplabx_base()
        if not mplabx_base:
            return None

        version_re = re.compile(r"v(\d+(?:\.\d+)*)")

        def version_key(version_dir):
            return tuple(int(part) for part in version_re.fullmatch(version_dir.name)[1].split("."))

        versions = sorted(
            (
                p
                for p in mplabx_base.glob("v*/")
                if p.is_dir() and version_re.fullmatch(p.name)
            ),
            key=version_key,
        )
        return versions[-1] if versions else None

    @staticmethod
    def find_java_bin(version_path):
        java_name = "java.exe" if platform.system() == "Windows" else "java"
        java_dirs = list(version_path.glob(f"sys/java/*/bin/{java_name}"))
        return java_dirs[0] if java_dirs else None

    @staticmethod
    def find_ipecmd_tool(version_path, tool):
        ipe_dir = version_path / "mplab_platform" / "mplab_ipe"
        if not ipe_dir.is_dir():
            return None
        for root, _, files in os.walk(ipe_dir):
            if tool in files:
                return Path(root) / tool
        return None
