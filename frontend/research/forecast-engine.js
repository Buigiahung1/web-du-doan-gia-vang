/**
 * FORECASTING ENGINE - MÔ HÌNH TOÁN HỌC & THỐNG KÊ KINH TẾ LƯỢNG
 * Bao gồm:
 * 1. Holt's Linear Exponential Smoothing (Dự báo xu hướng làm mịn số mũ kép)
 * 2. ARIMA(1,1,0) Drift Model (Tự hồi quy sai phân bậc 1)
 * 3. Multi-factor Macro Regression (Hồi quy đa nhân tố: Kitco World + Tỷ giá USD/VND + Biên trượt)
 * 4. Tính toán dải tin cậy (Confidence Interval Cones: 80% & 95%)
 * 5. Backtesting Engine: Đo lường MAPE, RMSE, MAE, R-Squared trên tập kiểm định thực tế
 */

class GoldForecastEngine {
  constructor(dataset) {
    this.dataset = dataset;
  }

  setDataset(dataset) {
    this.dataset = dataset;
  }

  /**
   * Tính toán các chỉ báo kỹ thuật cơ bản trên chuỗi giá
   */
  calculateIndicators(series, periodSMA = 14) {
    const sma = [];
    const rsi = [];
    const bollinger = [];

    for (let i = 0; i < series.length; i++) {
      // SMA
      if (i < periodSMA - 1) {
        sma.push(null);
      } else {
        const slice = series.slice(i - periodSMA + 1, i + 1);
        const avg = slice.reduce((a, b) => a + b, 0) / periodSMA;
        sma.push(Number(avg.toFixed(2)));
      }

      // Bollinger Bands (20 periods, 2 std dev)
      const bbPeriod = 14;
      if (i < bbPeriod - 1) {
        bollinger.push({ upper: null, lower: null, middle: null });
      } else {
        const slice = series.slice(i - bbPeriod + 1, i + 1);
        const mean = slice.reduce((a, b) => a + b, 0) / bbPeriod;
        const variance = slice.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / bbPeriod;
        const std = Math.sqrt(variance);
        bollinger.push({
          middle: Number(mean.toFixed(2)),
          upper: Number((mean + 2 * std).toFixed(2)),
          lower: Number((mean - 2 * std).toFixed(2))
        });
      }

      // RSI (14)
      if (i < 14) {
        rsi.push(null);
      } else {
        let gains = 0;
        let losses = 0;
        for (let j = i - 13; j <= i; j++) {
          const diff = series[j] - series[j - 1];
          if (diff >= 0) gains += diff;
          else losses += Math.abs(diff);
        }
        const avgGain = gains / 14;
        const avgLoss = losses / 14;
        if (avgLoss === 0) {
          rsi.push(100);
        } else {
          const rs = avgGain / avgLoss;
          const rsiVal = 100 - (100 / (1 + rs));
          rsi.push(Number(rsiVal.toFixed(1)));
        }
      }
    }

    return { sma, bollinger, rsi };
  }

  /**
   * 1. Mô hình Holt's Linear Exponential Smoothing
   * alpha: hệ số làm mịn mức (Level), beta: hệ số làm mịn xu hướng (Trend)
   */
  runHoltModel(series, steps = 14, alpha = 0.35, beta = 0.15) {
    if (series.length < 5) return null;

    let level = series[0];
    let trend = series[1] - series[0];
    const fitted = [level];
    const residuals = [0];

    for (let t = 1; t < series.length; t++) {
      const prevLevel = level;
      const prevTrend = trend;
      const y = series[t];

      level = alpha * y + (1 - alpha) * (prevLevel + prevTrend);
      trend = beta * (level - prevLevel) + (1 - beta) * prevTrend;

      const oneStepAhead = prevLevel + prevTrend;
      fitted.push(Number(oneStepAhead.toFixed(2)));
      residuals.push(y - oneStepAhead);
    }

    // Tính độ lệch chuẩn của phần dư để tạo dải tin cậy
    const residualVariance = residuals.slice(5).reduce((acc, r) => acc + r * r, 0) / (residuals.length - 5);
    const residualStd = Math.sqrt(residualVariance);

    // Sinh dự báo cho 'steps' bước tương lai
    const forecasts = [];
    for (let h = 1; h <= steps; h++) {
      const pointForecast = level + h * trend;
      // Sai số tăng dần theo căn bậc hai của chân trời dự báo (h)
      const horizonStd = residualStd * Math.sqrt(h);
      
      forecasts.push({
        step: h,
        forecast: Number(pointForecast.toFixed(2)),
        upper80: Number((pointForecast + 1.282 * horizonStd).toFixed(2)),
        lower80: Number((pointForecast - 1.282 * horizonStd).toFixed(2)),
        upper95: Number((pointForecast + 1.96 * horizonStd).toFixed(2)),
        lower95: Number((pointForecast - 1.96 * horizonStd).toFixed(2))
      });
    }

    return {
      fitted,
      forecasts,
      stdError: residualStd,
      modelName: "Holt's Linear Smoothing (Xu hướng kép thích nghi)"
    };
  }

