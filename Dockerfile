# ============================================================================
# Red Team MCP Server — Kali-based Docker Image
# ============================================================================
# Provides all penetration testing tools required by TOOL_BINARY_MAP plus
# the Python MCP server and tactical knowledge base.
#
# Usage:
#   docker build -t kail-mcp .
#   docker compose up
# ============================================================================

FROM kalilinux/kali-rolling:latest AS tools-base

LABEL maintainer="kail-mcp"
LABEL description="MCP server with Kali Linux penetration testing tools"
LABEL version="2.1.0"

# ── Avoid interactive prompts during install ────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# ── Seed machine-id for packages that expect a booted userspace ─────────────
# Kali rolling now pulls in systemd through some tool dependencies. During
# image build, its postinst expects /etc/machine-id to exist.
RUN mkdir -p /var/lib/dbus \
    && printf '00000000000000000000000000000000\n' > /etc/machine-id \
    && ln -sf /etc/machine-id /var/lib/dbus/machine-id

# ── Pre-create dbus service account expected by maintainer scripts ─────────
RUN groupadd --system messagebus \
    && useradd --system --gid messagebus --home-dir /run/dbus --no-create-home \
        --shell /usr/sbin/nologin messagebus \
    && mkdir -p /run/dbus

# ── Pre-create ssh sandbox group expected by openssh maintainer scripts ────
RUN groupadd --system _ssh

# ── Container-only shims for systemd postinst helpers ───────────────────────
# Some Kali tool dependencies pull in systemd. Its maintainer scripts assume a
# fuller userspace than Docker build provides, so these helpers need to no-op
# during image construction.
RUN for cmd in systemd-machine-id-setup systemd-sysusers systemd-tmpfiles systemctl; do \
        dpkg-divert --local --rename --add "/usr/bin/${cmd}"; \
        printf '#!/bin/sh\nexit 0\n' > "/usr/bin/${cmd}"; \
        chmod +x "/usr/bin/${cmd}"; \
    done

# ── Force official Kali mirror — CDN mirrors (mirror.es.cdn-perfprod.com etc.)
#    have intermittent SSL failures; http.kali.org is authoritative and stable.
RUN echo "deb http://kali.download/kali kali-rolling main non-free contrib" > /etc/apt/sources.list \
    && echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80retries

