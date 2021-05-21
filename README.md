# MKWFaraphel Installateur
Cet outil vous permet d'installer Mario Kart Wii Faraphel sans avoir à modifier tous les fichiers 1 par 1.

## Prérequis
- Une ROM de Mario Kart Wii dumpé depuis votre console avec votre propre copie (en CISO, ISO, WBFS, FST (Dossier))
- L'installateur disponible dans https://github.com/Faraphel/MKWF-Install/releases en .exe, ou utiliser la
source si vous avez python 3.8 et la librairie requests

## Installations
- Lancer l'application MKWF-Install.exe / MKWF-Install.py
- Sélectionner la ROM de votre jeu
- Appuyez sur "Extraire le fichier", qui va copier votre jeu dans un dossier nommé MKWiiFaraphel
- Une fois le fichier extrait, appuyez sur "Préparer les fichiers", cela va convertir beaucoup de fichiers,
comprenant les textes, les textures, les fichiers des menus, certains items et les courses. Cela peut prendre
beaucoup de temps (30min-1h) ! Cette opération n'a besoin d'être faite qu'une seule fois
- Une fois les fichiers prêt, vous pouvez choisir le format de sortie du jeu (ISO, CISO, WBFS, FST (Dossier))
et appuyez sur "Installer le mod". Après cette opération, une notification va apparaître vous informant
que l'installation est terminée

Une fois cela fait, vous pouvez lancer votre jeu avec Dolphin ou depuis votre Wii avec un Homebrew.
L'ID du jeu est RMCP60 si vous n'avez pas choisi comme format de sortie FST.

Si vous rencontrez un problème avec l'installateur, envoyez-moi un mp sur discord à Faraphel#5846