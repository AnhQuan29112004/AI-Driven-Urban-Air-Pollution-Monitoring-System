import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService } from 'app/core/default/dashboard/dashboard.service';
import { OnInit, OnDestroy } from '@angular/core';
import { takeUntil, pipe, Subject } from 'rxjs';
import { getAQIStyle } from 'utils/dashboard.utils';
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit, OnDestroy {
  response: string;
  sensorData: any = null;
  isMobileMenuOpen = false;
  AQI: number | string = '--';
  aqiStyle = { color: "#00E400", label: "N/A" };
  private destroy$ = new Subject()
  pollutants: any[] = [
    { name: 'PM2.5', value: 12.4, unit: 'μg/m³', percentage: 25, colorHex: '#00E400' },
    { name: 'PM10', value: 24.8, unit: 'μg/m³', percentage: 35, colorHex: '#00E400' },
    { name: 'NO2', value: 38.1, unit: 'ppb', percentage: 45, colorHex: '#00E400' },
    { name: 'O3 (Ozone)', value: 15.2, unit: 'ppb', percentage: 15, colorHex: '#00E400' },
  ];

  weather = [
    { name: 'Temp', value: '28°C', icon: 'thermostat', color: 'secondary' },
    { name: 'Humidity', value: '64%', icon: 'humidity_mid', color: 'primary' },
    { name: 'Wind', value: '12km/h', icon: 'air', color: 'on-surface-variant' },
  ];

  trendData: { aqi: number, timestamp: string, timeLabel: string, colorHex: string, heightPercent: number }[] = [];
  trendLabels: string[] = [];
  constructor(
    private dashBoardService: DashboardService
  ) {

  }
  ngOnInit(): void {
    //Lấy data mới nhất bằng API thay vì testApi
    this.dashBoardService.getLatestApi().pipe(
      takeUntil(this.destroy$)
    ).subscribe(res => {
      if (res && res.data) {
        this.updateDashboardData(res.data);
      }
    });

    //Lấy data lịch sử 24h để vẽ biểu đồ
    this.dashBoardService.getHistory24hApi().pipe(
      takeUntil(this.destroy$)
    ).subscribe(res => {
      if (res && res.data && Array.isArray(res.data)) {
        const history = res.data.reverse();
        this.trendData = [];
        history.forEach((data: any) => {
          this.pushToTrendData(data);
        });
        this.updateTrendLabels();
      }
    });

    this.dashBoardService.message$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(payload => {
      if (payload && payload.type === 'sensor_data') {
        this.updateDashboardData(payload.data);
        this.pushToTrendData(payload.data);
        this.updateTrendLabels();
      }
    });
  }

  updateDashboardData(data: any) {
    this.sensorData = data;
    this.pollutants = [
      { name: 'PM2.5', value: data['pm25'], unit: 'AQI' },
      { name: 'PM10', value: data['pm10'], unit: 'AQI' },
      { name: 'NO2', value: data['no2'], unit: 'AQI' },
      { name: 'O3 (Ozone)', value: data['o3'], unit: 'AQI' },
      { name: 'CO', value: data['co'], unit: 'AQI' },
      { name: 'SO2', value: data['so2'], unit: 'AQI' },
    ].map(p => {
      const val = Number(p.value || 0);
      const style = getAQIStyle(val);
      const percentage = Math.min((val / 300) * 100, 100);
      return { ...p, percentage, colorHex: style.color };
    });
    this.weather = [
      { name: 'Temp', value: data['temperature'], icon: 'thermostat', color: 'secondary' },
      { name: 'Humidity', value: data['humidity'], icon: 'humidity_mid', color: 'primary' },
      { name: 'Wind', value: data['wind_speed'] || data['windSpeed'], icon: 'air', color: 'on-surface-variant' },
    ];
    this.AQI = data['aqi'] || '--';
    if (this.AQI !== '--') {
       this.aqiStyle = getAQIStyle(Number(this.AQI));
    }
  }

  pushToTrendData(data: any) {
    const timestampStr = data['timestamp'];
    const timeLabel = timestampStr ? new Date(timestampStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
    const aqiNum = Number(data['aqi'] || 0);
    const heightPercent = Math.min((aqiNum / 300) * 100, 100);
    const style = getAQIStyle(aqiNum);
    
    this.trendData.push({
      aqi: aqiNum,
      timestamp: timestampStr || new Date().toISOString(),
      timeLabel,
      colorHex: style.color,
      heightPercent
    });
    
    if (this.trendData.length > 24) {
      this.trendData.shift();
    }
  }

  updateTrendLabels() {
    const labels = [];
    const numLabels = 6;
    if (this.trendData.length > 0) {
        const step = Math.max(1, Math.floor(this.trendData.length / numLabels));
        for (let i = 0; i < this.trendData.length; i += step) {
          labels.push(this.trendData[i].timeLabel);
        }
        if (labels[labels.length - 1] !== this.trendData[this.trendData.length - 1].timeLabel) {
           labels[labels.length - 1] = this.trendData[this.trendData.length - 1].timeLabel;
        }
    }
    this.trendLabels = labels;
  }
  ngOnDestroy(): void {
    this.destroy$.next('')
    this.destroy$.complete()
  }
}
