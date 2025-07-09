import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from './auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Ajouter le token à la requête si disponible
    const token = this.authService.getToken();

    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        // Si erreur 401 (non autorisé), essayer de rafraîchir le token
        if (error.status === 401 && token) {
          return this.authService.refreshToken().pipe(
            switchMap(() => {
              // Réessayer la requête avec le nouveau token
              const newToken = this.authService.getToken();
              const retryReq = req.clone({
                setHeaders: {
                  Authorization: `Bearer ${newToken}`
                }
              });
              return next.handle(retryReq);
            }),
            catchError(() => {
              // Si le rafraîchissement échoue, déconnecter l'utilisateur
              this.authService.logout();
              return throwError(() => error);
            })
          );
        }

        return throwError(() => error);
      })
    );
  }
}
