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
    if (token) {
      this.tokenSubject.next(token);
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
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        this.tokenSubject.next(response.access);

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
    this.http.get<User>(`${environment.apiUrl}/users/profile/`).subscribe({
      next: (user) => this.currentUserSubject.next(user),
      error: (error) => {
        console.error('Erreur chargement profil:', error);
        this.logout();
      }
    });
  }

  getToken(): string | null {
    return this.tokenSubject.value;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
}
