import { environment } from "environment/environment.dev";

const baseUrl = environment.baseUrl;

export const uriConfig = {
    API_LATEST : baseUrl + '/api/dashboard/latest/',
    API_HISTORY : baseUrl + '/api/dashboard/history/',
    WEBSOCKET_URL: 'ws://localhost:8000/ws/socket/'
}