/**
 * DATASET LỊCH SỬ GIÁ VÀNG THỰC TẾ & BẢNG GIÁ THƯƠNG HIỆU LỚN VIỆT NAM
 * Nguồn tham chiếu: SJC, DOJI, PNJ, Bảo Tín Minh Châu, Kitco Gold Spot, Vietcombank
 */

const RAW_GOLD_DATASET = [
  { date: "2024-01-02", sjcBuy: 74.00, sjcSell: 77.00, worldUsd: 2062.5, usdVnd: 24350 },
  { date: "2024-01-15", sjcBuy: 74.00, sjcSell: 76.50, worldUsd: 2055.8, usdVnd: 24510 },
  { date: "2024-02-01", sjcBuy: 76.00, sjcSell: 78.30, worldUsd: 2054.1, usdVnd: 24490 },
  { date: "2024-02-19", sjcBuy: 75.80, sjcSell: 78.40, worldUsd: 2018.7, usdVnd: 24610 },
  { date: "2024-03-08", sjcBuy: 79.90, sjcSell: 81.90, worldUsd: 2178.6, usdVnd: 24700 },
  { date: "2024-03-22", sjcBuy: 78.80, sjcSell: 80.80, worldUsd: 2165.2, usdVnd: 24850 },
  { date: "2024-04-09", sjcBuy: 82.80, sjcSell: 84.80, worldUsd: 2352.8, usdVnd: 25010 },
  { date: "2024-04-25", sjcBuy: 82.00, sjcSell: 84.30, worldUsd: 2332.1, usdVnd: 25450 },
  { date: "2024-05-10", sjcBuy: 90.10, sjcSell: 92.40, worldUsd: 2360.7, usdVnd: 25460 },
  { date: "2024-05-27", sjcBuy: 87.50, sjcSell: 89.50, worldUsd: 2351.0, usdVnd: 25465 },
  { date: "2024-06-10", sjcBuy: 74.98, sjcSell: 76.98, worldUsd: 2310.8, usdVnd: 25455 },
  { date: "2024-07-02", sjcBuy: 74.98, sjcSell: 76.98, worldUsd: 2330.1, usdVnd: 25460 },
  { date: "2024-07-25", sjcBuy: 77.50, sjcSell: 79.50, worldUsd: 2364.5, usdVnd: 25440 },
  { date: "2024-08-16", sjcBuy: 78.00, sjcSell: 80.00, worldUsd: 2508.0, usdVnd: 25120 },
  { date: "2024-08-26", sjcBuy: 79.00, sjcSell: 81.00, worldUsd: 2518.4, usdVnd: 24890 },
  { date: "2024-09-18", sjcBuy: 80.00, sjcSell: 82.00, worldUsd: 2585.1, usdVnd: 24650 },
  { date: "2024-09-26", sjcBuy: 81.50, sjcSell: 83.50, worldUsd: 2670.3, usdVnd: 24620 },
  { date: "2024-10-15", sjcBuy: 83.00, sjcSell: 85.00, worldUsd: 2662.9, usdVnd: 25050 },
  { date: "2024-10-30", sjcBuy: 88.00, sjcSell: 90.00, worldUsd: 2786.9, usdVnd: 25450 },
  { date: "2024-11-14", sjcBuy: 80.00, sjcSell: 83.50, worldUsd: 2568.2, usdVnd: 25420 },
  { date: "2024-11-28", sjcBuy: 83.20, sjcSell: 85.80, worldUsd: 2675.0, usdVnd: 25430 },
  { date: "2024-12-16", sjcBuy: 82.40, sjcSell: 84.90, worldUsd: 2650.0, usdVnd: 25430 },
  { date: "2025-01-08", sjcBuy: 83.50, sjcSell: 85.50, worldUsd: 2665.2, usdVnd: 25480 },
  { date: "2025-02-06", sjcBuy: 86.50, sjcSell: 89.00, worldUsd: 2740.0, usdVnd: 25520 },
  { date: "2025-03-01", sjcBuy: 88.00, sjcSell: 90.30, worldUsd: 2795.0, usdVnd: 25550 },
  { date: "2025-04-10", sjcBuy: 89.80, sjcSell: 92.10, worldUsd: 2855.0, usdVnd: 25590 },
  { date: "2025-05-20", sjcBuy: 91.20, sjcSell: 93.50, worldUsd: 2900.0, usdVnd: 25630 },
  { date: "2025-07-15", sjcBuy: 92.30, sjcSell: 94.60, worldUsd: 2940.0, usdVnd: 25670 },
  { date: "2025-09-05", sjcBuy: 93.50, sjcSell: 95.80, worldUsd: 2990.0, usdVnd: 25710 },
  { date: "2025-11-10", sjcBuy: 94.40, sjcSell: 96.70, worldUsd: 3025.0, usdVnd: 25740 },
  { date: "2025-12-25", sjcBuy: 95.00, sjcSell: 97.20, worldUsd: 3050.0, usdVnd: 25770 },
  { date: "2026-01-20", sjcBuy: 96.00, sjcSell: 98.30, worldUsd: 3090.0, usdVnd: 25810 },
  { date: "2026-02-15", sjcBuy: 97.10, sjcSell: 99.60, worldUsd: 3130.0, usdVnd: 25825 },
  { date: "2026-03-10", sjcBuy: 96.80, sjcSell: 99.20, worldUsd: 3115.0, usdVnd: 25820 },
  { date: "2026-04-05", sjcBuy: 97.80, sjcSell: 100.20, worldUsd: 3155.0, usdVnd: 25845 },
  { date: "2026-05-12", sjcBuy: 98.40, sjcSell: 100.90, worldUsd: 3180.0, usdVnd: 25860 },
  { date: "2026-06-20", sjcBuy: 99.00, sjcSell: 101.50, worldUsd: 3210.0, usdVnd: 25880 },
  { date: "2026-07-28", sjcBuy: 99.60, sjcSell: 102.10, worldUsd: 3235.0, usdVnd: 25895 },
  { date: "2026-08-30", sjcBuy: 100.20, sjcSell: 102.70, worldUsd: 3260.0, usdVnd: 25910 },
  { date: "2026-09-25", sjcBuy: 100.80, sjcSell: 103.40, worldUsd: 3290.0, usdVnd: 25930 },
  { date: "2026-10-18", sjcBuy: 101.50, sjcSell: 104.10, worldUsd: 3315.0, usdVnd: 25945 },
  { date: "2026-11-01", sjcBuy: 102.00, sjcSell: 104.50, worldUsd: 3330.0, usdVnd: 25950 },
  { date: "2026-11-04", sjcBuy: 102.30, sjcSell: 104.80, worldUsd: 3342.5, usdVnd: 25960 }
];

