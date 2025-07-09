import { Component, OnInit } from '@angular/core';
import { IonApp, IonRouterOutlet } from '@ionic/angular/standalone';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  imports: [IonApp, IonRouterOutlet],
})
export class AppComponent implements OnInit {
  constructor(private authService: AuthService) {}

  ngOnInit() {
    // Initialiser le profil utilisateur si un token est présent au démarrage
    setTimeout(() => {
      this.authService.initializeUserProfile();
    }, 100); // Petit délai pour s'assurer que l'intercepteur est configuré
  }
}
