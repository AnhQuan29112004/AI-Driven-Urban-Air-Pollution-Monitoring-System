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
    this.dashBoardService.getTestApi().pipe(
      takeUntil(
        this.destroy$
      )
    ).subscribe(res => {
      this.response = res.data.test
    })

    // Lắng nghe dữ liệu WebSocket từ Service đã được kết nối ở EmptyLayoutComponent
    this.dashBoardService.message$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(payload => {
      if (payload && payload.type === 'sensor_data') {
        this.sensorData = payload.data;
        this.pollutants = [
          { name: 'PM2.5', value: payload.data['pm25'], unit: 'AQI' },
          { name: 'PM10', value: payload.data['pm10'], unit: 'AQI' },
          { name: 'NO2', value: payload.data['no2'], unit: 'AQI' },
          { name: 'O3 (Ozone)', value: payload.data['o3'], unit: 'AQI' },
          { name: 'CO', value: payload.data['co'], unit: 'AQI' },
          { name: 'SO2', value: payload.data['so2'], unit: 'AQI' },
        ].map(p => {
          const val = Number(p.value);
          const style = getAQIStyle(val);
          const percentage = Math.min((val / 300) * 100, 100);
          return { ...p, percentage, colorHex: style.color };
        });
        this.weather = [
          { name: 'Temp', value:payload.data['temperature'] , icon: 'thermostat', color: 'secondary' },
          { name: 'Humidity', value:payload.data['humidity'] , icon: 'humidity_mid', color: 'primary' },
          { name: 'Wind', value:payload.data['wind_speed'] , icon: 'air', color: 'on-surface-variant' },
        ];
        this.AQI = payload.data['aqi'];
        this.aqiStyle = getAQIStyle(Number(this.AQI));
        
        // Update trend data
        const timestampStr = payload.data['timestamp'];
        const timeLabel = timestampStr ? new Date(timestampStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
        const heightPercent = Math.min((Number(this.AQI) / 300) * 100, 100);
        
        this.trendData.push({
          aqi: Number(this.AQI),
          timestamp: timestampStr || new Date().toISOString(),
          timeLabel,
          colorHex: this.aqiStyle.color,
          heightPercent
        });
        
        if (this.trendData.length > 24) {
          this.trendData.shift();
        }
        
        // Update X-axis labels for trend chart
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
    });
  }
  ngOnDestroy(): void {
    this.destroy$.next('')
    this.destroy$.complete()
  }
}
