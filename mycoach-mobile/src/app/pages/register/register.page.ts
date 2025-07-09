import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService, RegisterData } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.page.html',
  styleUrls: ['./register.page.scss'],
  standalone: true,
  imports: [IonicModule, FormsModule, CommonModule]
})
export class RegisterPage {
  firstName: string = '';
  lastName: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  isLoading: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private toastController: ToastController,
    private loadingController: LoadingController
  ) {}

  async register() {
    // Validation des champs
    if (!this.isFormValid()) {
      this.showToast('Veuillez remplir tous les champs correctement', 'warning');
      return;
    }

    // Validation format email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.showToast('Veuillez entrer un email valide', 'warning');
      return;
    }

    // Validation mot de passe
    if (this.password.length < 6) {
      this.showToast('Le mot de passe doit contenir au moins 6 caractères', 'warning');
      return;
    }

    // Vérification confirmation mot de passe
    if (this.password !== this.confirmPassword) {
      this.showToast('Les mots de passe ne correspondent pas', 'warning');
      return;
    }

    this.isLoading = true;
    const loading = await this.loadingController.create({
      message: 'Création du compte...',
      backdropDismiss: false
    });
    await loading.present();

    try {
      const registerData: RegisterData = {
        email: this.email,
        password: this.password,
        first_name: this.firstName,
        last_name: this.lastName
      };

      await this.authService.register(registerData).toPromise();
      await loading.dismiss();
      this.isLoading = false;

      this.showToast('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success');

      // Rediriger vers la page de connexion
      this.router.navigate(['/login']);

    } catch (error: any) {
      await loading.dismiss();
      this.isLoading = false;
      console.error('Erreur lors de l\'inscription:', error);

      let errorMessage = 'Une erreur est survenue lors de la création du compte';

      if (error?.status === 400) {
        if (error.error?.email) {
          errorMessage = 'Cet email est déjà utilisé';
        } else if (error.error?.password) {
          errorMessage = 'Le mot de passe ne respecte pas les critères';
        } else {
          errorMessage = 'Données invalides. Vérifiez vos informations.';
        }
      } else if (error?.status === 0) {
        errorMessage = 'Impossible de contacter le serveur. Vérifiez votre connexion internet.';
      }

      this.showToast(errorMessage, 'danger');
    }
  }

  isFormValid(): boolean {
    return !!(
      this.firstName.trim() &&
      this.lastName.trim() &&
      this.email.trim() &&
      this.password &&
      this.confirmPassword
    );
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

  goToLogin() {
    this.router.navigate(['/login']);
  }

  // Méthode pour permettre la soumission avec Enter
  onKeyPress(event: any) {
    if (event.key === 'Enter' && !this.isLoading) {
      this.register();
    }
  }
}