  /**
   * 2. Mô hình ARIMA(1,1,0) với độ trôi (Drift)
   */
  runARIMAModel(series, steps = 14) {
    if (series.length < 5) return null;

    // Sai phân bậc 1: dy_t = y_t - y_{t-1}
    const diffs = [];
    for (let i = 1; i < series.length; i++) {
      diffs.push(series[i] - series[i - 1]);
    }

    // Tính độ trôi trung bình (Drift)
    const drift = diffs.reduce((a, b) => a + b, 0) / diffs.length;

    // Ước lượng phi (hệ số tự hồi quy bậc 1 trên chuỗi sai phân)
    let num = 0;
    let den = 0;
    for (let i = 1; i < diffs.length; i++) {
      num += (diffs[i] - drift) * (diffs[i - 1] - drift);
      den += Math.pow(diffs[i - 1] - drift, 2);
    }
    const phi = den !== 0 ? Math.max(Math.min(num / den, 0.85), -0.85) : 0.2;

    // Tính sai số
    const residuals = [];
    for (let i = 1; i < diffs.length; i++) {
      const predDiff = drift + phi * (diffs[i - 1] - drift);
      residuals.push(diffs[i] - predDiff);
    }
    const variance = residuals.reduce((a, b) => a + b * b, 0) / residuals.length;
    const std = Math.sqrt(variance);

    // Dự báo tương lai
    let lastPrice = series[series.length - 1];
    let lastDiff = diffs[diffs.length - 1];
    const forecasts = [];

    for (let h = 1; h <= steps; h++) {
      const expectedDiff = drift + Math.pow(phi, h) * (lastDiff - drift);
      lastPrice = lastPrice + expectedDiff;
      const horizonStd = std * Math.sqrt(h);

      forecasts.push({
        step: h,
        forecast: Number(lastPrice.toFixed(2)),
        upper80: Number((lastPrice + 1.282 * horizonStd).toFixed(2)),
        lower80: Number((lastPrice - 1.282 * horizonStd).toFixed(2)),
        upper95: Number((lastPrice + 1.96 * horizonStd).toFixed(2)),
        lower95: Number((lastPrice - 1.96 * horizonStd).toFixed(2))
      });
    }

    return {
      forecasts,
      stdError: std,
      phi: Number(phi.toFixed(3)),
      drift: Number(drift.toFixed(3)),
      modelName: "ARIMA(1,1,0) có tham số Drift"
    };
  }

