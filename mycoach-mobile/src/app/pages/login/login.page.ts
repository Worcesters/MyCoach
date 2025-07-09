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
  isLoading: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private toastController: ToastController,
    private loadingController: LoadingController
  ) {}

  async login() {
    // Validation des champs
    if (!this.email || !this.password) {
      this.showToast('Veuillez remplir tous les champs', 'warning');
      return;
    }

    // Validation format email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.showToast('Veuillez entrer un email valide', 'warning');
      return;
    }

    if (this.password.length < 6) {
      this.showToast('Le mot de passe doit contenir au moins 6 caractères', 'warning');
      return;
    }

    this.isLoading = true;
    const loading = await this.loadingController.create({
      message: 'Connexion en cours...',
      backdropDismiss: false
    });
    await loading.present();

    try {
      await this.authService.login(this.email, this.password).toPromise();
      await loading.dismiss();
      this.isLoading = false;

      // Initialiser le profil utilisateur après la connexion
      this.authService.initializeUserProfile();

      this.showToast('Connexion réussie !', 'success');
      this.router.navigate(['/tabs']);
    } catch (error: any) {
      await loading.dismiss();
      this.isLoading = false;
      console.error('Erreur de connexion:', error);

      let errorMessage = 'Une erreur est survenue';
      if (error?.status === 401) {
        errorMessage = 'Email ou mot de passe incorrect';
      } else if (error?.status === 0) {
        errorMessage = 'Impossible de contacter le serveur. Vérifiez votre connexion internet.';
      } else if (error?.error?.detail) {
        errorMessage = error.error.detail;
      }

      this.showToast(errorMessage, 'danger');
    }
  }

  private async showToast(message: string, color: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color,
      position: 'bottom',
      buttons: [
        {
          text: 'Fermer',
          role: 'cancel'
        }
      ]
    });
    await toast.present();
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }

  // Méthode pour permettre la soumission avec Enter
  onKeyPress(event: any) {
    if (event.key === 'Enter' && !this.isLoading) {
      this.login();
    }
  }
}
