"""口令攻击、哈希破解与字典生成工具实现。"""

import json
import shlex

from ..input_sanitizer import InputSanitizer
from ..parsers import OutputParsers


class CredentialToolsMixin:
    async def _tool_hydra_attack(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)

        service = InputSanitizer.sanitize_generic(args["service"])
        password_list = InputSanitizer.sanitize_path(args["password_list"])
        username = args.get("username", "")
        username_list = args.get("username_list", "")
        port = args.get("port")
        threads = args.get("threads", 4)
        extra = args.get("extra_args", "")

        cmd = ["hydra"]
        if username:
            cmd += ["-l", InputSanitizer.sanitize_generic(username)]
        elif username_list:
            cmd += ["-L", InputSanitizer.sanitize_path(username_list)]
        else:
            cmd += ["-l", "admin"]

        cmd += ["-P", password_list]
        if port:
            cmd += ["-s", str(int(port))]
        cmd += ["-t", str(int(threads))]
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
        cmd += [target, service]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("hydra"))

        raw = stdout if stdout else stderr
        # [MEJORA 3] Parse hydra output
        parsed = OutputParsers.parse_hydra(raw)
        if parsed:
            combined = json.dumps(parsed, indent=2) + "\n\n--- Raw Output ---\n" + raw
            return self._ok(combined)
        return self._ok(raw)

    async def _tool_hashcat_crack(self, args: dict) -> dict:
        hash_file = InputSanitizer.sanitize_path(args["hash_file"])
        hash_type = int(args["hash_type"])
        wordlist = InputSanitizer.sanitize_path(args["wordlist"])
        rules = args.get("rules", "")
        extra = args.get("extra_args", "")

        cmd = ["hashcat", "-m", str(hash_type), hash_file, wordlist, "--force"]
        if rules:
            cmd += ["-r", InputSanitizer.sanitize_path(rules)]
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("hashcat"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_john_crack(self, args: dict) -> dict:
        hash_file = InputSanitizer.sanitize_path(args["hash_file"])
        wordlist = args.get("wordlist", "")
        fmt = args.get("format", "")
        extra = args.get("extra_args", "")

        cmd = ["john"]
        if wordlist:
            cmd.append(f"--wordlist={InputSanitizer.sanitize_path(wordlist)}")
        if fmt:
            cmd.append(f"--format={InputSanitizer.sanitize_generic(fmt)}")
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
        cmd.append(hash_file)

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("john"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_medusa_bruteforce(self, args: dict) -> dict:
        """Ataque de fuerza bruta con Medusa"""
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)

        service = args["service"]
        password_list = InputSanitizer.sanitize_path(args["password_list"])

        cmd = ["medusa", "-h", target, "-U", args.get("user_list", ""), 
               "-P", password_list, "-M", service]

        if args.get("username"):
            cmd += ["-u", args["username"]]
        if args.get("port"):
            cmd += ["-n", str(args["port"])]
        if args.get("threads"):
            cmd += ["-t", str(args["threads"])]
        if args.get("timeout"):
            cmd += ["-T", str(args["timeout"])]
        if args.get("verbose"):
            cmd.append("-v")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("medusa"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_ncrack_bruteforce(self, args: dict) -> dict:
        """Ataque de fuerza bruta con Ncrack"""
        target = args["target"]  # formato: ip:puerto
        service = args["service"]

        cmd = ["ncrack", "-U", args["user_list"], "-P", args["pass_list"], 
               f"{service}://{target}"]

        if args.get("timing"):
            cmd += ["-T", args["timing"]]
        if args.get("connections"):
            cmd += ["-c", str(args["connections"])]
        if args.get("save"):
            cmd += ["-oN", args["save"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("ncrack"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_crunch_gen(self, args: dict) -> dict:
        """Generar wordlists con Crunch"""
        min_len = args["min_length"]
        max_len = args["max_length"]

        cmd = ["crunch", str(min_len), str(max_len)]

        if args.get("charset"):
            cmd += [args["charset"]]
        if args.get("pattern"):
            cmd += ["-t", args["pattern"]]
        if args.get("output_file"):
            cmd += ["-o", args["output_file"]]
        if args.get("start_string"):
            cmd += ["-s", args["start_string"]]
        if args.get("stop_string"):
            cmd += ["-e", args["stop_string"]]
        if args.get("compress"):
            cmd += ["-z", "gzip"]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("crunch"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_cewl_gen(self, args: dict) -> dict:
        """Generar wordlists con CeWL"""
        url = InputSanitizer.sanitize_url(args["target_url"])

        cmd = ["cewl", url]

        if args.get("depth"):
            cmd += ["-d", str(args["depth"])]
        if args.get("min_word_length"):
            cmd += ["-m", str(args["min_word_length"])]
        if args.get("max_word_length"):
            cmd += ["-x", str(args["max_word_length"])]
        if args.get("output_file"):
            cmd += ["-w", args["output_file"]]
        if args.get("with_numbers"):
            cmd += ["--with-numbers"]
        if args.get("email_addresses"):
            cmd += ["-e"]
        if args.get("meta_data"):
            cmd += ["--meta"]
        if args.get("user_agent"):
            cmd += ["-u", args["user_agent"]]
        if args.get("proxy"):
            cmd += ["--proxy", args["proxy"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("cewl"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_kerbrute_enum(self, args: dict) -> dict:
        domain = InputSanitizer.sanitize_target(args["domain"])
        user_list = InputSanitizer.sanitize_path(args["user_list"])
        mode = args.get("mode", "userenum")
        threads = int(args.get("threads", 10))
        extra = args.get("extra_args", "")

        cmd = ["kerbrute", mode, "--domain", domain, "--threads", str(threads)]
        if args.get("dc"):
            cmd += ["--dc", InputSanitizer.sanitize_target(args["dc"])]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")
        cmd.append(user_list)

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("kerbrute"))
        return self._ok(stdout if stdout else stderr)
