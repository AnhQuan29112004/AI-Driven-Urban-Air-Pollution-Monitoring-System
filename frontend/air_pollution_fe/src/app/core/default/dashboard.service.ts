import { Injectable } from '@angular/core';
import {Dashboard} from './dashboard.type';
import { map, pipe,switchMap, Observable, Subject, BehaviorSubject, tap, catchError, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { uriConfig } from '../uri/config_uri.config';
@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  constructor(
    private http: HttpClient
  ) { }

  dashBoard:Subject<any>= new Subject()

  getTestApi(param?:any):Observable<any>{
    return this.http.get<any>(uriConfig.API_TEST).pipe(
      map(res=>({
        data: res.data
      }))
    )
  }
}
