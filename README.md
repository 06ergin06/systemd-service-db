# systemd Service DB

**English** | [Turkish](README.tr.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![JSON Schema: Draft 2020-12](https://img.shields.io/badge/JSON%20Schema-Draft%202020--12-green)](schemas/)

A central JSON database of 147 systemd services with Turkish/English descriptions, recommendations, and optimization profiles. Built for [Pardus Boot Analyzer](https://github.com/06ergin06/pardus-boot-analyzer), [Linux Boot Analyzer](https://github.com/06ergin06/linux_boot_analyzer_tui), and other Linux tools.

## Quick Fetch

```bash
curl -fsSL https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json -o services.json
```

```python
import json
from urllib.request import urlopen

url = "https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json"
with urlopen(url) as response:
    services = json.load(response)

print(services["cups.service"]["description_en"])
```

## Data Structure

```json
{
  "cups.service": {
    "name": "cups.service",
    "description_tr": "CUPS yazıcı sistemi. Yazıcı tanımlama, yazdırma ve kuyruk işlemlerini yönetir.",
    "description_en": "Provides the CUPS print spooler and printer management service.",
    "suggestion_tr": "Sisteminizde bağlı veya tanımlı bir yazıcı kullanmıyorsanız açılışta gereksiz kaynak tüketmemesi için kapatılması önerilir.",
    "suggestion_en": "Disable it on machines without printers or print clients.",
    "category": "printing",
    "safe_to_disable": true,
    "critical": false,
    "required": false
  }
}
```

Categories: `system`, `boot`, `network`, `bluetooth`, `printing`, `telemetry`, `storage`, `security`, `hardware`, `power`, `desktop`, `virtualization`, `database`, `maintenance`, `other`.

## How to Contribute

1. Add the service to `data/services.json`.
2. Run `python3 scripts/validate.py --fix-sort`.
3. Open a PR.

## License

MIT License — [LICENSE](LICENSE)
