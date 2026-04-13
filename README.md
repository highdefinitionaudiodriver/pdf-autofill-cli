# PDF Auto-Fill CLI

コマンドラインからPDFにユーザー情報を自動入力するツール。  
あらかじめ定義したプロフィール(JSON)とマッピング設定に従い、PDFテンプレートの指定座標またはフォームフィールドにテキストを描画して新しいPDFとして出力します。

## 特徴

- **座標指定描画** — ページ番号・(x, y)座標を指定してテキストを直接描画
- **フォームフィールド対応** — AcroFormフィールド名を指定して値をセット
- **日本語対応** — Windows環境のMSゴシック/メイリオ/游ゴシックを自動検出
- **PyInstaller対応** — 単一EXEとしてパッケージング可能な設計

## プロジェクト構成

```
pdf-autofill-cli/
├── main.py                     # メインスクリプト
├── requirements.txt
├── config/
│   ├── user_profile.json       # ユーザー個人情報
│   └── mapping_config.json     # 座標/フィールドのマッピング定義
├── templates/                  # テンプレートPDF置き場
└── output/                     # 出力先
```

## セットアップ

```bash
pip install -r requirements.txt
```

## 使い方

### サンプルテンプレートの生成

テスト用のA4サイズPDFテンプレートを生成します。

```bash
python main.py --generate-template
```

`templates/sample_template.pdf` が作成されます。

### PDF自動入力の実行

```bash
python main.py templates/sample_template.pdf
```

#### オプション

| オプション | デフォルト値 | 説明 |
|---|---|---|
| `-p`, `--profile` | `config/user_profile.json` | ユーザープロフィールJSONのパス |
| `-m`, `--mapping` | `config/mapping_config.json` | マッピング定義JSONのパス |
| `-o`, `--output` | `output/filled.pdf` | 出力先PDFのパス |
| `--generate-template` | — | テスト用サンプルPDFを生成 |

```bash
# フルオプション指定の例
python main.py input.pdf -p my_profile.json -m my_mapping.json -o result.pdf
```

## 設定ファイル

### user_profile.json

ユーザーの個人情報を定義します。キー名は自由に追加できます。

```json
{
  "last_name": "山田",
  "first_name": "太郎",
  "full_name": "山田 太郎",
  "postal_code": "100-0001",
  "address_pref": "東京都",
  "address_city": "千代田区千代田",
  "address_detail": "1-1-1 サンプルマンション101",
  "phone": "090-1234-5678",
  "email": "taro.yamada@example.com",
  "birthdate": "1990-01-15"
}
```

### mapping_config.json

「どのプロフィール項目を」「PDFのどこに」書き込むかを定義します。

#### 座標指定 (`coordinate`)

```json
{
  "field_key": "full_name",
  "method": "coordinate",
  "page": 0,
  "x": 150,
  "y": 200,
  "font_size": 12
}
```

| プロパティ | 説明 |
|---|---|
| `field_key` | `user_profile.json` のキー名 |
| `method` | `"coordinate"` |
| `page` | ページ番号 (0始まり) |
| `x`, `y` | 描画座標 (ポイント単位、左上原点) |
| `font_size` | フォントサイズ |

#### フォームフィールド (`form_field`)

```json
{
  "field_key": "full_name",
  "method": "form_field",
  "field_name": "name_field",
  "font_size": 12
}
```

| プロパティ | 説明 |
|---|---|
| `field_key` | `user_profile.json` のキー名 |
| `method` | `"form_field"` |
| `field_name` | PDF内のAcroFormフィールド名 |

## EXE化 (PyInstaller)

```bash
pip install pyinstaller
pyinstaller --onefile --name pdf-autofill main.py
```

`dist/pdf-autofill.exe` が生成されます。  
`config/` フォルダをEXEと同じディレクトリに配置して使用してください。

## 座標の調べ方

テンプレートPDFの書き込み座標を調べるには、以下の方法があります。

1. **Adobe Acrobat** — カーソル位置の座標を画面下部に表示（単位をポイントに設定）
2. **PDF Viewer のルーラー機能** — 各種ビューアのルーラー/グリッド表示
3. **試行調整** — mapping_config.json の座標を少しずつ変えて出力を確認

> PyMuPDFの座標系はページ左上が原点 (0, 0)、右下に向かって値が増加します。単位はポイント (1pt = 1/72 inch) です。A4サイズは 595 x 842 pt です。

## 技術スタック

- Python 3.10+
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) — PDF読み書き・テキスト描画

## ライセンス

MIT
