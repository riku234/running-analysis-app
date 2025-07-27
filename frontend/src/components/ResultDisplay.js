import React from 'react';

/**
 * ランニング動画解析結果を表示するコンポーネント
 * 
 * @param {Object} props - コンポーネントのプロパティ
 * @param {number} props.step_count - 歩数
 * @param {number} props.average_lean_angle - 平均前傾角度
 * @param {string} props.note - 解析方法の説明（オプション）
 * @param {string} props.method - 使用された解析方法（オプション）
 */
const ResultDisplay = ({ step_count, average_lean_angle, note, method }) => {
  // データが存在しない場合の処理
  if (step_count === undefined && average_lean_angle === undefined) {
    return (
      <div className="result-display">
        <h2>解析結果</h2>
        <p>解析結果がありません。動画をアップロードして解析を実行してください。</p>
      </div>
    );
  }

  return (
    <div className="result-display">
      <h2>解析結果</h2>
      <div className="result-container">
        <div className="result-item">
          <div className="result-label">歩数:</div>
          <div className="result-value">
            {step_count !== undefined ? `${step_count} 歩` : '計測できませんでした'}
          </div>
        </div>
        
        <div className="result-item">
          <div className="result-label">平均前傾角度:</div>
          <div className="result-value">
            {average_lean_angle !== undefined ? `${average_lean_angle} 度` : '計測できませんでした'}
          </div>
        </div>
      </div>
      
      {/* 解析方法の表示 */}
      {(note || method) && (
        <div className="analysis-info">
          <h3>解析方法</h3>
          {note && <p className="analysis-note">{note}</p>}
          {method && (
            <p className="analysis-method">
              使用手法: {method === 'opencv_basic' ? 'OpenCVベース解析' : 'MediaPipe高精度解析'}
            </p>
          )}
        </div>
      )}

      {/* 解析結果の解釈ヒント */}
      <div className="result-tips">
        <h3>結果の見方</h3>
        <ul>
          <li><strong>歩数</strong>: 動画中で検出された歩数の総計です</li>
          <li><strong>前傾角度</strong>: 90度に近いほど直立、それより小さいほど前傾しています</li>
        </ul>
      </div>
    </div>
  );
};

export default ResultDisplay; 