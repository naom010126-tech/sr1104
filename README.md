# 中古マンション管理DD & リノベ制限チェック PoC

一次資料（重調・工事履歴・規約・細則・長修）だけを根拠に、管理DDとリノベ制限の2枚レポを生成するPoCです。

## リポジトリ構成
```
.
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services
│   │       ├── metrics_extraction.py
│   │       ├── pdf_extraction.py
│   │       ├── pdf_report.py
│   │       └── report_generation.py
│   └── tests
└── frontend
    ├── app
    ├── components
    └── lib
```

## 必要環境
- Python 3.11+
- Node.js 18+

## 環境変数
`.env.example` をコピーして `.env` を作成してください。

- `OPENAI_API_KEY`: OpenAI APIキー
- `OPENAI_MODEL`: モデル名（例: gpt-4o-mini）
- `DATABASE_URL`: SQLite接続文字列（例: `sqlite:///./data/app.db`）
- `STORAGE_PATH`: PDF保存先（例: `./storage`）
- `NEXT_PUBLIC_API_BASE`: フロントから参照するAPIベースURL

## 起動手順

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## サンプル実行手順
1. フロントで案件作成
2. 資料を種別ごとにアップロード
3. 「評価して（解析）」ボタン
4. 「2枚レポ生成」ボタン
5. PDFダウンロード

## API
- POST `/cases`
- POST `/cases/{case_id}/documents`
- POST `/cases/{case_id}/analyze`
- POST `/cases/{case_id}/generate-report`
- GET `/cases/{case_id}`
- GET `/cases/{case_id}/report.pdf`
