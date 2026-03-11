import { environment } from "environment/environment.dev";

const baseUrl = environment.baseUrl;

export const uriConfig = {
    API_TEST : baseUrl + '/api/test-api/'
}