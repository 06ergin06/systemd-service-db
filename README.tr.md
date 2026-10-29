# systemd Service DB

[English](README.md) | **Türkçe**

[![Validate data](https://github.com/06ergin06/systemd-service-db/actions/workflows/validate.yml/badge.svg)](https://github.com/06ergin06/systemd-service-db/actions/workflows/validate.yml)
[![Sync data](https://github.com/06ergin06/systemd-service-db/actions/workflows/sync.yml/badge.svg)](https://github.com/06ergin06/systemd-service-db/actions/workflows/sync.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![JSON Schema: Draft 2020-12](https://img.shields.io/badge/JSON%20Schema-Draft%202020--12-green)](schemas/)

[`pardus-boot-analyzer`](https://github.com/06ergin06/pardus-boot-analyzer) ve
[`linux_boot_analyzer_tui`](https://github.com/06ergin06/linux_boot_analyzer_tui)
için merkezi, iki dilli ve doğrulanmış systemd servis veritabanı.

**147 servis · 3 profil · JSON Schema · bağımlılıksız doğrulayıcı · otomatik eşitleme**

## Yapı

```text
data/services.json       # birim adıyla anahtarlanmış
data/profiles.json       # Ofis, Yazılımcı, Minimum
schemas/                 # JSON Schema Draft 2020-12
scripts/validate.py      # sözdizimi, şema, referans ve sıralama
.github/workflows/       # validate.yml, sync.yml
```

## Veri

`data/services.json` içindeki her kayıt `name`, `description_tr/en`,
`suggestion_tr/en`, `category`, `safe_to_disable`, `critical`, `required` ve
eski uygulamalar için `desc`, `desc_en`, `suggestion`, `oneri_en`, `tip`
alanlarını içerir. Eski alanlar kanonik alanlarla birebir aynı olmalıdır.

| `tip` | `safe_to_disable` | `critical` | `required` |
|---|---:|---:|---:|
| `suggestion` | `true` | `false` | `false` |
| `kritik` | `false` | `true` | `false` |
| `gerekli` | `false` | `false` | `true` |

Kategoriler: `system`, `boot`, `network`, `bluetooth`, `printing`, `telemetry`,
`storage`, `security`, `hardware`, `power`, `desktop`, `virtualization`,
`database`, `maintenance`, `other`.

`profiles.json`, profil bilgilerini ve `enable`/`disable` kurallarını içerir.
Referans verilen her servis `services.json` içinde bulunmalıdır. Tam tanımlar
için [`schemas/`](schemas/) klasörüne bakın.

## Kullanım

```bash
curl -fsSL \
  https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json \
  -o services.json
```

```python
import json, urllib.request

URL = "https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json"
with urllib.request.urlopen(URL) as response:
    services = json.load(response)

print(services["cups.service"]["description_tr"])
```

Sabitlenmiş Git alt modülü de kullanılabilir. Üretimde commit veya etiket
sabitleyin.

## Doğrulama

```bash
python3 scripts/validate.py
python3 scripts/validate.py --check-sorted
python3 scripts/validate.py --fix-sort
```

JSON sözdizimi, şemalar, tekrarlar, referanslar, bayrak tutarlılığı ve sıralama
kontrol edilir. Yalnızca Python standart kütüphanesi kullanılır. CI her push ve
PR'de çalışır.

## Katkı

1. Servisi `data/services.json` içine ekleyin.
2. İki dili de doldurun, kategori seçin ve eski alanları eşit tutun.
3. Profil davranışı değişiyorsa `data/profiles.json` dosyasını güncelleyin.
4. `python3 scripts/validate.py --fix-sort` komutunu çalıştırın.
5. Doğrulama çıktısıyla PR açın.

## Eşitleme

`main` dalına `data/**` altında değişiklik geldiğinde dosyalar şu repolara
kopyalanır:

| Repo | Dal | Servisler | Profiller |
|---|---|---|---|
| `06ergin06/pardus-boot-analyzer` | `main` | `src/services_data.json` | `src/profiles_data.json` |
| `06ergin06/linux_boot_analyzer_tui` | `master` | `assets/services_data.json` | `assets/profiles_data.json` |

`SYNC_PAT` secret'ı ve `systemd-service-db-bot` kimliği kullanılır.

## Lisans

MIT. Kaynak projeler GPL-3.0 kullanmaktadır; yeniden dağıtımdan önce hukuki
değerlendirme önerilir. Ayrıntılar için [`LICENSE`](LICENSE).
