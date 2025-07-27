import React, { useState } from 'react';
import axios from 'axios';
import ResultDisplay from './components/ResultDisplay';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setError(null);
    setAnalysisResult(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('動画ファイルを選択してください');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('video', selectedFile);

    const apiUrl = process.env.REACT_APP_API_URL || 'https://running-analysis-api.onrender.com';
    
    try {
      const response = await axios.post(`${apiUrl}/api/analyze/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30秒タイムアウト
      });

      console.log('API Response:', response);
      console.log('Response Data:', response.data);
      
      if (response.data && response.status === 200) {
        setAnalysisResult(response.data);
      } else {
        setError('予期しないレスポンス形式です');
      }
    } catch (err) {
      console.error('API Error:', err);
      console.error('Response:', err.response);
      
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.status === 200 && err.response?.data) {
        // 成功レスポンスだが何らかの理由でエラーとして扱われた場合
        setAnalysisResult(err.response.data);
      } else {
        setError(`解析中にエラーが発生しました: ${err.message}`);
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏃‍♂️ ランニング動画解析アプリ</h1>
        <p>動画をアップロードして歩数と前傾角度を測定しましょう</p>
      </header>

      <main className="App-main">
        <div className="upload-section">
          <h2>📹 動画ファイルをアップロード</h2>
          <div className="file-input-container">
            <input
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="file-input"
            />
            {selectedFile && (
              <p className="selected-file">選択されたファイル: {selectedFile.name}</p>
            )}
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
            className="analyze-button"
          >
            {isAnalyzing ? '解析中...' : '🔍 解析開始'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <h3>⚠️ エラー</h3>
            <p>{error}</p>
          </div>
        )}

        {analysisResult && (
          <ResultDisplay
            step_count={analysisResult.step_count}
            average_lean_angle={analysisResult.average_lean_angle}
            note={analysisResult.note}
            method={analysisResult.method}
          />
        )}
      </main>
    </div>
  );
}

export default App; 