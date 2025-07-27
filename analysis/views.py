import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .services import analyze_run_basics, analyze_run_basic_opencv_only, MEDIAPIPE_AVAILABLE
import logging

# ログ設定
logger = logging.getLogger(__name__)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def analyze_running_video(request):
    """
    ランニング動画を解析するAPIエンドポイント
    
    POSTリクエストで動画ファイルを受け取り、歩数と前傾角度を解析して返す
    
    Returns:
        JSON: {"step_count": int, "average_lean_angle": float}
    """
    try:
        # リクエストから動画ファイルを取得
        if 'video' not in request.FILES:
            return Response(
                {"error": "動画ファイルが見つかりません。'video'という名前でファイルをアップロードしてください。"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        video_file = request.FILES['video']
        
        # ファイル形式のチェック
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        file_extension = os.path.splitext(video_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return Response(
                {"error": f"サポートされていないファイル形式です。対応形式: {', '.join(allowed_extensions)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # ファイルの内容を一時ファイルに書き込み
            for chunk in video_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # 動画解析の実行（環境に応じて最適な手法を選択）
            logger.info(f"動画解析を開始: {video_file.name}")
            
            if MEDIAPIPE_AVAILABLE:
                try:
                    # MediaPipeを使用した高精度解析
                    analysis_result = analyze_run_basics(temp_file_path)
                    logger.info(f"MediaPipe解析完了: {analysis_result}")
                except Exception as mediapipe_error:
                    # MediaPipe解析でエラーが発生した場合のフォールバック
                    logger.warning(f"MediaPipe解析失敗、OpenCVフォールバックを使用: {str(mediapipe_error)}")
                    analysis_result = analyze_run_basic_opencv_only(temp_file_path)
                    analysis_result["note"] = "MediaPipe解析でエラーが発生したため、OpenCVベースの簡易解析を使用しました"
                    logger.info(f"OpenCV解析完了: {analysis_result}")
            else:
                # MediaPipeが利用できない環境では最初からOpenCV解析を使用
                logger.info("MediaPipeが利用できません。OpenCVベースの解析を使用します。")
                analysis_result = analyze_run_basic_opencv_only(temp_file_path)
                analysis_result["note"] = "この環境ではMediaPipeが利用できないため、OpenCVベースの簡易解析を使用しました"
                logger.info(f"OpenCV解析完了: {analysis_result}")
            
            # 結果を返す
            return Response(analysis_result, status=status.HTTP_200_OK)
            
        except Exception as analysis_error:
            logger.error(f"動画解析エラー: {str(analysis_error)}")
            return Response(
                {"error": f"動画解析中にエラーが発生しました: {str(analysis_error)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        finally:
            # 一時ファイルを削除
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"一時ファイルの削除に失敗: {cleanup_error}")
    
    except Exception as e:
        logger.error(f"APIエラー: {str(e)}")
        return Response(
            {"error": f"リクエスト処理中にエラーが発生しました: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """
    APIの稼働状況を確認するヘルスチェックエンドポイント
    """
    return Response(
        {"status": "ok", "message": "ランニング動画解析APIは正常に動作しています"},
        status=status.HTTP_200_OK
    ) 