# ── 1. System update + core utilities ───────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        git \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ── 2. Kali tools — grouped by category ────────────────────────────────────
#
# Install only the binaries required by the MCP registry. Keeping this list
# aligned with TOOL_BINARY_MAP avoids slow rebuilds and non-MCP GUI/platform
# dependencies.
#
# Category C tools (NOT installable — auto-hidden by check_available_binaries):
#   mimikatz, cobaltstrike, burpsuite, powersploit, empire, shellter,
#   pth-toolkit, xhydra (GUI), pyrit, ewsa, wifiphisher, fluxion,
#   airgeddon, wifi-honey, ghost-phisher, fern-wifi-cracker
#
RUN apt-get update && apt-get install -y --no-install-recommends \
        \
        # ── Recon / passive ─────────────────────────────── \
        whois \
        dnsutils \
        whatweb \
        exploitdb \
        theharvester \
        \
        # ── Active scanning ─────────────────────────────── \
        nmap \
        masscan \
        nikto \
        gobuster \
        feroxbuster \
        dirsearch \
        ffuf \
        dirb \
        wfuzz \
        enum4linux \
        enum4linux-ng \
        nuclei \
        subfinder \
        naabu \
        \
        # ── Exploitation / brute-force ──────────────────── \
        hydra \
        sqlmap \
        hashcat \
        john \
        netcat-traditional \
        \
        # ── SMB / AD enumeration ────────────────────────── \
        smbclient \
        smbmap \
        crackmapexec \
        netexec \
        evil-winrm \
        certipy-ad \
        python3-impacket \
        \
        # ── Extra brute-force ───────────────────────────── \
        medusa \
        ncrack \
        \
        # ── CMS scanners ───────────────────────────────── \
        wpscan \
        joomscan \
        \
        # ── Web app testing ─────────────────────────────── \
        zaproxy \
        \
        # ── Frameworks / C2 ─────────────────────────────── \
        metasploit-framework \
        beef-xss \
        set \
        \
        # ── MITM / network interception ─────────────────── \
        bettercap \
        ettercap-text-only \
        responder \
        tor \
        \
        # ── Wireless ────────────────────────────────────── \
        aircrack-ng \
        wifite \
        \
        # ── Wordlist generators ─────────────────────────── \
        crunch \
        cewl \
        \
        # ── Network capture / analysis ──────────────────── \
        tcpdump \
        \
        # ── Wordlists ──────────────────────────────────── \
        wordlists \
        seclists \
    && rm -rf /var/lib/apt/lists/*

# ── 3. Quality-of-life / shell comfort tools ───────────────────────────────
#
# Standard utilities present in a normal Kali install that
# --no-install-recommends strips out.
#
RUN apt-get update && apt-get install -y --no-install-recommends \
        \
        # ── Editors ─────────────────────────────────────── \
        nano \
        vim-tiny \
        \
        # ── Network utilities ───────────────────────────── \
        iputils-ping \
        net-tools \
        iproute2 \
        dnsutils \
        traceroute \
        telnet \
        socat \
        openssh-client \
        proxychains4 \
        \
        # ── Shell / terminal comfort ─────────────────────── \
        zsh \
        zsh-syntax-highlighting \
        zsh-autosuggestions \
        bash-completion \
        less \
        tree \
        file \
        lsof \
        procps \
        man-db \
        \
        # ── Archive / transfer ───────────────────────────── \
        zip \
        unzip \
        p7zip-full \
        rsync \
        \
        # ── Misc dev tools ───────────────────────────────── \
        jq \
        xxd \
        binutils \
        tmux \
    && rm -rf /var/lib/apt/lists/*

# ── Fixed upstream CLI tools not packaged in Kali repos ───────────────────
#
# ProjectDiscovery httpx is installed as pd-httpx to avoid clobbering the
# existing /usr/bin/httpx command from Kali/Python packages.
#
ARG KATANA_VERSION=1.6.1
ARG KATANA_SHA256=503754f1bd370c3ef287df6998e317baed2dd75bdd13ea64034f09b80ca393f3
ARG KERBRUTE_VERSION=1.0.3
ARG KERBRUTE_SHA256=710a9d2653c8bd3689e451778dab9daec0de4c4c75f900788ccf23ef254b122a
ARG PD_HTTPX_VERSION=1.9.0
ARG PD_HTTPX_SHA256=54c6c91d61d3b82ba79f93633df04bb547f0c954d9d9b0fb8bcedf158f85ff2f
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG ALL_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ARG all_proxy
ARG no_proxy

RUN set -eux; \
    export HTTP_PROXY="${HTTP_PROXY:-${http_proxy:-}}"; \
    export HTTPS_PROXY="${HTTPS_PROXY:-${https_proxy:-}}"; \
    export ALL_PROXY="${ALL_PROXY:-${all_proxy:-}}"; \
    export NO_PROXY="${NO_PROXY:-${no_proxy:-}}"; \
    export http_proxy="${http_proxy:-${HTTP_PROXY:-}}"; \
    export https_proxy="${https_proxy:-${HTTPS_PROXY:-}}"; \
    export all_proxy="${all_proxy:-${ALL_PROXY:-}}"; \
    export no_proxy="${no_proxy:-${NO_PROXY:-}}"; \
    tmpdir="$(mktemp -d)"; \
    cd "$tmpdir"; \
    download() { \
        url="$1"; \
        output="$2"; \
        curl --fail --show-error --silent --location \
            --retry 8 --retry-all-errors --retry-connrefused --retry-delay 5 \
            --connect-timeout 30 \
            --output "$output" "$url"; \
    }; \
    download "https://github.com/projectdiscovery/katana/releases/download/v${KATANA_VERSION}/katana_${KATANA_VERSION}_linux_amd64.zip" "katana_${KATANA_VERSION}_linux_amd64.zip"; \
    echo "${KATANA_SHA256}  katana_${KATANA_VERSION}_linux_amd64.zip" | sha256sum -c -; \
    mkdir katana-dist; \
    unzip -oq "katana_${KATANA_VERSION}_linux_amd64.zip" -d katana-dist; \
    install -m 0755 katana-dist/katana /usr/local/bin/katana; \
    download "https://github.com/ropnop/kerbrute/releases/download/v${KERBRUTE_VERSION}/kerbrute_linux_amd64" kerbrute; \
    echo "${KERBRUTE_SHA256}  kerbrute" | sha256sum -c -; \
    install -m 0755 kerbrute /usr/local/bin/kerbrute; \
    download "https://github.com/projectdiscovery/httpx/releases/download/v${PD_HTTPX_VERSION}/httpx_${PD_HTTPX_VERSION}_linux_amd64.zip" "httpx_${PD_HTTPX_VERSION}_linux_amd64.zip"; \
    echo "${PD_HTTPX_SHA256}  httpx_${PD_HTTPX_VERSION}_linux_amd64.zip" | sha256sum -c -; \
    mkdir httpx-dist; \
    unzip -oq "httpx_${PD_HTTPX_VERSION}_linux_amd64.zip" -d httpx-dist; \
    install -m 0755 httpx-dist/httpx /usr/local/bin/pd-httpx; \
    katana -version; \
    kerbrute version; \
    pd-httpx -version; \
    rm -rf "$tmpdir"

# ── Nuclei community templates (resource, not an MCP tool) ────────────────
ARG NUCLEI_TEMPLATES_COMMIT=a07c83b51f52bcfe6708a56170ab9920a17d8db2
RUN set -eux; \
    export HTTP_PROXY="${HTTP_PROXY:-${http_proxy:-}}"; \
    export HTTPS_PROXY="${HTTPS_PROXY:-${https_proxy:-}}"; \
    export ALL_PROXY="${ALL_PROXY:-${all_proxy:-}}"; \
    export NO_PROXY="${NO_PROXY:-${no_proxy:-}}"; \
    export http_proxy="${http_proxy:-${HTTP_PROXY:-}}"; \
    export https_proxy="${https_proxy:-${HTTPS_PROXY:-}}"; \
    export all_proxy="${all_proxy:-${ALL_PROXY:-}}"; \
    export no_proxy="${no_proxy:-${NO_PROXY:-}}"; \
    git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates.git /usr/share/nuclei-templates; \
    cd /usr/share/nuclei-templates; \
    git fetch --depth 1 origin "${NUCLEI_TEMPLATES_COMMIT}"; \
    git checkout "${NUCLEI_TEMPLATES_COMMIT}"; \
    rm -rf .git

# ── Shell history + readline (arrow-up navigation in terminal) ──────────────
RUN echo 'export HISTFILE=/root/.bash_history' >> /root/.bashrc \
    && echo 'export HISTSIZE=5000' >> /root/.bashrc \
    && echo 'export HISTFILESIZE=10000' >> /root/.bashrc \
    && echo 'export HISTCONTROL=ignoredups:erasedups' >> /root/.bashrc \
    && echo 'shopt -s histappend' >> /root/.bashrc \
    && echo 'PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"' >> /root/.bashrc \
    && echo 'source /usr/share/bash-completion/bash_completion 2>/dev/null || true' >> /root/.bashrc

# proxychains4 configs:
#   proxychains <tool>                                    → Burp en Windows (análisis, sin anonimato)
#   proxychains -f /etc/proxychains4-tor.conf <tool>     → Tor dentro del contenedor (anónimo, sin análisis Burp)
#
#   Para análisis Burp + anonimato Tor (mejor opción):
#     1. Activa Tor desde the host UI (expone SOCKS en 127.0.0.1:9050 vía network_mode:host)
#     2. En Burp Suite (Windows): Settings → Network → Connections → SOCKS proxy → 127.0.0.1:9050
#     3. Usa proxychains normalmente → tool → Burp → Tor → internet
RUN sed -i 's/^socks4\s.*/# &/' /etc/proxychains4.conf \
    && echo 'http    host.docker.internal  8080' >> /etc/proxychains4.conf \
    && cp /etc/proxychains4.conf /etc/proxychains4-tor.conf \
    && sed -i 's/^http.*/# &/' /etc/proxychains4-tor.conf \
    && echo 'socks5  127.0.0.1  9050' >> /etc/proxychains4-tor.conf

