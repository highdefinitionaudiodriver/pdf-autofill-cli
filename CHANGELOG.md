# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-04

### Added
- 入力処理 `main.fill_pdf` の統合テスト `tests/test_fill_pdf.py`（9ケース）。実際に PyMuPDF でテンプレート生成→流し込み→出力 PDF のテキスト抽出で検証。座標書き込み、プロフィールキー欠落/ページ範囲外/未知メソッドのスキップ、フォームフィールド書き込み（存在/不在）、`load_json` のエラー終了（ファイル無し/不正 JSON）をカバー
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
