import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stock.models import Profil


def load_env_file_if_present():
    """Charge un éventuel fichier .env situé à la racine du projet dans os.environ."""
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    env_file = root_dir / '.env'
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        key, val = key.strip(), val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass


class Command(BaseCommand):
    help = "Initialise deux comptes utilisateurs de test (Superviseur et Chef d'équipe) avec mots de passe via variables d'environnement."

    def handle(self, *args, **options):
        # Charge le fichier .env si présent
        load_env_file_if_present()

        # Lecture des mots de passe depuis les variables d'environnement (avec repli générique)
        env_supervisor_pwd = os.environ.get('SEED_SUPERVISOR_PASSWORD') or os.environ.get('SUPERVISOR_PASSWORD')
        supervisor_pwd = env_supervisor_pwd or 'SuperviseurDefault2026!'
        supervisor_src = "Variable d'environnement" if env_supervisor_pwd else "Valeur par défaut générique"

        env_chef_pwd = os.environ.get('SEED_CHEF_EQUIPE_PASSWORD') or os.environ.get('CHEF_EQUIPE_PASSWORD')
        chef_equipe_pwd = env_chef_pwd or 'ChefEquipeDefault2026!'
        chef_src = "Variable d'environnement" if env_chef_pwd else "Valeur par défaut générique"

        users_data = [
            {
                'username': 'superviseur',
                'first_name': 'Samir',
                'last_name': 'Superviseur',
                'email': 'superviseur@focusquality.ma',
                'password': supervisor_pwd,
                'source': supervisor_src,
                'role': 'SUPERVISEUR',
                'is_staff': True,
            },
            {
                'username': 'chef_equipe',
                'first_name': 'Karim',
                'last_name': 'Chef d\'équipe',
                'email': 'chef.equipe@focusquality.ma',
                'password': chef_equipe_pwd,
                'source': chef_src,
                'role': 'CHEF_EQUIPE',
                'is_staff': False,
            },
        ]

        self.stdout.write(self.style.NOTICE("Initialisation des comptes utilisateurs (Superviseur / Chef d'équipe)..."))

        for u_info in users_data:
            user, created = User.objects.get_or_create(
                username=u_info['username'],
                defaults={
                    'first_name': u_info['first_name'],
                    'last_name': u_info['last_name'],
                    'email': u_info['email'],
                    'is_staff': u_info['is_staff'],
                }
            )
            user.set_password(u_info['password'])
            user.first_name = u_info['first_name']
            user.last_name = u_info['last_name']
            user.email = u_info['email']
            user.is_staff = u_info['is_staff']
            user.save()

            profil, p_created = Profil.objects.get_or_create(
                user=user,
                defaults={'role': u_info['role']}
            )
            if not p_created:
                profil.role = u_info['role']
                profil.save()

            action_str = "Créé" if created else "Mis à jour"
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [OK] {action_str} : {user.username} ({profil.get_role_display()}) | Mot de passe : {u_info['password']} ({u_info['source']})"
                )
            )

        self.stdout.write("\n" + "=" * 75)
        self.stdout.write(
            self.style.WARNING(
                "NOTE DE SÉCURITÉ :\n"
                "- Les mots de passe sont configurés via les variables SEED_SUPERVISOR_PASSWORD\n"
                "  et SEED_CHEF_EQUIPE_PASSWORD (cf. fichier .env.example).\n"
                "- Si aucune variable n'est définie, des valeurs génériques par défaut sont appliquées.\n"
                "- Veillez à définir vos propres mots de passe en production via un fichier .env !"
            )
        )
        self.stdout.write("=" * 75 + "\n")
