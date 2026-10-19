<img src="assets/icon.png" width="96" align="right" alt="icon">

# Claude Usage Widget

A tiny always-on-top desktop widget that shows your **real** Claude usage limits — the 5-hour session and the weekly limit — exactly as they appear on claude.ai › Settings › Usage. Works on **Windows, macOS and Linux**. Single Python file, no dependencies.

![screenshot](docs/screenshot_en.png)

[Türkçe açıklama aşağıda ↓](#türkçe)

## How it works

The widget asks the same endpoint that Claude Code's `/usage` command uses, signed in with the login Claude Code has already saved on your computer:

- **Windows / Linux:** `~/.claude/.credentials.json`
- **macOS:** the Keychain item `Claude Code-credentials`

It shows no estimates and needs no calibration. It refreshes every 60 seconds. Your token is sent only to `api.anthropic.com`.

## Requirements

- [Claude Code](https://claude.com/claude-code), logged in with a Claude subscription (Pro / Max). Open it once, and the widget can use its login.
- Python 3.9+ with Tkinter
  - **Windows:** the python.org installer includes Tkinter.
  - **macOS:** use the [python.org installer](https://www.python.org/downloads/macos/) or `brew install python-tk`. Apple's `/usr/bin/python3` comes with an outdated Tk that may draw a blank window.
  - **Linux:** `sudo apt install python3-tk` (or your distro's equivalent).

## Run

**Windows:** double-click `Install (Windows).bat` once. It creates a **Claude Usage** shortcut with the widget icon on your Desktop and in the Start menu, and asks whether to start the widget with Windows. After that, open the widget from the shortcut. (Windows shows every `.pyw` file with the Python icon, so the icon only appears on the shortcut.) You can also just double-click `claude_usage_widget.pyw`; no console window opens.

**macOS:** double-click `Claude Usage.command`. The first time, macOS asks whether `security` may read the `Claude Code-credentials` Keychain item. Choose **Always Allow**, otherwise it asks again on every refresh. If macOS blocks the file because it was downloaded, right-click it › Open, or run:

```sh
chmod +x "Claude Usage.command"
xattr -d com.apple.quarantine "Claude Usage.command"
```

**Linux:** `python3 claude_usage_widget.pyw &`

### Start automatically

- **Windows:** run `Install (Windows).bat` and answer **Y**.
- **macOS:** System Settings › General › Login Items › add `Claude Usage.command`.

## Controls

| Action | Windows / Linux | macOS |
|---|---|---|
| Move | drag with left click | drag |
| Refresh now | double click | double click |
| Close | right click | right click or ctrl + click |

A red dot in the top-right corner means the last refresh failed and the numbers shown are stale.

The language (English / Turkish) follows your system. To set it yourself, use `CLAUDE_WIDGET_LANG=en` or `CLAUDE_WIDGET_LANG=tr`.

## Notes

- The usage endpoint is undocumented and used by Claude Code internally, so it may change without notice.
- If you poll very often (or run several copies), the API may answer `429`. The widget keeps showing the last value with a red dot and tries again later.
- This is an unofficial community tool and is not affiliated with Anthropic.

---

## Türkçe

claude.ai › Ayarlar › Kullanım sayfasındaki **gerçek** oturum (5 saatlik) ve haftalık limit yüzdelerini gösteren, her zaman üstte duran küçük bir masaüstü widget'ı. **Windows, macOS ve Linux**'ta çalışır. Tek Python dosyası, ek paket gerekmez.

![ekran görüntüsü](docs/screenshot_tr.png)

**Nasıl çalışır:** Claude Code'un `/usage` komutunun kullandığı uç noktayı, Claude Code'un bilgisayarına kaydettiği girişle sorgular (Windows/Linux: `~/.claude/.credentials.json`, macOS: Anahtar Zinciri'ndeki `Claude Code-credentials` kaydı). Tahmin yapmaz, 60 saniyede bir yenilenir. Anahtarın yalnızca `api.anthropic.com`'a gönderilir.

**Gereksinimler:** Claude aboneliğiyle (Pro / Max) giriş yapılmış Claude Code ve Tkinter içeren Python 3.9+. macOS'ta python.org kurulumunu ya da `brew install python-tk` kullan. Apple'ın `/usr/bin/python3`'ündeki eski Tk boş pencere çizebilir.

**Çalıştırma:**
- **Windows:** `Install (Windows).bat` dosyasına bir kez çift tıkla. Masaüstüne ve Başlat menüsüne ikonlu **Claude Usage** kısayolu ekler, Windows açılışında başlasın mı diye sorar. Sonra widget'ı bu kısayoldan aç. (Windows her `.pyw` dosyasını Python ikonuyla gösterir; ikon yalnızca kısayolda görünür.)
- **macOS:** `Claude Usage.command` dosyasına çift tıkla. İlk açılışta Anahtar Zinciri izni sorulur; **Her Zaman İzin Ver**'i seç, yoksa her yenilemede tekrar sorar. Dosya engellenirse sağ tık › Aç ile aç.
- **Linux:** `python3 claude_usage_widget.pyw &`

**Kullanım:**
- Taşımak için sol tıkla sürükle.
- Hemen yenilemek için çift tıkla.
- Kapatmak için sağ tıkla (Mac'te ctrl + tık da olur).

Sağ üstteki kırmızı nokta, son yenilemenin başarısız olduğunu ve gösterilen değerin eski olduğunu belirtir.

Dil sisteme göre seçilir. Kendin seçmek için `CLAUDE_WIDGET_LANG=tr` ya da `CLAUDE_WIDGET_LANG=en` kullan.

Resmi olmayan bir topluluk aracıdır, Anthropic ile bağlantısı yoktur. Kullandığı uç nokta belgelenmemiştir ve haber verilmeden değişebilir.

## License

MIT
