<img src="assets/icon.png" width="96" align="right" alt="icon">

# Claude Usage Widget

A tiny always-on-top desktop widget that shows your **real** Claude usage limits — the 5-hour session and the weekly limit — exactly as they appear on claude.ai › Settings › Usage. For **Windows and macOS** (Linux from source).

![screenshot](docs/screenshot_en.png)

[Türkçe açıklama aşağıda ↓](#türkçe)

## Install

You need [Claude Code](https://claude.com/claude-code), logged in with a Claude subscription (Pro / Max). Open it once, and the widget can use its login. Nothing else is needed.

Download from the **[latest release](https://github.com/pholsen/claude-usage-widget/releases/latest)**:

- **Windows:** `ClaudeUsage-Setup-….exe`. Run it and click through. It adds a Claude Usage folder to the Start menu, and can add a desktop shortcut and start with Windows.
- **macOS:** `…-macOS-AppleSilicon.dmg` for M1/M2/M3/M4 Macs, `…-macOS-Intel.dmg` for older Macs. Open it and drag **Claude Usage** onto **Applications**.

The app is not code-signed yet, so the first launch shows a warning:

- **Windows** ("Windows protected your PC"): click **More info** › **Run anyway**.
- **macOS** ("Apple could not verify…"): click **Done**, then open System Settings › Privacy & Security, scroll down and click **Open Anyway** next to Claude Usage.
- **macOS Keychain:** the first refresh asks whether the app may read `Claude Code-credentials`. Choose **Always Allow**, otherwise it asks again on every refresh.

**Start automatically on macOS:** System Settings › General › Login Items › add Claude Usage.

## Uninstall

- **Windows:** Start menu › Claude Usage › **Uninstall Claude Usage**, or Settings › Apps › Installed apps › Claude Usage › Uninstall. This also removes the shortcuts.
- **macOS:** close the widget, then drag **Claude Usage** from Applications to the Trash. If you added it to Login Items, remove it there too.

The widget stores no settings or data of its own.

## Use

| Action | Windows | macOS |
|---|---|---|
| Move | drag with left click | drag |
| Refresh now | double click | double click |
| Close | right click | right click or ctrl + click |

A red dot in the top-right corner means the last refresh failed and the numbers shown are stale.

The language (English / Turkish) follows your system. To set it yourself, use `CLAUDE_WIDGET_LANG=en` or `CLAUDE_WIDGET_LANG=tr`.

## How it works

The widget asks the same endpoint that Claude Code's `/usage` command uses, signed in with the login Claude Code has already saved on your computer:

- **Windows / Linux:** `~/.claude/.credentials.json`
- **macOS:** the Keychain item `Claude Code-credentials`

It shows no estimates and needs no calibration. It refreshes every 60 seconds. Your token is sent only to `api.anthropic.com`.

## Project layout

```
src/         the widget (a single Python file)
assets/      icons
packaging/   PyInstaller spec, Windows installer script, icon generator
docs/        screenshots
```

**Run from source:** Python 3.9+ with Tkinter, then `python3 src/claude_usage_widget.pyw` (on Windows you can double-click the file). On macOS use the python.org installer or `brew install python-tk`; Apple's `/usr/bin/python3` has an outdated Tk. On Linux: `sudo apt install python3-tk`.

**Build the installers:** `.github/workflows/release.yml` builds them on GitHub with PyInstaller and Inno Setup. Push a tag such as `v1.0.2` to publish a release. To regenerate the icons, run `python packaging/make_icon.py`.

## Notes

- The usage endpoint is undocumented and used by Claude Code internally, so it may change without notice.
- If you run several copies, the API may answer `429`. The widget keeps showing the last value with a red dot and tries again later.
- This is an unofficial community tool and is not affiliated with Anthropic.

---

## Türkçe

claude.ai › Ayarlar › Kullanım sayfasındaki **gerçek** oturum (5 saatlik) ve haftalık limit yüzdelerini gösteren, her zaman üstte duran küçük bir masaüstü widget'ı. **Windows ve macOS** için (Linux'ta kaynak koddan).

![ekran görüntüsü](docs/screenshot_tr.png)

### Kurulum

Claude aboneliğiyle (Pro / Max) giriş yapılmış [Claude Code](https://claude.com/claude-code) yeterli; bir kez açman yeter, başka bir şey gerekmez. **[Son sürümden](https://github.com/pholsen/claude-usage-widget/releases/latest)** indir:

- **Windows:** `ClaudeUsage-Setup-….exe` dosyasını çalıştır ve İleri ile ilerle. Başlat menüsüne Claude Usage klasörü ekler; istersen masaüstü kısayolu ekler ve Windows açılışında başlatır.
- **macOS:** M1/M2/M3/M4 Mac'ler için `…-macOS-AppleSilicon.dmg`, eski Mac'ler için `…-macOS-Intel.dmg`. Aç ve **Claude Usage**'ı **Applications** (Uygulamalar) klasörüne sürükle.

Uygulama henüz imzalı olmadığı için ilk açılışta uyarı çıkar:

- **Windows** ("Windows bilgisayarınızı korudu"): **Ek bilgi** › **Yine de çalıştır**.
- **macOS** ("Apple doğrulayamadı…"): **Bitti**'ye bas, sonra Sistem Ayarları › Gizlilik ve Güvenlik'te aşağı kaydırıp Claude Usage'ın yanındaki **Yine de Aç**'a tıkla.
- **macOS Anahtar Zinciri:** İlk yenilemede `Claude Code-credentials` iznini sorar; **Her Zaman İzin Ver**'i seç.

**macOS'ta açılışta başlatmak için:** Sistem Ayarları › Genel › Giriş Öğeleri › Claude Usage'ı ekle.

### Kaldırma

- **Windows:** Başlat menüsü › Claude Usage › **Claude Usage Kaldır**, ya da Ayarlar › Uygulamalar › Yüklü uygulamalar › Claude Usage › Kaldır. Kısayollar da silinir.
- **macOS:** Widget'ı kapat, sonra **Claude Usage**'ı Uygulamalar klasöründen Çöp Sepeti'ne sürükle. Giriş Öğeleri'ne eklediysen oradan da kaldır.

Widget kendine ait bir ayar ya da veri saklamaz.

### Kullanım

- Taşımak için sol tıkla sürükle.
- Hemen yenilemek için çift tıkla.
- Kapatmak için sağ tıkla (Mac'te ctrl + tık da olur).

Sağ üstteki kırmızı nokta, son yenilemenin başarısız olduğunu ve gösterilen değerin eski olduğunu belirtir. Dil sisteme göre seçilir; kendin seçmek için `CLAUDE_WIDGET_LANG=tr` ya da `CLAUDE_WIDGET_LANG=en` kullan.

**Nasıl çalışır:** Claude Code'un `/usage` komutunun kullandığı uç noktayı, Claude Code'un bilgisayarına kaydettiği girişle sorgular (Windows/Linux: `~/.claude/.credentials.json`, macOS: Anahtar Zinciri'ndeki `Claude Code-credentials` kaydı). Tahmin yapmaz, 60 saniyede bir yenilenir. Anahtarın yalnızca `api.anthropic.com`'a gönderilir.

Resmi olmayan bir topluluk aracıdır, Anthropic ile bağlantısı yoktur. Kullandığı uç nokta belgelenmemiştir ve haber verilmeden değişebilir.

## License

MIT
