import { Injectable } from '@angular/core';
import { Dashboard } from './dashboard.type';
import { map, pipe, switchMap, Observable, Subject, BehaviorSubject, tap, catchError, of } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { HttpClient } from '@angular/common/http';
import { uriConfig } from '../../uri/config_uri.config';
@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  constructor(
    private http: HttpClient,
  ) { }

  dashBoard: Subject<any> = new Subject()
  private socket$: WebSocketSubject<any>=null;
  private messageSubject: BehaviorSubject<any>= new BehaviorSubject<any>('')
  public message$ = this.messageSubject.asObservable()
  private connectionSubject$ = new BehaviorSubject<boolean>(false);
  connection$ = this.connectionSubject$.asObservable();

  getTestApi(param?: any): Observable<any> {
    return this.http.get<any>(uriConfig.API_TEST).pipe(
      map(res => ({
        data: res.data
      }))
    )
  }

  connect(){
    if (this.socket$){
      this.socket$.complete()
    }
    this.socket$ = webSocket({
      url: uriConfig.WEBSOCKET_URL,
      openObserver: {
        next: () => {
            console.log('WebSocket connected!');
            this.connectionSubject$.next(true);
        }
      },
      closeObserver: {
        next: () => {
            console.log('WebSocket disconnected!');
            this.connectionSubject$.next(false);
            this.socket$ = null;
        }
      }
    });

    this.socket$.subscribe({
      next: (message)=>{
        this.messageSubject.next(message)
      },
      error:(error)=>{
        this.connectionSubject$.next(false);
        
      }
    });
    return this.connection$
  }

  sendMessage(message: any): void {
    if (this.socket$) {
      this.socket$.next(message);
    } else {
      console.error('WebSocket is not connected');
    }
  }
}
