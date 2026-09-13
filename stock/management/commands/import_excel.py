import os
from django.core.management.base import BaseCommand, CommandError
from stock.importers.excel_import import import_excel_log


class Command(BaseCommand):
    help = "Importe les mouvements de stock et trajets depuis un fichier Excel LOG_TFZ-TOUBKAL."

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            nargs='?',
            type=str,
            default=r'C:\Users\Kharraz\Desktop\LOG TFZ-TOUBKAL.xlsx',
            help="Chemin vers le fichier Excel (par defaut: C:\\Users\\Kharraz\\Desktop\\LOG TFZ-TOUBKAL.xlsx)"
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default='RECEIVING-EXPORT Status',
            help="Nom de la feuille Excel (par defaut: 'RECEIVING-EXPORT Status')"
        )
        parser.add_argument(
            '--no-trajets',
            action='store_true',
            help="Ne pas creer automatiquement de Trajets pour les exports"
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose_mode',
            help="Afficher le numero de ligne et la raison exacte de chaque ligne ignoree"
        )

    def handle(self, *args, **options):
        file_path = options['excel_file']
        sheet_name = options['sheet']
        create_trajets = not options['no_trajets']
        is_verbose = options.get('verbose_mode', False) or options.get('verbosity', 1) > 1

        if not os.path.exists(file_path):
            raise CommandError(f"Le fichier Excel n'existe pas : {file_path}")

        self.stdout.write(self.style.NOTICE(f"Debut de l'import depuis : {file_path} (feuille: {sheet_name})"))

        stats = import_excel_log(
            file_path=file_path,
            sheet_name=sheet_name,
            create_trajets=create_trajets
        )

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("RAPPORT D'IMPORTATION EXCEL FOCUS QUALITY"))
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"  -> Mouvements crees          : {stats['mouvements_crees']}"))
        self.stdout.write(f"       * Receptions creees     : {stats['receptions_crees']}")
        self.stdout.write(f"       * Exports crees         : {stats['exports_crees']}")
        self.stdout.write(f"  -> Trajets crees             : {stats['trajets_crees']}")
        self.stdout.write(f"  -> Mouvements doublons ign.  : {stats['mouvements_doublons']}")
        self.stdout.write(f"  -> Lignes ignorees / totaux  : {stats['lignes_ignorees']}")
        self.stdout.write("-" * 60)

        if stats.get('avertissements'):
            self.stdout.write(self.style.WARNING(f"Avertissements ({len(stats['avertissements'])}) :"))
            for warn in stats['avertissements']:
                self.stdout.write(self.style.WARNING(f"  - {warn}"))

        if stats['erreurs']:
            self.stdout.write(self.style.WARNING(f"Erreurs rencontrees ({len(stats['erreurs'])}) :"))
            for err in stats['erreurs']:
                self.stdout.write(self.style.ERROR(f"  - {err}"))
        else:
            self.stdout.write(self.style.SUCCESS("Aucune erreur rencontree lors du traitement des lignes."))
        self.stdout.write("=" * 60)

        # Mode verbeux : détail de chaque ligne ignorée
        if is_verbose and stats.get('lignes_ignorees_details'):
            self.stdout.write("")
            self.stdout.write("=" * 75)
            self.stdout.write(self.style.WARNING("DETAIL DES LIGNES IGNOREES (--verbose) :"))
            self.stdout.write("=" * 75)

            categories_count = {}
            for item in stats['lignes_ignorees_details']:
                cat_raw = item.get('categorie', 'autre')
                cat_tag = cat_raw.upper().replace('Ê', 'E').replace('É', 'E')
                categories_count[cat_tag] = categories_count.get(cat_tag, 0) + 1
                self.stdout.write(f"  Ligne {item['ligne']:3d} [{cat_tag:<15s}] : {item['raison']}")

            self.stdout.write("-" * 75)
            self.stdout.write(self.style.NOTICE("Synthese des lignes ignorees par categorie :"))
            for cat, count in sorted(categories_count.items()):
                self.stdout.write(f"   - {cat:<17s} : {count} ligne(s)")
            self.stdout.write("=" * 75)

