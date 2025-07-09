import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Machine {
  id: number;
  name: string;
  muscle_group: string;
  instructions: string;
  machine_type: string;
}

export interface Exercise {
  id: number;
  machine: Machine;
  sets: number;
  reps: number;
  weight: number;
  rpe?: number;
}

export interface Workout {
  id: number;
  name: string;
  date: string;
  exercises: Exercise[];
  duration_minutes?: number;
  completed: boolean;
}

export interface CalendarEvent {
  id: number;
  title: string;
  start_date: string;
  end_date: string;
  workout?: Workout;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) { }

  // Machines
  getMachines(): Observable<Machine[]> {
    return this.http.get<Machine[]>(`${environment.apiUrl}/machines/machines/`);
  }

  getMuscleGroups(): Observable<any[]> {
    return this.http.get<any[]>(`${environment.apiUrl}/machines/muscle-groups/`);
  }

  // Workouts
  getWorkouts(): Observable<Workout[]> {
    return this.http.get<Workout[]>(`${environment.apiUrl}/workouts/workouts/`);
  }

  createWorkout(workout: Partial<Workout>): Observable<Workout> {
    return this.http.post<Workout>(`${environment.apiUrl}/workouts/workouts/`, workout);
  }

  updateWorkout(id: number, workout: Partial<Workout>): Observable<Workout> {
    return this.http.put<Workout>(`${environment.apiUrl}/workouts/workouts/${id}/`, workout);
  }

  deleteWorkout(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/workouts/workouts/${id}/`);
  }

  startWorkout(workoutId: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/workouts/start-workout/`, { workout_id: workoutId });
  }

  completeWorkout(workoutId: number, data: any): Observable<any> {
    return this.http.post(`${environment.apiUrl}/workouts/complete-workout/`, {
      workout_id: workoutId,
      ...data
    });
  }

  // Exercises
  getExercises(): Observable<Exercise[]> {
    return this.http.get<Exercise[]>(`${environment.apiUrl}/workouts/exercises/`);
  }

  createExercise(exercise: Partial<Exercise>): Observable<Exercise> {
    return this.http.post<Exercise>(`${environment.apiUrl}/workouts/exercises/`, exercise);
  }

  // Calendar
  getCalendarEvents(): Observable<CalendarEvent[]> {
    return this.http.get<CalendarEvent[]>(`${environment.apiUrl}/calendar/events/`);
  }

  getPlans(): Observable<any[]> {
    return this.http.get<any[]>(`${environment.apiUrl}/calendar/plans/`);
  }

  createPlan(plan: any): Observable<any> {
    return this.http.post(`${environment.apiUrl}/calendar/plans/`, plan);
  }

  // Statistiques
  getUserStats(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/users/profile/stats/`);
  }
}
