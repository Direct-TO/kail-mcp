"""SMB / Windows / Active Directory 相关工具实现。"""

import shlex
from datetime import datetime
from pathlib import Path

from ..input_sanitizer import InputSanitizer


class WindowsADToolsMixin:
    async def _tool_enum4linux_scan(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)
        options = args.get("options", "all")

        flag_map = {
            "all": "-a", "users": "-U", "shares": "-S",
            "policies": "-P", "groups": "-G",
        }
        flag = flag_map.get(options, "-a")

        cmd = ["enum4linux", flag, target]
        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("enum4linux"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_crackmapexec(self, args: dict) -> dict:
        """Ejecutar CrackMapExec"""
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)

        protocol = args.get("protocol", "smb")
        cmd = ["crackmapexec", protocol, target]

        if args.get("username"):
            cmd += ["-u", args["username"]]
        if args.get("password"):
            cmd += ["-p", args["password"]]
        if args.get("hash"):
            cmd += ["-H", args["hash"]]
        if args.get("module"):
            cmd += ["-M", args["module"]]
        if args.get("command"):
            cmd += ["-x", args["command"]]
        if args.get("exec_method"):
            cmd += ["--exec-method", args["exec_method"]]
        if args.get("port"):
            cmd += ["--port", str(args["port"])]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("crackmapexec"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_impacket_scripts(self, args: dict) -> dict:
        """Ejecutar scripts de Impacket"""
        script = args["script"]
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)
        impacket_script = Path("/usr/share/doc/python3-impacket/examples") / script
        if not impacket_script.is_file():
            return self._error(f"Impacket script not found: {impacket_script}")

        username = args.get("username")
        password = args.get("password")
        domain = args.get("domain", "")
        ntlm_hash = args.get("hash")

        def _identity(include_target: bool) -> str:
            if not username:
                raise ValueError(f"username is required for {script}")
            identity = f"{domain}/{username}" if domain else username
            if password:
                identity = f"{identity}:{password}"
            if include_target:
                identity = f"{identity}@{target}"
            return identity

        def _add_hash(cmd: list[str]) -> None:
            if ntlm_hash:
                cmd += ["-hashes", ntlm_hash]

        # Construir comando base
        if script in ["psexec.py", "wmiexec.py", "smbexec.py"]:
            cmd = [str(impacket_script)]
            _add_hash(cmd)
            cmd.append(_identity(include_target=True))

            if args.get("command"):
                cmd.append(args["command"])

        elif script == "secretsdump.py":
            cmd = [str(impacket_script)]
            _add_hash(cmd)
            cmd.append(_identity(include_target=True))

        elif script in ["GetUserSPNs.py", "GetNPUsers.py"]:
            cmd = [str(impacket_script)]
            _add_hash(cmd)
            cmd += [_identity(include_target=False), "-dc-ip", target]
        elif script in ["ticketer.py", "raiseChild.py"]:
            cmd = [str(impacket_script)]
            _add_hash(cmd)
            cmd += [_identity(include_target=False), "-dc-ip", target]
        else:
            return self._error(f"Unsupported Impacket script: {script}")

        if args.get("port"):
            cmd += ["-port", str(args["port"])]
        if args.get("extra_args"):
            cmd += shlex.split(args["extra_args"])

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("impacket"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_bloodhound_enum(self, args: dict) -> dict:
        """Enumeración con BloodHound"""
        target = args["target"]
        username = args["username"]
        password = args["password"]
        domain = args["domain"]
        collector = args.get("collector", "BloodHound.py")

        if collector != "BloodHound.py":
            return self._error("Only BloodHound.py is supported in this Linux Docker MCP image.")

        cmd = ["bloodhound-python", "-u", username, "-p", password, "-d", domain, "-dc", target]
        if args.get("collection_methods"):
            methods = ",".join(args["collection_methods"])
            cmd += ["-c", methods]
        if args.get("zip_filename"):
            cmd += ["--zip", args["zip_filename"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, 300)
        return self._ok(stdout if stdout else stderr)

    async def _tool_netexec(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)
        protocol = args.get("protocol", "smb")
        extra = args.get("extra_args", "")

        cmd = ["netexec", protocol, target]
        if args.get("username"):
            cmd += ["-u", args["username"]]
        if args.get("password"):
            cmd += ["-p", args["password"]]
        if args.get("hash"):
            cmd += ["-H", args["hash"]]
        if args.get("module"):
            cmd += ["-M", args["module"]]
        if args.get("command"):
            cmd += ["-x", args["command"]]
        if args.get("port"):
            cmd += ["--port", str(args["port"])]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("netexec"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_evil_winrm_shell(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)
        username = args["username"]
        command = args.get("command", "").strip()
        if not command:
            return self._error("command is required; interactive Evil-WinRM sessions are not supported by this MCP tool.")
        if not args.get("password") and not args.get("hash"):
            return self._error("Provide password or hash.")

        cmd = ["evil-winrm", "-i", target, "-u", username]
        if args.get("password"):
            cmd += ["-p", args["password"]]
        if args.get("hash"):
            cmd += ["-H", args["hash"]]
        if args.get("domain"):
            cmd += ["-r", args["domain"]]
        if args.get("scripts_path"):
            cmd += ["-s", InputSanitizer.sanitize_path(args["scripts_path"])]
        if args.get("extra_args"):
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(args["extra_args"]))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdin_text = f"{command}\nexit\n"
        stdout, stderr, rc = await self._run_subprocess_with_input(cmd, stdin_text, self._timeout_for("evil_winrm"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_certipy_ad(self, args: dict) -> dict:
        action = args.get("action", "find")
        cmd = ["certipy-ad", action]
        target = args.get("target", "").strip()
        if target:
            cmd += ["-target", InputSanitizer.sanitize_target(target)]
        if args.get("username"):
            identity = args["username"]
            if args.get("domain") and "@" not in identity and "\\" not in identity and "/" not in identity:
                identity = f"{identity}@{args['domain']}"
            cmd += ["-u", identity]
        if args.get("password"):
            cmd += ["-p", args["password"]]
        if args.get("hash"):
            cmd += ["-hashes", args["hash"]]
        if args.get("dc_ip"):
            cmd += ["-dc-ip", InputSanitizer.sanitize_target(args["dc_ip"])]
        if args.get("ca"):
            cmd += ["-ca", args["ca"]]
        if args.get("template"):
            cmd += ["-template", args["template"]]
        if args.get("extra_args"):
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(args["extra_args"]))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("certipy_ad"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_enum4linux_ng_scan(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)
        options = args.get("options", "all")
        extra = args.get("extra_args", "")

        flag_map = {
            "all": "-A", "users": "-U", "groups": "-G", "shares": "-S",
            "policy": "-P", "os": "-O", "listeners": "-L",
        }
        cmd = ["enum4linux-ng", flag_map.get(options, "-A")]
        if args.get("domain"):
            cmd += ["-w", args["domain"]]
        if args.get("username"):
            cmd += ["-u", args["username"]]
        if args.get("password"):
            cmd += ["-p", args["password"]]
        output_prefix = ""
        if args.get("json_output", True):
            output_prefix = f"/tmp/enum4linux_ng_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            cmd += ["-oJ", output_prefix]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")
        cmd.append(target)

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("enum4linux_ng"))
        if output_prefix:
            json_path = Path(f"{output_prefix}.json")
            if json_path.is_file():
                try:
                    return self._ok(json_path.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    pass
        return self._ok(stdout if stdout else stderr)