  /**
   * 3. Mô hình Kinh tế lượng vĩ mô (Macro Multi-factor)
   * Phân tích tác động truyền dẫn từ Vàng TG (Kitco) và Tỷ giá USD/VND sang Giá SJC
   */
  runMacroFactorModel(data, steps = 14) {
    if (data.length < 5) return null;

    // Tính chênh lệch giá trung bình (Premium) trong 10 phiên gần nhất
    const recent = data.slice(-10);
    const avgPremium = recent.reduce((sum, item) => sum + (item.sjcSell - item.worldVnd), 0) / recent.length;

    // Lấy xu thế tăng trưởng của Kitco trong 15 phiên
    const recentWorld = data.slice(-15);
    const worldRateOfChange = (recentWorld[recentWorld.length - 1].worldUsd - recentWorld[0].worldUsd) / recentWorld.length;

    // Lấy tỷ giá gần nhất
    const latestUsdVnd = data[data.length - 1].usdVnd;
    let currentWorldUsd = data[data.length - 1].worldUsd;

    const forecasts = [];
    const residualStd = 0.85; // Độ biến động chuẩn theo triệu đồng/lượng

    for (let h = 1; h <= steps; h++) {
      currentWorldUsd += worldRateOfChange * 0.95; // Có lực cản hồi quy về trung bình
      const convertedVnd = window.GoldDatasetEngine.calculateConvertedWorldPrice(currentWorldUsd, latestUsdVnd);
      // Giá SJC mô phỏng = Giá thế giới quy đổi + Premium cân bằng thị trường
      const projectedSjc = convertedVnd + avgPremium;

      const horizonStd = residualStd * Math.sqrt(h);
      forecasts.push({
        step: h,
        forecast: Number(projectedSjc.toFixed(2)),
        upper80: Number((projectedSjc + 1.282 * horizonStd).toFixed(2)),
        lower80: Number((projectedSjc - 1.282 * horizonStd).toFixed(2)),
        upper95: Number((projectedSjc + 1.96 * horizonStd).toFixed(2)),
        lower95: Number((projectedSjc - 1.96 * horizonStd).toFixed(2))
      });
    }

    return {
      forecasts,
      stdError: residualStd,
      avgPremium: Number(avgPremium.toFixed(2)),
      modelName: "Mô hình Truyền dẫn Vĩ mô (Kitco Spot + Tỷ giá USD/VND)"
    };
  }

  /**
   * 4. Hệ thống Kiểm định Ngược (Backtesting Engine)
   * Cắt dữ liệu: 80% Train, 20% Test để tính các chỉ số định lượng khách quan
   */
  runBacktest(targetField = 'sjcSell') {
    const rawSeries = this.dataset.map(item => item[targetField]);
    const totalLen = rawSeries.length;
    if (totalLen < 15) return null;

    const splitIdx = Math.floor(totalLen * 0.80);
    const trainSeries = rawSeries.slice(0, splitIdx);
    const testSeries = rawSeries.slice(splitIdx);
    const testLen = testSeries.length;

    // Chạy mô hình Holt trên tập train
    const holtResult = this.runHoltModel(trainSeries, testLen);
    const predictions = holtResult.forecasts.map(f => f.forecast);

    // Tính các chỉ số sai số thống kê:
    let sumAbsError = 0;
    let sumAbsPctError = 0;
    let sumSquaredError = 0;
    let correctDirectionCount = 0;

    let testMean = testSeries.reduce((a, b) => a + b, 0) / testLen;
    let totalSS = 0;
    let resSS = 0;

    for (let i = 0; i < testLen; i++) {
      const actual = testSeries[i];
      const pred = predictions[i];
      const error = actual - pred;

      sumAbsError += Math.abs(error);
      sumAbsPctError += Math.abs(error / actual);
      sumSquaredError += error * error;

      totalSS += Math.pow(actual - testMean, 2);
      resSS += Math.pow(error, 2);

      // Kiểm tra xu hướng
      if (i > 0) {
        const actualDir = actual - testSeries[i - 1];
        const predDir = pred - predictions[i - 1];
        if ((actualDir >= 0 && predDir >= 0) || (actualDir < 0 && predDir < 0)) {
          correctDirectionCount++;
        }
      }
    }

    const mae = Number((sumAbsError / testLen).toFixed(2));
    const mape = Number(((sumAbsPctError / testLen) * 100).toFixed(2));
    const rmse = Number(Math.sqrt(sumSquaredError / testLen).toFixed(2));
    const r2 = Number(Math.max(0, 1 - (resSS / (totalSS || 1))).toFixed(3));
    const directionalAccuracy = Number(((correctDirectionCount / (testLen - 1 || 1)) * 100).toFixed(1));

    return {
      trainCount: splitIdx,
      testCount: testLen,
      mae,   // Triệu VNĐ
      mape,  // Phần trăm (%)
      rmse,  // Triệu VNĐ
      r2,    // R-bình phương (0 - 1)
      directionalAccuracy, // Độ chính xác hướng đi (%)
      testDates: this.dataset.slice(splitIdx).map(d => d.date),
      actuals: testSeries,
      predictions
    };
  }
}

window.GoldForecastEngine = GoldForecastEngine;
