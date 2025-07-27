# 🚀 ランニング動画解析アプリ - デプロイ手順

## Renderでのデプロイ

### 1. 事前準備

1. **GitHubリポジトリの作成**
   ```bash
   # GitHubで新しいリポジトリを作成し、コードをプッシュ
   git remote add origin https://github.com/YOUR_USERNAME/running-analysis-app.git
   git branch -M main
   git push -u origin main
   ```

2. **Renderアカウント作成**
   - [Render.com](https://render.com) でアカウント作成
   - GitHubアカウントと連携

### 2. デプロイ設定

#### 📡 **バックエンド（API）のデプロイ**

1. Render Dashboard → **"New Web Service"**
2. GitHubリポジトリを選択
3. 設定：
   ```
   Name: running-analysis-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   Start Command: gunicorn running_analysis_project.wsgi:application --bind 0.0.0.0:$PORT
   ```

4. 環境変数を設定：
   ```
   DJANGO_SECRET_KEY: [自動生成]
   DEBUG: False
   ALLOWED_HOSTS: *
   DJANGO_SETTINGS_MODULE: running_analysis_project.settings
   ```

5. **Deploy** をクリック

#### ⚛️ **フロントエンド（UI）のデプロイ**

1. Render Dashboard → **"New Web Service"**
2. 同じGitHubリポジトリを選択
3. 設定：
   ```
   Name: running-analysis-frontend
   Environment: Node
   Build Command: cd frontend && npm ci && npm run build
   Start Command: cd frontend && npx serve -s build -p $PORT
   ```

4. 環境変数を設定：
   ```
   REACT_APP_API_URL: https://running-analysis-api.onrender.com
   ```

5. **Deploy** をクリック

### 3. アクセスURL

デプロイ完了後、以下のURLでアクセス可能：

- **フロントエンド**: `https://running-analysis-frontend.onrender.com`
- **API**: `https://running-analysis-api.onrender.com`

### 4. 動作確認

1. **API確認**: `https://running-analysis-api.onrender.com/api/health/`
2. **アプリ確認**: フロントエンドURLで動画アップロード機能をテスト

---

## 🐳 Docker でのデプロイ（代替手段）

### Dockerfile（バックエンド用）

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# システム依存関係
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコード
COPY . .

# 静的ファイル収集
RUN python manage.py collectstatic --noinput

# ポート
EXPOSE 8000

# 起動コマンド
CMD ["gunicorn", "running_analysis_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DJANGO_SECRET_KEY=your-secret-key
      - ALLOWED_HOSTS=*
      
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
```

---

## 📝 トラブルシューティング

### よくある問題

1. **MediaPipeのインストールエラー**
   ```
   ERROR: Could not find a version that satisfies the requirement mediapipe
   ```
   
   **解決方法**:
   - `requirements-light.txt` を使用（MediaPipe除外版）
     ```bash
     Build Command: pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - または、Pythonバージョンを確認（`runtime.txt`で`python-3.9.18`指定）
   - システム依存関係をビルドコマンドに追加:
     ```bash
     apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 && pip install -r requirements.txt
     ```

2. **CORS エラー**
   - `CORS_ALLOWED_ORIGINS` の設定確認
   - フロントエンドとバックエンドのURL一致確認

3. **静的ファイルが読み込まれない**
   - `WhiteNoise` の設定確認
   - `collectstatic` の実行確認

4. **動画アップロードエラー**
   - ファイルサイズ制限の確認（100MB制限）
   - サポート形式の確認（MP4, AVI, MOV等）

### ログの確認

```bash
# Renderでのログ確認
# Dashboard → Service → Logs タブ
```

## 🌐 公開後の管理

- **監視**: Render Dashboardでメトリクス確認
- **スケーリング**: 有料プランでオートスケーリング
- **ドメイン**: カスタムドメインの設定可能
- **SSL**: 自動SSL証明書（Let's Encrypt）

---

## 💡 本番運用の推奨事項

1. **セキュリティ**
   - `DEBUG=False` の確認
   - 強力な `DJANGO_SECRET_KEY` の設定
   - `ALLOWED_HOSTS` の適切な設定

2. **パフォーマンス**
   - 動画ファイルサイズの制限
   - タイムアウト設定の調整
   - キャッシュの設定

3. **監視**
   - アプリケーションメトリクスの監視
   - エラーログの確認
   - ユーザビリティテスト 