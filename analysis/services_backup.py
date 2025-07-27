# 緊急時用：ライブラリ不要のダミー解析
import os
import time

def analyze_run_dummy(video_path):
    """
    ライブラリ不要のダミー解析（デプロイテスト用）
    
    Args:
        video_path (str): 動画ファイルパス（使用しない）
        
    Returns:
        dict: 固定値を返す
    """
    # ファイルサイズから推定歩数を計算（簡易）
    try:
        file_size = os.path.getsize(video_path)
        # ファイルサイズ（MB）を歩数の近似値として使用
        estimated_steps = min(max(int(file_size / (1024 * 1024) * 10), 10), 200)
    except:
        estimated_steps = 50  # デフォルト値
    
    return {
        "step_count": estimated_steps,
        "average_lean_angle": 85.0,  # 標準的な角度
        "method": "dummy_analysis",
        "note": "ライブラリ不要の簡易解析版です"
    } 