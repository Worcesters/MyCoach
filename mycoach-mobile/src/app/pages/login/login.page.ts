import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  standalone: true,
  imports: [IonicModule, FormsModule, CommonModule]
})
export class LoginPage {
  email: string = '';
  password: string = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private toastController: ToastController,
    private loadingController: LoadingController
  ) {}

  async login() {
    if (!this.email || !this.password) {
      this.showToast('Veuillez remplir tous les champs', 'warning');
      return;
    }

    const loading = await this.loadingController.create({
      message: 'Connexion...'
    });
    await loading.present();

    this.authService.login(this.email, this.password).subscribe({
      next: async () => {
        await loading.dismiss();
        this.showToast('Connexion réussie !', 'success');
        this.router.navigate(['/tabs']);
      },
      error: async (error) => {
        await loading.dismiss();
        console.error('Erreur de connexion:', error);
        this.showToast('Email ou mot de passe incorrect', 'danger');
      }
    });
  }

  private async showToast(message: string, color: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color,
      position: 'bottom'
    });
    await toast.present();
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }
}