# inputrc: arrow-up/down search history by prefix already typed (bash fallback)
RUN printf '"\e[A": history-search-backward\n"\e[B": history-search-forward\n"\eOA": history-search-backward\n"\eOB": history-search-forward\nset show-all-if-ambiguous on\nset completion-ignore-case on\n' > /root/.inputrc

# zsh config: syntax highlighting + autosuggestions + history navigation
RUN echo 'source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' >> /root/.zshrc \
    && echo 'source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh' >> /root/.zshrc \
    && echo 'export HISTFILE=/root/.zsh_history' >> /root/.zshrc \
    && echo 'export HISTSIZE=5000' >> /root/.zshrc \
    && echo 'export SAVEHIST=10000' >> /root/.zshrc \
    && echo 'setopt HIST_IGNORE_DUPS HIST_APPEND INC_APPEND_HISTORY SHARE_HISTORY' >> /root/.zshrc \
    && echo 'autoload -Uz compinit && compinit' >> /root/.zshrc \
    && echo 'bindkey "^[[A" history-search-backward' >> /root/.zshrc \
    && echo 'bindkey "^[[B" history-search-forward' >> /root/.zshrc \
    && echo 'bindkey "^[OA" history-search-backward' >> /root/.zshrc \
    && echo 'bindkey "^[OB" history-search-forward' >> /root/.zshrc \
    && echo 'ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=8"' >> /root/.zshrc \
    && chsh -s /bin/zsh root

