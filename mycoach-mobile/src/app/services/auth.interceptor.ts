import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor() {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    console.log('🔐 AuthInterceptor: Intercepting request', {
      url: req.url,
      method: req.method,
      headers: req.headers.keys()
    });

    // Récupérer le token directement depuis localStorage pour éviter la dépendance circulaire
    const token = localStorage.getItem('access_token');
    console.log('🔐 AuthInterceptor: Token found?', !!token);

    if (token) {
      console.log('🔐 AuthInterceptor: Token details', {
        hasToken: true,
        tokenLength: token.length,
        tokenStart: token.substring(0, 20) + '...',
        isValidJWT: token.split('.').length === 3
      });

      const authReq = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('🔐 AuthInterceptor: Request with auth headers', {
        authorization: authReq.headers.get('Authorization')?.substring(0, 30) + '...',
        contentType: authReq.headers.get('Content-Type'),
        url: authReq.url
      });

      return next.handle(authReq).pipe(
        catchError((error: HttpErrorResponse) => {
          console.error('🔐 AuthInterceptor: Request failed', {
            url: req.url,
            status: error.status,
            statusText: error.statusText,
            message: error.message,
            error: error.error,
            headers: error.headers?.keys()
          });

          if (error.status === 401) {
            console.warn('🔐 AuthInterceptor: 401 Unauthorized - clearing tokens and redirecting');
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_profile');
            // Redirection vers login
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
          }

          return throwError(() => error);
        })
      );
    }

    console.log('🔐 AuthInterceptor: No token, proceeding without auth for', req.url);
    return next.handle(req);
  }
}
