# IQ 分析 Bot

[![Live](https://img.shields.io/badge/Live-tewei02.github.io%2Fiq--analysis--bot-6ea8fe?logo=github)](https://tewei02.github.io/iq-analysis-bot/)
[![Web](https://img.shields.io/badge/Web-HTML%2FCSS%2FJS-%23E34F26?logo=html5)](https://tewei02.github.io/iq-analysis-bot/)
[![PWA](https://img.shields.io/badge/PWA-installable-5A0FC8)](https://web.dev/progressive-web-apps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

互動式智力測驗網頁，共 **48 題**，作答後即時分析結果。純前端實作，無需後端即可使用。

**線上使用：** <https://tewei02.github.io/iq-analysis-bot/>

## 功能

| 功能 | 說明 |
|------|------|
| 48 題互動測驗 | 分層隨機題庫，涵蓋多類型題目 |
| 加權計分 | 依難度與作答速度加權估算 |
| 即時分析 | 作答後產生分數與能力面向分析 |
| 深色／淺色主題 | 一鍵切換，跟隨 `data-theme` 權杖 |
| 響應式設計 | 手機、平板、桌面皆可流暢使用 |
| 可離線使用 | Service Worker 快取應用外殼，安裝後離線可用 |

## 安裝為 App（PWA）

支援 Progressive Web App：

- **Android / Chrome**：開啟網頁 → 選單 →「加到主畫面」
- **iOS / Safari**：開啟網頁 → 分享 →「加入主畫面」
- **桌面 Chrome / Edge**：網址列右側的安裝圖示

安裝後可全螢幕開啟，並在離線狀態下繼續使用。

## 技術

- HTML5 / CSS3 / Vanilla JavaScript（零依賴）
- `manifest.json` + `sw.js`：離線優先的 PWA 外殼快取
- GitHub Pages 靜態託管（`main` 分支根目錄）

## 專案結構

```
iq-analysis-bot/
├── index.html        # 測驗主程式（版面 / 樣式 / 邏輯單檔）
├── manifest.json     # PWA manifest
├── sw.js             # Service Worker（離線快取）
├── icons/            # 192 / 512 / apple-touch / favicon（PNG + SVG）
├── LICENSE
└── README.md
```

## License

MIT
