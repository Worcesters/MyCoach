import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor() {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Récupérer le token directement depuis localStorage pour éviter la dépendance circulaire
    const token = localStorage.getItem('access_token');

    console.log('🔍 Intercepteur HTTP:', {
      url: req.url,
      method: req.method,
      hasToken: !!token,
      token: token ? `${token.substring(0, 20)}...` : 'aucun'
    });

    // Si un token existe, l'ajouter aux headers
    if (token) {
      const authReq = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      console.log('✅ Token ajouté aux headers pour:', req.url);
      return next.handle(authReq);
    }

    console.log('⚠️ Aucun token disponible pour:', req.url);
    // Sinon, continuer sans modification
    return next.handle(req);
  }
}
