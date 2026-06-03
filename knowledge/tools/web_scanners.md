# Web Application Scanners

> Covers: owasp_zap, burpsuite, wpscan, joomscan, droopescan, drupwn, feroxbuster, dirsearch, subfinder, naabu, ProjectDiscovery httpx, katana

## Local Resource Packs

- SecLists is installed at `/usr/share/seclists`.
- Web content lists: `/usr/share/seclists/Discovery/Web-Content/`
- Usernames: `/usr/share/seclists/Usernames/`
- Passwords: `/usr/share/seclists/Passwords/`
- Fuzz payloads: `/usr/share/seclists/Fuzzing/`
- Nuclei community templates are pinned at `/usr/share/nuclei-templates`.

Use these paths directly in `gobuster_dir`, `ffuf_fuzz`, `wfuzz_scan`, `feroxbuster_scan`, `dirsearch_scan`, and `nuclei_scan`.

---

## Fast Discovery Stack

### feroxbuster / dirsearch — Recursive Content Discovery

Use after a web service is confirmed. Prefer SecLists web content lists for breadth.

```bash
feroxbuster --url http://<target> --wordlist /usr/share/seclists/Discovery/Web-Content/common.txt
dirsearch -u http://<target> -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

### subfinder → naabu → pd-httpx → katana

Use for domain-owned asset discovery:

```bash
subfinder -d <domain> -silent
naabu -host <host> -p 80,443,8080,8443 -silent
pd-httpx -u <url> -title -tech-detect -status-code
katana -u <url> -d 2 -jc -silent
```

`pd-httpx` is ProjectDiscovery httpx. It is intentionally named this way in the container so it does not conflict with Kali's `/usr/bin/httpx`.

## OWASP ZAP — Web App Security Scanner

### When to Use
| Signal | Action |
|---|---|
| Need automated web vuln scan | Full DAST scan |
| Need proxy for manual testing | Intercept mode |
| Need API scanning | OpenAPI/GraphQL support |
| Free alternative to Burp | ZAP is open source |

### Common Invocations
```bash
# Quick scan
zap-cli quick-scan http://<target>

# Active scan
zap-cli active-scan http://<target>

# Spider (crawl)
zap-cli spider http://<target>

# Open GUI
zap-cli open-url http://<target>

# Generate report
zap-cli report -o report.html -f html
```

---

## Burp Suite — Web Security Testing Platform

### When to Use
| Signal | Action |
|---|---|
| Manual web testing | Intercept proxy |
| Need request replay | Repeater module |
| Need fuzzing | Intruder module |
| Complex web apps | Full-featured testing |

### Key Modules
| Module | Purpose |
|---|---|
| Proxy | Intercept/modify requests |
| Repeater | Re-send modified requests |
| Intruder | Automated parameter fuzzing |
| Scanner | Automated vuln detection (Pro) |
| Decoder | Encode/decode payloads |

---

## wpscan — WordPress Scanner

### When to Use
| Signal | Action |
|---|---|
| WordPress detected (whatweb) | Run immediately |
| Need plugin/theme enum | wpscan enumerates all |
| Need user enumeration | wpscan finds WP users |
| Need vuln check | WPVulnDB integration |

### Common Invocations
```bash
# Full enumeration
wpscan --url http://<target> -e ap,at,u

# Aggressive plugin detection
wpscan --url http://<target> -e ap --plugins-detection aggressive

# Password brute force
wpscan --url http://<target> -U <user> -P <wordlist>

# With API token (more vuln data)
wpscan --url http://<target> --api-token <token> -e vp,vt

# Enumerate users only
wpscan --url http://<target> -e u
```

### Enumeration Flags
| Flag | Enumerates |
|---|---|
| `ap` | All plugins |
| `at` | All themes |
| `u` | Users |
| `vp` | Vulnerable plugins |
| `vt` | Vulnerable themes |
| `cb` | Config backups |
| `dbe` | DB exports |

---

## joomscan — Joomla Scanner

### When to Use
| Signal | Action |
|---|---|
| Joomla detected (whatweb) | Run immediately |

### Common Invocations
```bash
# Full scan
joomscan -u http://<target>

# With user agent
joomscan -u http://<target> -a "Mozilla/5.0"
```

### Key Findings
- Joomla version → searchsploit
- Installed components → component-specific vulns
- Config file leaks → database credentials
- Admin panel location → cred testing

---

## droopescan — Multi-CMS Scanner

### When to Use
| Signal | Action |
|---|---|
| Drupal detected | Primary Drupal scanner |
| SilverStripe detected | Also supports it |
| Moodle detected | Also supports it |

### Common Invocations
```bash
# Drupal scan
droopescan scan drupal -u http://<target>

# Auto-detect CMS
droopescan scan -u http://<target>

# Enumerate plugins
droopescan scan drupal -u http://<target> -e p
```

---

## CMS Scanner Decision Tree

```
CMS DETECTED:
  ├─ WordPress    → wpscan (best WP scanner)
  ├─ Joomla       → joomscan
  ├─ Drupal       → droopescan
  ├─ SilverStripe → droopescan
  ├─ Unknown CMS  → droopescan (auto-detect)
  └─ No CMS       → gobuster + nikto + manual

AFTER CMS SCAN:
  ├─ Version found?      → searchsploit
  ├─ Vuln plugins?       → exploit known vulns
  ├─ Users enumerated?   → brute force login
  ├─ Config leaks?       → extract credentials
  └─ Admin panel found?  → default creds → SQLi → brute
```
