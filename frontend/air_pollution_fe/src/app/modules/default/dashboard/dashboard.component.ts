import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService } from 'app/core/default/dashboard/dashboard.service';
import { OnInit, OnDestroy } from '@angular/core';
import { takeUntil, pipe, Subject } from 'rxjs';
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
  AQI: any;
  private destroy$ = new Subject()
  pollutants = [
    { name: 'PM2.5', value: 12.4, unit: 'μg/m³', percentage: 25, color: 'primary' },
    { name: 'PM10', value: 24.8, unit: 'μg/m³', percentage: 35, color: 'primary' },
    { name: 'NO2', value: 38.1, unit: 'ppb', percentage: 45, color: 'secondary' },
    { name: 'O3 (Ozone)', value: 15.2, unit: 'ppb', percentage: 15, color: 'secondary' },
  ];

  weather = [
    { name: 'Temp', value: '28°C', icon: 'thermostat', color: 'secondary' },
    { name: 'Humidity', value: '64%', icon: 'humidity_mid', color: 'primary' },
    { name: 'Wind', value: '12km/h', icon: 'air', color: 'on-surface-variant' },
  ];

  trendBars = [30, 35, 32, 28, 40, 45, 50, 48, 60, 75, 85, 70, 55, 40, 35, 38];
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
          { name: 'PM2.5', value: payload.data['pm25'], unit: 'AQI', percentage: 25, color: 'primary' },
          { name: 'PM10', value: payload.data['pm10'], unit: 'AQI', percentage: 35, color: 'primary' },
          { name: 'NO2', value: payload.data['no2'], unit: 'AQI', percentage: 45, color: 'secondary' },
          { name: 'O3 (Ozone)', value: payload.data['o3'], unit: 'AQI', percentage: 15, color: 'secondary' },
          { name: 'CO', value: payload.data['co'], unit: 'AQI', percentage: 15, color: 'secondary' },
          { name: 'SO2', value: payload.data['so2'], unit: 'AQI', percentage: 15, color: 'secondary' },
        ]
        this.weather = [
          { name: 'Temp', value:payload.data['temperature'] , icon: 'thermostat', color: 'secondary' },
          { name: 'Humidity', value:payload.data['humidity'] , icon: 'humidity_mid', color: 'primary' },
          { name: 'Wind', value:payload.data['wind_speed'] , icon: 'air', color: 'on-surface-variant' },
        ]
        this.AQI = payload.data['aqi']
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next('')
    this.destroy$.complete()
  }
}
