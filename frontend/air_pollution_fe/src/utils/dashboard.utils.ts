export function getAQIStyle(aqi: number) {
  if (isNaN(aqi) || aqi === null || aqi === undefined) {
    return { color: "#AAAAAA", label: "N/A" };
  }
  if (aqi <= 50) return { color: "#00E400", label: "Good / Tốt" };
  if (aqi <= 100) return { color: "#FFFF00", label: "Moderate / Trung bình" };
  if (aqi <= 150) return { color: "#FF7E00", label: "Unhealthy for Sensitive Groups / Kém" };
  if (aqi <= 200) return { color: "#FF0000", label: "Unhealthy / Xấu" };
  if (aqi <= 300) return { color: "#8F3F97", label: "Very Unhealthy / Rất xấu" };
  return { color: "#7E0023", label: "Hazardous / Nguy hại" };
}