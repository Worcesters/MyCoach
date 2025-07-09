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
  weight: number | null = null;
  height: number | null = null;
  objective: string = '';
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
    console.log('🔄 Tentative d\'inscription...');

    // Validation des champs
    if (!this.isFormValid()) {
      this.showToast('Veuillez remplir tous les champs obligatoires (*)', 'warning');
      return;
    }

    // Validation format email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.showToast('Veuillez entrer un email valide', 'warning');
      return;
    }

    // Validation poids
    if (!this.weight || this.weight < 30 || this.weight > 300) {
      this.showToast('Le poids doit être entre 30 et 300 kg', 'warning');
      return;
    }

    // Validation taille
    if (!this.height || this.height < 100 || this.height > 250) {
      this.showToast('La taille doit être entre 100 et 250 cm', 'warning');
      return;
    }

    // Validation objectif
    if (!this.objective) {
      this.showToast('Veuillez choisir un objectif', 'warning');
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
        last_name: this.lastName,
        weight: this.weight,
        height: this.height,
        objective: this.objective
      };

      console.log('📡 Envoi des données d\'inscription:', {
        email: registerData.email,
        first_name: registerData.first_name,
        last_name: registerData.last_name,
        weight: registerData.weight,
        height: registerData.height,
        objective: registerData.objective
      });

      await this.authService.register(registerData).toPromise();
      await loading.dismiss();
      this.isLoading = false;

      console.log('✅ Inscription réussie');
      this.showToast('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success');

      // Rediriger vers la page de connexion
      this.router.navigate(['/login']);

    } catch (error: any) {
      await loading.dismiss();
      this.isLoading = false;
      console.error('❌ Erreur lors de l\'inscription:', error);

      let errorMessage = 'Une erreur est survenue lors de la création du compte';

      if (error?.status === 400) {
        if (error.error?.email) {
          errorMessage = 'Cet email est déjà utilisé';
        } else if (error.error?.password) {
          errorMessage = 'Le mot de passe ne respecte pas les critères';
        } else if (error.error?.weight) {
          errorMessage = 'Poids invalide';
        } else if (error.error?.height) {
          errorMessage = 'Taille invalide';
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
      this.weight &&
      this.height &&
      this.objective &&
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
