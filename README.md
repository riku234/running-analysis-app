# ランニング動画解析アプリ

MediaPipeを使用してランニング動画から歩数と体幹の前傾角度を測定するWebアプリケーションです。

## 機能

- **動画アップロード**: MP4、AVI、MOV等の動画ファイルをアップロード
- **歩数計測**: 腰の上下動から歩数を自動推定
- **前傾角度測定**: 肩と腰を結ぶ線の垂直線に対する平均角度を計算
- **結果表示**: 計測結果をわかりやすく表示

## 技術スタック

### バックエンド
- Python 3.8+
- Django 4.2.7
- Django REST Framework
- MediaPipe (姿勢推定)
- OpenCV (動画処理)
- SciPy (信号処理)

### フロントエンド
- React 18.2
- JavaScript/JSX
- Axios (HTTP通信)

## プロジェクト構造

```
歩行動画解析/
├── analysis/                   # Djangoアプリ
│   ├── __init__.py
│   ├── apps.py
│   ├── services.py            # 動画解析のコア機能
│   ├── views.py               # REST API エンドポイント
│   └── urls.py                # URL設定
├── running_analysis_project/   # Djangoプロジェクト設定
│   ├── __init__.py
│   ├── settings.py            # Django設定
│   ├── urls.py                # メインURL設定
│   ├── wsgi.py
│   └── asgi.py
├── frontend/                   # Reactフロントエンド
│   ├── src/
│   │   └── components/
│   │       └── ResultDisplay.js  # 結果表示コンポーネント
│   └── package.json
├── manage.py                   # Django管理スクリプト
├── requirements.txt            # Python依存関係
└── README.md
```

## セットアップ手順

### 1. バックエンド (Django)

#### 💻 **ローカル開発環境（MediaPipe対応）**

```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 開発用依存関係のインストール（MediaPipe含む）
pip install --upgrade pip
pip install -r requirements-dev.txt

# データベースの初期化
python manage.py migrate

# 開発サーバーの起動
python manage.py runserver
```

#### ☁️ **本番デプロイ用（MediaPipe除外）**

```bash
# 本番デプロイ用依存関係のインストール
pip install -r requirements.txt
```

**💡 環境の使い分け**:
- **`requirements-dev.txt`**: ローカル開発用（MediaPipe高精度解析）
- **`requirements.txt`**: 本番デプロイ用（OpenCVベース解析）

### 2. フロントエンド (React)

```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm start
```

## API仕様

### 動画解析エンドポイント

**POST** `/api/analyze/`

- **Content-Type**: `multipart/form-data`
- **パラメータ**: 
  - `video`: 動画ファイル (MP4, AVI, MOV, MKV, WMV)

**レスポンス例**:
```json
{
  "step_count": 182,
  "average_lean_angle": 85.5
}
```

### ヘルスチェック

**GET** `/api/health/`

**レスポンス例**:
```json
{
  "status": "ok",
  "message": "ランニング動画解析APIは正常に動作しています"
}
```

## 使用方法

1. バックエンドとフロントエンドの両方のサーバーを起動
2. ブラウザで `http://localhost:3000` にアクセス
3. ランニング動画ファイルをアップロード
4. 解析結果（歩数と前傾角度）を確認

## 解析アルゴリズム

### 歩数計測
- MediaPipeで人物の骨格ランドマークを検出
- 腰の中心座標（左右の腰ランドマークの中点）のY座標変化を追跡
- SciPyの`find_peaks`を使用して上下動の谷（極小値）を検出
- 谷の数を歩数として計算

### 前傾角度測定
- 肩の中心座標と腰の中心座標を算出
- 2点を結ぶ直線の垂直線に対する角度を計算
- 全フレームの角度の平均値を算出

## 注意事項

- 動画ファイルサイズの上限: 100MB
- 対応動画形式: MP4, AVI, MOV, MKV, WMV
- 人物が明確に映っている動画での使用を推奨
- 複数人が映っている場合、最も信頼度の高い人物を自動選択

## トラブルシューティング

### よくある問題

1. **MediaPipeのインストールエラー**
   ```bash
   pip install --upgrade pip
   pip install mediapipe
   ```

2. **OpenCVのインストールエラー**
   ```bash
   pip install opencv-python-headless
   ```

3. **CORSエラー**
   - `settings.py`の`CORS_ALLOWED_ORIGINS`を確認
   - フロントエンドとバックエンドのポート番号を確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 