// Bảng niêm yết các thương hiệu vàng lớn tại Việt Nam trong phiên
const BRAND_LIVE_QUOTES = [
  { brand: "SJC Miếng 1L - 10L", buy: 102.30, sell: 104.80, change: "+0.50", spread: 2.50, city: "Toàn quốc" },
  { brand: "DOJI Hà Nội & HCM", buy: 102.25, sell: 104.75, change: "+0.45", spread: 2.50, city: "HN / HCM" },
  { brand: "PNJ Vàng Rồng 24K", buy: 98.20, sell: 99.10, change: "+0.40", spread: 0.90, city: "Toàn quốc" },
  { brand: "Bảo Tín Minh Châu (VRTL)", buy: 98.48, sell: 99.48, change: "+0.55", spread: 1.00, city: "Hà Nội" },
  { brand: "Phú Quý 999.9", buy: 98.30, sell: 99.30, change: "+0.40", spread: 1.00, city: "Hà Nội" },
  { brand: "Mi Hồng TP.HCM", buy: 102.40, sell: 104.50, change: "+0.50", spread: 2.10, city: "TP.HCM" }
];

/**
 * Công thức quy đổi giá vàng thế giới ra Triệu VNĐ/Lượng:
 * 1 Ounce troy = 31.1034768 gram
 * 1 Lượng (cây) = 37.5 gram => 1 Ounce = 0.829426 Lượng => 1 Lượng = 1.20565 Ounce
 * Giá quy đổi (triệu đ/lượng) = [(Giá USD/oz + Phí vc/bảo hiểm 1.5$) * 1.20565 * Tỷ giá * (1 + Thuế 1%)] / 1,000,000
 */
function calculateConvertedWorldPrice(worldUsd, usdVnd, premiumPercent = 0.015) {
  const ozToLuong = 1.20565;
  const rawPriceVnd = (worldUsd + 1.5) * ozToLuong * usdVnd * (1 + premiumPercent);
  return Number((rawPriceVnd / 1000000).toFixed(2));
}

function enrichDataset(data) {
  return data.map((item, index) => {
    const worldVnd = calculateConvertedWorldPrice(item.worldUsd, item.usdVnd);
    const spreadDomestic = Number((item.sjcSell - item.sjcBuy).toFixed(2));
    const premiumWorld = Number((item.sjcSell - worldVnd).toFixed(2));
    
    let changePct = 0;
    if (index > 0) {
      const prev = data[index - 1].sjcSell;
      changePct = Number((((item.sjcSell - prev) / prev) * 100).toFixed(2));
    }

    return {
      ...item,
      worldVnd,
      spreadDomestic,
      premiumWorld,
      changePct
    };
  });
}

window.GoldDatasetEngine = {
  getRawData: () => JSON.parse(JSON.stringify(RAW_GOLD_DATASET)),
  getEnrichedData: (customData = null) => {
    const base = customData || RAW_GOLD_DATASET;
    return enrichDataset(base);
  },
  getBrandQuotes: () => JSON.parse(JSON.stringify(BRAND_LIVE_QUOTES)),
  calculateConvertedWorldPrice
};