# ── pip-only tools (not in Kali repos) ───────────────────────────────────
RUN pip3 install --no-cache-dir --break-system-packages \
        bloodhound \
        droopescan \
    && command -v bloodhound-python
# Note: drupwn is no longer available on PyPI

# ── 4. Ensure rockyou.txt is decompressed ───────────────────────────────────
RUN if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then \
        gunzip /usr/share/wordlists/rockyou.txt.gz; \
    fi

# ── Pre-configure Tor transparent proxy ────────────────────────────────────
# Directives required by the host UI's tor_start() transparent proxy feature.
# _ensure_torrc() in terminal.py will detect these are already present (no-op).
RUN printf '\n# the host UI transparent proxy\nTransPort 9040\nDNSPort 5353\nVirtualAddrNetworkIPv4 10.192.0.0/10\nAutomapHostsOnResolve 1\n' >> /etc/tor/torrc

# ── 5. Initialize Metasploit database ──────────────────────────────────────
RUN service postgresql start \
    && msfdb init \
    && service postgresql stop \
    || echo "msfdb init skipped (will retry at runtime)"

# ── 6. Application layer ──────────────────────────────────────────────────
FROM tools-base AS app

# ── 7. Application directory ───────────────────────────────────────────────
WORKDIR /opt/kail-mcp

# ── 8. Python dependencies ─────────────────────────────────────────────────
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# ── 9. Application code + knowledge base ───────────────────────────────────
COPY config.yaml .
COPY mcp_server.py .
COPY knowledge/ knowledge/
COPY scripts/check-tools.py scripts/check-tools.py
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# ── 10. Runtime directories for volumes ────────────────────────────────────
RUN mkdir -p /opt/kail-mcp/reports /opt/kail-mcp/data

# ── 11. Environment variable defaults ──────────────────────────────────────
#    All can be overridden in docker-compose.yml or with `docker run -e`
ENV MCP_CONFIG_PATH=/opt/kail-mcp/config.yaml \
    MCP_LOG_LEVEL=INFO \
    MCP_DATABASE=/opt/kail-mcp/data/scan_results.db \
    MCP_AUDIT_LOG=/opt/kail-mcp/data/audit.log \
    MCP_REPORT_DIR=/opt/kail-mcp/reports

# ── 12. Healthcheck ────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# ── 13. Entrypoint + default command ───────────────────────────────────────
ENTRYPOINT ["docker-entrypoint.sh"]
CMD []
