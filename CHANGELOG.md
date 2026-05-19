# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- README に「これは何？（30秒で）」「想定ユースケース・価格帯」セクションを追加
- SECURITY.md を追加（脆弱性報告フロー）
- 商用利用・カスタマイズ依頼の連絡先を README 末尾に明記
- **templates/iryouhi_meisai/** — 医療費控除明細書（国税庁様式）テンプレート枠
  - `mapping_config.iryouhi.json`: 令和6年様式基準の座標マッピング（5行分の医療費内訳 + 合計欄）
  - `user_profile.iryouhi.json`: 入力例（家族3名分の医療費サンプル）
  - `README.md`: 公式 PDF の取得手順・キャリブレーション方法・確定申告セット連携図
  - 著作物のため PDF 本体は同梱せず、国税庁からのダウンロード手順を記載

## [0.1.0]

### Added
- 初版リリース
