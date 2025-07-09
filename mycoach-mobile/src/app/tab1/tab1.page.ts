import { Component, OnInit } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { ApiService, Workout } from '../services/api.service';
import { AuthService, User } from '../services/auth.service';

@Component({
  selector: 'app-tab1',
  templateUrl: 'tab1.page.html',
  styleUrls: ['tab1.page.scss'],
  standalone: true,
  imports: [IonicModule, CommonModule],
})
export class Tab1Page implements OnInit {
  workouts: Workout[] = [];
  currentUser: User | null = null;
  loading = false;

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
    this.loadWorkouts();
  }

  async loadWorkouts() {
    this.loading = true;
    this.apiService.getWorkouts().subscribe({
      next: (workouts) => {
        this.workouts = workouts;
        this.loading = false;
      },
      error: (error) => {
        console.error('Erreur chargement workouts:', error);
        this.loading = false;
      }
    });
  }

  async startWorkout(workout: Workout) {
    this.apiService.startWorkout(workout.id).subscribe({
      next: () => {
        console.log('Workout démarré');
        this.loadWorkouts();
      },
      error: (error) => {
        console.error('Erreur démarrage workout:', error);
      }
    });
  }

  logout() {
    this.authService.logout();
  }

  doRefresh(event: any) {
    this.loadWorkouts();
    setTimeout(() => {
      event.target.complete();
    }, 1000);
  }
}
