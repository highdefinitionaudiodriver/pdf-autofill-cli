# 医療費控除明細書テンプレート

確定申告の **医療費控除明細書（国税庁配布）** に、自動入力するためのマッピング設定一式です。

> ⚠️ **PDF 本体は同梱していません**（国税庁の著作物のため）。下記の手順で公式 PDF を取得してください。

---

## 公式 PDF の取得方法

1. 国税庁の「医療費控除の明細書」ダウンロードページにアクセス
   - https://www.nta.go.jp/taxes/shiraberu/shinkoku/yoshiki02/r2bunsho.htm
   - もしくは最新年度の「確定申告関係書類」を検索
2. **「医療費控除の明細書【内訳書】」** の PDF をダウンロード
3. 本ディレクトリ内に `iryouhi_meisai.pdf` として配置

> 国税庁の様式は年次でレイアウトが微調整されることがあります。本ディレクトリの
> `mapping_config.iryouhi.json` は **令和 6 年分の様式を基準** にしています。
> 最新年度を使用する場合は座標値の微調整が必要な場合があります。

---

## ファイル構成

```
templates/iryouhi_meisai/
├── README.md                          このファイル
├── mapping_config.iryouhi.json        座標マッピング定義
├── user_profile.iryouhi.json          ユーザー情報の入力例
└── iryouhi_meisai.pdf                 ← 国税庁からダウンロードして配置
```

---

## 使い方

### 1. プロフィールを編集

`user_profile.iryouhi.json` を自分の情報で書き換えます：

```json
{
  "full_name": "山田 太郎",
  "address": "東京都千代田区...",
  "year": "令和 6",
  "medical_total": "284,500",
  "self_paid_total": "184,500",
  "_医療費の内訳": [
    {
      "person_name": "山田 太郎",
      "facility": "○○薬局",
      "medical_type": "医薬品購入",
      "paid_amount": "12,800",
      "reimbursed_amount": "0"
    }
  ]
}
```

### 2. 実行

```bash
python main.py \
  --template templates/iryouhi_meisai/iryouhi_meisai.pdf \
  --profile templates/iryouhi_meisai/user_profile.iryouhi.json \
  --mapping templates/iryouhi_meisai/mapping_config.iryouhi.json \
  --output output/iryouhi_filled.pdf
```

### 3. PDF を確認

`output/iryouhi_filled.pdf` を開いて、各欄が想定通り埋まっているか確認します。
ずれている場合は `mapping_config.iryouhi.json` の `x` / `y` 値を ±5〜10 ポイント単位で調整してください。

---

## 確定申告セット（selfmed-tax-tool / receipt-ocr-tool との連携）

このテンプレートは確定申告セットの **最終ステップ**に位置します：

```
[1] receipt-ocr-tool       レシート画像 → CSV
       ↓
[2] selfmed-tax-tool       購入履歴 CSV → 対象医薬品の Excel
       ↓
[3] pdf-autofill-cli       明細書 PDF 自動入力 (このテンプレート)
       ↓
   税務署提出用 PDF 完成
```

3 ツールの連携ガイドは将来統合ランチャー化を予定しています。

---

## 注意事項

- **座標は令和 6 年様式基準** です。最新様式では微調整が必要な場合があります
- **医療費の内訳行は最大 5 行**まで対応（明細書 1 枚に収まる範囲）
- 6 行目以降は追加用紙が必要 — 現状では手動で対応してください
- 計算結果（控除額）は **このツールでは自動計算しません**（手動入力 or 国税庁の e-Tax 経由を推奨）

## 商用利用

- 個人利用は無料（MIT）
- 税理士事務所向けの一括処理対応・追加様式対応は応相談
- 連絡先: highdefinitionaudiodriver@gmail.com
