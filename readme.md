# Documentation de Mise en Place du Projet

Ce document décrit les étapes nécessaires pour lancer le projet, qui est un starter pack simpliste :

- **Authentification** : Permet de s'authentifier + récupérer son mot de passe en cas d'oubli
- **Envoie de mail Gmail** : Permet d'envoyer un mail à un utilisateur (mot de passe oublié, invitation à une organisation, etc.)
- **Création d'Organisation** : Permet de créer une nouvelle organisation.
- **Édition d'Organisation** : Permet de modifier le nom d'une organisation.
- **Suppression d'Organisation** : Permet de supprimer une organisation.
- **Invitation d'Utilisateur à une Organisation** : Permet d'inviter un utilisateur à rejoindre une organisation.
- **Mise à Jour du Rôle d'Utilisateur** : Permet de mettre à jour le rôle d'un utilisateur.
- **Mise à Jour du Statut d'Utilisateur** : Permet de mettre à jour le statut d'un utilisateur.
- **Ajout de Connecteur** : Permet d'ajouter un nouveau connecteur.
- **Suppression de Connecteur** : Permet de supprimer un connecteur.
- **Upload de Fichier** : Permet d'uploader un ou plusieurs fichiers avec barre de progression.

## Dépendances

- **Flask** : pour exécuter l'application web.
- **Flask-SQLAlchemy** : pour gérer la base de données.
- **Flask-Migrate** : pour gérer les migrations de base de données.
- **Flask-Login** : pour gérer l'authentification des utilisateurs.
- **psycopg2-binary** : pour la connexion à la base de données PostgreSQL.
- **werkzeug** : pour les utilitaires web.
- **Flask-Mail** : pour envoyer des e-mails depuis l'application.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants sur votre machine :

- **Docker** : pour exécuter la base de données PostgreSQL.
- **Python** : pour exécuter l'application Flask.
- **pip** : pour installer les dépendances Python.

## Étapes de Mise en Place

### 1. Lancer la Base de Données avec Docker seule

Pour démarrer la base de données PostgreSQL, exécutez la commande suivante dans votre terminal :

```bash
   docker run --name postgres-db -e POSTGRES_DB=ma_base -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
```

Tu ne connais pas docker ? [Deviens expert avec moi 🚀](https://ada-study.com)

Cette commande fait ce qui suit :

- Crée un conteneur Docker nommé `postgres-db`.
- Définit les variables d'environnement pour la base de données, l'utilisateur et le mot de passe.
- Expose le port 5432 pour permettre la connexion à la base de données depuis l'extérieur du conteneur.

### 2. Installer les Dépendances

Une fois la base de données en cours d'exécution, installez toutes les dépendances nécessaires en exécutant :

```bash
   pip install -r requirements.txt
```

Cela installera toutes les bibliothèques Python requises pour le projet, telles que Flask, Flask-SQLAlchemy, Flask-Login, etc.

### 3. Initialiser le Projet de Base de Données

Pour initialiser le projet de base de données, exécutez les commandes suivantes :

```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   flask run --debug
```

Ces commandes effectuent les opérations suivantes :

- `flask db init` : Crée un répertoire de migration pour gérer les modifications de la base de données.
- `flask db migrate` : Crée une migration initiale basée sur les modèles définis dans le code.
- `flask db upgrade` : Applique les migrations à la base de données.

### 4. Configurer les Variables d'Environnement

Avant de lancer l'application, vous devez définir les variables d'environnement nécessaires. Cela peut être fait en exécutant les commandes suivantes :

#### Sur Mac OS

```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```

#### Sur Windows

```bash
   set FLASK_APP=run.py
   set FLASK_ENV=development
```

### 5. Lancer l'Application

Pour démarrer l'application Flask, exécutez :

```bash
   flask run
```

Cela lancera le serveur de développement Flask, et vous pourrez accéder à l'application via `http://127.0.0.1:5001`.

### 6. Gérer les Utilisateurs

Après avoir créé un premier utilisateur, vous devez exécuter les commandes suivantes dans le conteneur Docker pour passer en admin :

```bash
   docker ps
   docker exec -it <id_container> bash
```

Ensuite, connectez-vous à la base de données PostgreSQL :

```bash
   psql -U postgres -d ma_base
```

Une fois connecté, exécutez la commande suivante pour mettre à jour le rôle d'un utilisateur dans le conteneur :

```sql
   UPDATE utilisateur
   SET role = 'admin'
   WHERE email = 'Votre email ici';
```

## Vous souhaitez en apprendre plus sur Python, la data et la data engineering ?

[Découvrez notre formation complète sur ada-study.com](https://ada-study.com) !

Nous vous proposons un parcours de formation personnalisé pour vous aider à acquérir les compétences nécessaires pour réussir dans le domaine de la data. Rejoignez notre communauté 🚀

# Pourquoi Docker ?

Docker permet de s'assurer que l'application fonctionne de la même manière sur différents environnements.

# Pourquoi utiliser un fichier Dockerfile ?

Un fichier Dockerfile permet de définir l'environnement d'exécution de l'application.

# Pourquoi utiliser un fichier docker-compose.yml ?

Un fichier docker-compose.yml permet de définir les services nécessaires à l'exécution de l'application.

# Pourquoi utiliser un fichier entrypoint.sh ?

Un fichier entrypoint.sh permet d'exécuter des commandes avant le lancement de l'application.

# Lancer l'application

```bash
   docker compose up --build -d
```
