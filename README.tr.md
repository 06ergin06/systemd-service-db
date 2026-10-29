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
data/profiles.json       # Office, Developer, Minimum
schemas/                 # JSON Schema Draft 2020-12
scripts/validate.py      # sözdizimi, şema, referans ve sıralama
scripts/export_legacy.py # mevcut uygulamalar için uyumluluk adaptörü
.github/workflows/       # validate.yml, sync.yml
```

## Veri

Kanonik veri yalnızca İngilizce tanımlayıcılar kullanır. Çeviri metinleri
değer olarak saklanır; tüm nesne anahtarları, alan adları, profil kimlikleri ve
enum değerleri İngilizcedir.

`data/services.json` içindeki her kayıt şu alanları içerir:

- `name`
- `description_tr`, `description_en`
- `suggestion_tr`, `suggestion_en`
- `category`, `safe_to_disable`, `critical`, `required`

Kanonik sınıflandırma üç boolean ile ifade edilir:

| Sınıf | `safe_to_disable` | `critical` | `required` |
|---|---:|---:|---:|
| İsteğe bağlı | `true` | `false` | `false` |
| Kritik | `false` | `true` | `false` |
| Zorunlu | `false` | `false` | `true` |

Kategoriler: `system`, `boot`, `network`, `bluetooth`, `printing`, `telemetry`,
`storage`, `security`, `hardware`, `power`, `desktop`, `virtualization`,
`database`, `maintenance`, `other`.

`profiles.json`, `office`, `developer` ve `minimum` profillerini içerir.
Profil, etiket veya güvenle kapatılabilir listesinde geçen her servis
`services.json` içinde bulunmak zorundadır. Tam tanımlar için
[`schemas/`](schemas/) klasörüne bakın.

İngilizce servis açıklamaları systemd birim davranışına ve resmi systemd
belgelerine dayanan özgün teknik özetlerdir. Üçüncü taraf bir uygulamadan
kopyalanmamıştır.

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

JSON sözdizimi, şemalar, tekrarlar, referanslar, bayrak tutarlılığı, ASCII nesne
anahtarları ve sıralama kontrol edilir. Yalnızca Python standart kütüphanesi
kullanılır. CI her push ve PR'de aynı kontrolleri çalıştırır.

## Katkı

1. Servisi `data/services.json` içine ekleyin.
2. İki dili de doldurun, kategori seçin ve tam olarak bir sınıflandırma
   boolean'ını `true` yapın.
3. Profil davranışı değişiyorsa `data/profiles.json` dosyasını güncelleyin.
4. `python3 scripts/validate.py --fix-sort` komutunu çalıştırın.
5. Doğrulama çıktısıyla PR açın.

Alan adlarında, profil kimliklerinde ve kategori değerlerinde İngilizce
kullanın. Çeviri açıklama ve öneri değerleri memnuniyetle karşılanır.

## Eşitleme

`main` dalına `data/**` altında değişiklik geldiğinde GitHub Actions, mevcut
uygulamaların beklediği uyumluluk düzenini üretir ve şu repolara gönderir:

| Repo | Dal | Servisler | Profiller |
|---|---|---|---|
| `06ergin06/pardus-boot-analyzer` | `main` | `src/services_data.json` | `src/profiles_data.json` |
| `06ergin06/linux_boot_analyzer_tui` | `master` | `assets/services_data.json` | `assets/profiles_data.json` |

Adaptör `scripts/export_legacy.py` içinde izole edilmiştir; bu repodaki kanonik
veri İngilizce tanımlayıcılarla kalır. İş akışı `SYNC_PAT` secret'ını ve
`systemd-service-db-bot` kimliğini kullanır.

## Lisans

MIT. Bu bağımsız bir projedir. Bu repodaki tüm içerik yalnızca MIT Lisansı
altında sunulur. Ayrıntılar için [`LICENSE`](LICENSE).
