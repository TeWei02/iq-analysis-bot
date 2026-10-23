**Language:** [![English](https://img.shields.io/badge/English-English-blue?style=flat-square)](README.en.md) [![中文](https://img.shields.io/badge/%E4%B8%AD%E6%96%87-%E4%B8%AD%E6%96%87%E7%89%88-blue?style=flat-square)](README.md)

# IQ Analysis Bot

[![Live](https://img.shields.io/badge/Live-tewei02.github.io%2Fiq--analysis--bot-6ea8fe?logo=github)](https://tewei02.github.io/iq-analysis-bot/)
[![Web](https://img.shields.io/badge/Web-HTML%2FCSS%2FJS-%23E34F26?logo=html5)](https://tewei02.github.io/iq-analysis-bot/)
[![PWA](https://img.shields.io/badge/PWA-installable-5A0FC8)](https://web.dev/progressive-web-apps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive intelligence test web page with **48 questions** that analyzes results instantly after answering. Pure front-end implementation — no backend required.

**Use it online:** <https://tewei02.github.io/iq-analysis-bot/>

## Features

| Feature | Description |
|---------|-------------|
| 48-question interactive test | Layered random question bank covering multiple question types |
| Weighted scoring | Weighted estimate based on difficulty and answering speed |
| Instant analysis | Produces a score and ability-dimension analysis after answering |
| Dark / light theme | One-click toggle, follows the `data-theme` token |
| Responsive design | Works smoothly on mobile, tablet, and desktop |
| Offline-capable | Service Worker caches the app shell; usable offline after install |

## Install as an App (PWA)

Supports Progressive Web App:

- **Android / Chrome**: Open the page → Menu → "Add to Home screen"
- **iOS / Safari**: Open the page → Share → "Add to Home Screen"
- **Desktop Chrome / Edge**: Install icon at the right of the address bar

After installing, it opens in fullscreen and keeps working offline.

## Tech

- HTML5 / CSS3 / Vanilla JavaScript (zero dependencies)
- `manifest.json` + `sw.js`: offline-first PWA shell caching
- GitHub Pages static hosting (root of the `main` branch)

## Project Structure

```
iq-analysis-bot/
├── index.html        # Main test program (layout / styles / logic in one file)
├── manifest.json     # PWA manifest
├── sw.js             # Service Worker (offline cache)
├── icons/            # 192 / 512 / apple-touch / favicon (PNG + SVG)
├── LICENSE
└── README.md
```

## License

MIT
