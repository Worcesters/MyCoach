import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    const isAuthenticated = this.authService.isAuthenticated();
    console.log('🛡️ AuthGuard - Token présent:', isAuthenticated);

    if (isAuthenticated) {
      // Initialiser le profil si pas encore fait
      this.authService.initializeUserProfile();
      return true;
    } else {
      console.log('❌ Pas de token, redirection vers login');
      this.router.navigate(['/login']);
      return false;
    }
  }
}
