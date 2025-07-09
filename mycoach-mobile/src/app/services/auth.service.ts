import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  weight: number;
  height: number;
  objective: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  private tokenSubject = new BehaviorSubject<string | null>(null);

  constructor(private http: HttpClient) {
    // Charger le token depuis le localStorage au démarrage
    const token = localStorage.getItem('access_token');
    console.log('🔑 Initialisation AuthService - Token trouvé:', !!token);
    if (token) {
      console.log('✅ Token chargé depuis localStorage:', token.substring(0, 20) + '...');
      this.tokenSubject.next(token);
      // Ne pas charger le profil immédiatement pour éviter les problèmes de timing
      // this.loadUserProfile();
    } else {
      console.log('❌ Aucun token trouvé dans localStorage');
    }
  }

  /**
   * Initialise le profil utilisateur si un token est disponible
   */
  initializeUserProfile(): void {
    const token = this.getToken();
    if (token && !this.currentUserSubject.value) {
      console.log('🔄 Initialisation du profil utilisateur...');
      this.loadUserProfile();
    }
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/auth/token/`, {
      email,
      password
    }).pipe(
      tap(response => {
        // Stocker les tokens
        console.log('💾 Stockage du token après login:', response.access.substring(0, 20) + '...');
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        this.tokenSubject.next(response.access);

        console.log('🔄 Token mis à jour dans BehaviorSubject');
        // Charger le profil utilisateur
        this.loadUserProfile();
      })
    );
  }

  register(userData: RegisterData): Observable<any> {
    return this.http.post(`${environment.apiUrl}/auth/register/`, userData);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
  }

  refreshToken(): Observable<any> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http.post(`${environment.apiUrl}/auth/token/refresh/`, {
      refresh: refreshToken
    }).pipe(
      tap((response: any) => {
        localStorage.setItem('access_token', response.access);
        this.tokenSubject.next(response.access);
      })
    );
  }

  private loadUserProfile(): void {
    console.log('📡 Chargement du profil utilisateur...');
    this.http.get<User>(`${environment.apiUrl}/users/profile/`).subscribe({
      next: (user) => {
        console.log('✅ Profil utilisateur chargé:', user.email);
        this.currentUserSubject.next(user);
      },
      error: (error) => {
        console.error('❌ Erreur chargement profil:', error);

        // Ne déconnecter que si c'est une erreur d'authentification (401)
        if (error.status === 401) {
          console.log('🔒 Token invalide, déconnexion...');
          this.logout();
        } else {
          console.log('⚠️ Erreur temporaire, conservation du token');
          // Pour les autres erreurs (réseau, 500, etc.), on garde le token
        }
      }
    });
  }

  getToken(): string | null {
    let token = this.tokenSubject.value;

    // Si le BehaviorSubject n'a pas de token, vérifier localStorage
    if (!token) {
      token = localStorage.getItem('access_token');
      if (token) {
        console.log('🔄 Token récupéré depuis localStorage et mis à jour dans BehaviorSubject');
        this.tokenSubject.next(token);
      }
    }

    console.log('🔍 getToken() appelé - token disponible:', !!token);
    return token;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
}
