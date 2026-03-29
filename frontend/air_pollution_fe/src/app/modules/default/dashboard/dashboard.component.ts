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
  private destroy$ = new Subject()
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
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next('')
    this.destroy$.complete()
  }
}
