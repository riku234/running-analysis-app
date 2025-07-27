import cv2
import mediapipe as mp
import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.ndimage import gaussian_filter1d
import math


def analyze_run_basics(video_path):
    """
    ランニング動画から歩数と前傾角度を解析する関数
    
    Args:
        video_path (str): 解析対象の動画ファイルパス
        
    Returns:
        dict: {"step_count": int, "average_lean_angle": float}
    """
    # MediaPipeの初期化
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # 動画の読み込み
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError("動画ファイルを開けませんでした")
    
    # 動画の情報を取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    hip_y_coordinates = []  # 腰のY座標を記録するリスト
    lean_angles = []  # 前傾角度を記録するリスト
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # フレームをRGBに変換（MediaPipeはRGBを期待）
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 姿勢推定の実行
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # 腰の中心座標を計算（ランドマーク23と24の中点）
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
            hip_center_y = (left_hip.y + right_hip.y) / 2
            hip_y_coordinates.append(hip_center_y)
            
            # 肩の中心座標を計算（ランドマーク11と12の中点）
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            
            hip_center_x = (left_hip.x + right_hip.x) / 2
            
            # 前傾角度の計算（肩と腰を結ぶ線の垂直線に対する角度）
            if shoulder_center_y != hip_center_y:
                # ベクトルの計算
                dx = shoulder_center_x - hip_center_x
                dy = shoulder_center_y - hip_center_y
                
                # 垂直線（Y軸）に対する角度を計算
                angle_rad = math.atan2(dx, -dy)  # -dyは座標系の向きを調整
                angle_deg = math.degrees(angle_rad)
                
                # 角度を0-180度の範囲に正規化
                if angle_deg < 0:
                    angle_deg += 180
                    
                lean_angles.append(angle_deg)
        
        frame_count += 1
    
    cap.release()
    pose.close()
    
    # 歩数の計算（改善版：より高精度な歩数検出）
    step_count = 0
    if len(hip_y_coordinates) > 10:  # 最低限のデータ数が必要
        hip_y_array = np.array(hip_y_coordinates)
        
        # 1. データの平滑化（ノイズ除去）
        if len(hip_y_array) > 5:
            # ガウシアンフィルタでノイズを除去
            smoothed_hip_y = gaussian_filter1d(hip_y_array, sigma=2.0)
        else:
            smoothed_hip_y = hip_y_array
        
        # 2. 適応的閾値の計算
        hip_y_std = np.std(smoothed_hip_y)
        hip_y_mean = np.mean(smoothed_hip_y)
        
        # 標準偏差が小さすぎる場合は歩行動作が少ないと判断
        if hip_y_std < 0.005:  # 閾値を調整可能
            step_count = 0
        else:
            # 3. 歩数検出のための動的パラメータ設定
            
            # 実際のFPSを使用（フォールバック付き）
            actual_fps = fps if fps > 0 else 30.0  # デフォルト30fps
            video_duration = len(hip_y_coordinates) / actual_fps
            
            # 現実的な歩行周期制約（0.8-1.5秒の間隔）
            min_step_interval = int(0.8 * actual_fps)  # 最小歩行間隔（フレーム数）
            max_step_interval = int(1.5 * actual_fps)  # 最大歩行間隔（フレーム数）
            distance_constraint = max(8, min_step_interval)
            
            # 高さ閾値（標準偏差の一定割合）
            height_threshold = hip_y_std * 0.3  # 調整可能なパラメータ
            
            # 4. 谷（歩行の最低点）の検出
            # データを反転してピークとして検出
            inverted_hip_y = -smoothed_hip_y
            
            # ピーク検出（改善されたパラメータ）
            peaks, properties = find_peaks(
                inverted_hip_y, 
                height=-hip_y_mean + height_threshold,  # 適応的高さ閾値
                distance=distance_constraint,  # 現実的な距離制約
                prominence=hip_y_std * 0.2  # ピークの顕著性
            )
            
            # 5. さらなるフィルタリング
            valid_peaks = []
            if len(peaks) > 0:
                peak_heights = smoothed_hip_y[peaks]
                
                # 異常値除去（四分位範囲を使用）
                q1 = np.percentile(peak_heights, 25)
                q3 = np.percentile(peak_heights, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                for peak in peaks:
                    peak_height = smoothed_hip_y[peak]
                    if lower_bound <= peak_height <= upper_bound:
                        valid_peaks.append(peak)
            
            step_count = len(valid_peaks)
            
            # 6. 最終的な妥当性チェック
            # 動画の長さから推定される最大歩数をチェック
            max_reasonable_steps = int(video_duration * 2.5)  # 最大2.5歩/秒
            
            if step_count > max_reasonable_steps:
                step_count = max_reasonable_steps
            
            # デバッグ情報（ログに出力）
            print(f"歩数検出デバッグ: フレーム数={len(hip_y_coordinates)}, FPS={actual_fps:.1f}, "
                  f"動画時間={video_duration:.1f}秒, 標準偏差={hip_y_std:.4f}, "
                  f"生ピーク数={len(peaks) if 'peaks' in locals() else 0}, "
                  f"有効ピーク数={len(valid_peaks) if 'valid_peaks' in locals() else 0}, "
                  f"最終歩数={step_count}")
    
    # 平均前傾角度の計算
    average_lean_angle = 0.0
    if len(lean_angles) > 0:
        average_lean_angle = sum(lean_angles) / len(lean_angles)
    
    return {
        "step_count": step_count,
        "average_lean_angle": round(average_lean_angle, 1)
    } 