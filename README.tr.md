# systemd Service DB

[English](README.md) | **Türkçe**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![JSON Schema: Draft 2020-12](https://img.shields.io/badge/JSON%20Schema-Draft%202020--12-green)](schemas/)

Pardus Boot Analyzer, Linux Boot Analyzer ve diğer Linux araçları için hazırlanmış; 147 systemd servisini, Türkçe/İngilizce açıklama ve önerilerini ve optimizasyon profillerini barındıran merkezi JSON veritabanı.

## Hızlı Kullanım

```bash
curl -fsSL https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json -o services.json
```

```python
import json
from urllib.request import urlopen

url = "https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json"
with urlopen(url) as response:
    services = json.load(response)

print(services["cups.service"]["description_tr"])
```

## Veri Yapısı

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

Kategoriler: `system`, `boot`, `network`, `bluetooth`, `printing`, `telemetry`, `storage`, `security`, `hardware`, `power`, `desktop`, `virtualization`, `database`, `maintenance`, `other`.

## Nasıl Katkı Sağlanır?

1. Servisi `data/services.json` içine ekle.
2. `python3 scripts/validate.py --fix-sort` komutunu çalıştır.
3. PR aç.

## Lisans

MIT License — [LICENSE](LICENSE)
