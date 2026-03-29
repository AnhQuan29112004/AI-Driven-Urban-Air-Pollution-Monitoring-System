export interface AirQualityData {
  timestamp: string;
  sensor_id?: string;
  city: string;
  latitude: number;
  longitude: number;
  co: number;
  no2: number;
  o3_proxy: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  aqi: number;
  noise_factor?: number;
}