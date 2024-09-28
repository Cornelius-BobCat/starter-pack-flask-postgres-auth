from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user  # Add this import
from app import app, db
from app.models import  Utilisateur
from flask_mail import Mail, Message
import secrets
from datetime import datetime, timedelta
from app.models import ResetPassword 
from urllib.parse import quote  # Ajoutez cette importation

mail = Mail()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Cette fonction gère le processus de connexion.
    Elle vérifie si l'utilisateur existe et si le mot de passe est correct.
    Si la connexion est réussie, elle redirige vers la page privée.
    Si la connexion échoue, elle affiche un message d'erreur.
    """
    email = '' 
    if request.method == 'POST':
        email = request.form['email'] 
        mot_de_passe = request.form['password']
        utilisateur = Utilisateur.query.filter_by(email=email).first()
        if utilisateur:
            if not utilisateur.actif:  # Vérification si le compte est désactivé
                flash('Votre compte est désactivé', category='info')
                return redirect(url_for('login'))  # Redirection vers la page de connexion
            if utilisateur.check_mot_de_passe(mot_de_passe):
                login_user(utilisateur)
                flash('Connexion réussie', category='success')
                return redirect(url_for('private'))
        flash('Email ou mot de passe incorrect', category='error')
    return render_template('login.html', email=email)  

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Cette fonction gère le processus d'inscription.
    Elle vérifie si l'email n'est pas déjà utilisé, si le mot de passe répond aux exigences et si les mots de passe correspondent.
    Si l'inscription est réussie, elle redirige vers la page de connexion.
    Si l'inscription échoue, elle affiche un message d'erreur.
    """
    email = '' 
    if request.method == 'POST':
        email = request.form['email'] 
        mot_de_passe = request.form['password']
        confirm_mot_de_passe = request.form['confirm_password']
        
        if len(mot_de_passe) < 5 or len(confirm_mot_de_passe) < 5 or not any(c.isdigit() for c in mot_de_passe) or not any(c.isalpha() for c in mot_de_passe):
            flash('Le mot de passe doit contenir au moins 5 caractères, incluant des lettres et des chiffres.', category='error')
        elif mot_de_passe != confirm_mot_de_passe:
            flash('Les mots de passe ne correspondent pas.', category='error')
        else:
            utilisateur = Utilisateur.query.filter_by(email=email).first()
            if utilisateur:
                flash('Cet email est déjà utilisé', category='error')
            else:
                role = "basic" 
                nouvel_utilisateur = Utilisateur(email=email, role=role)  
                nouvel_utilisateur.set_mot_de_passe(mot_de_passe)
                db.session.add(nouvel_utilisateur)
                db.session.commit()
                flash('Inscription réussie, vous pouvez vous connecter', category='success')
                return redirect(url_for('login'))
    return render_template('register.html', email=email) 

@app.route('/logout')
@login_required
def logout():
    """
    Cette fonction gère la déconnexion de l'utilisateur.
    Elle utilise la fonction logout_user() de Flask-Login pour déconnecter l'utilisateur actuel.
    Après la déconnexion, l'utilisateur est redirigé vers la page d'accueil.
    """
    logout_user()
    return redirect(url_for('home'))

@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    """
    Cette fonction gère la mise à jour du mot de passe de l'utilisateur.
    Elle vérifie si l'ancien mot de passe est correct, si les nouveaux mots de passe correspondent et si le nouveau mot de passe répond aux exigences.
    Si la mise à jour est réussie, elle redirige vers la page des paramètres.
    Si la mise à jour échoue, elle affiche un message d'erreur.
    """
    old_password = request.form['old_password']  # Récupération de l'ancien mot de passe
    new_password = request.form['new_password']  # Récupération du nouveau mot de passe
    confirm_new_password = request.form['confirm_password']  # Récupération de la confirmation du nouveau mot de passe
    utilisateur = Utilisateur.query.filter_by(email=current_user.email).first()  # Recherche de l'utilisateur par son email
    
    # Vérification de l'ancien mot de passe et de la correspondance des nouveaux mots de passe
    if utilisateur and utilisateur.check_mot_de_passe(old_password):
        if new_password == confirm_new_password:
            # Vérification des exigences du mot de passe (longueur, lettres et chiffres)
            if len(new_password) < 5 or len(confirm_new_password) < 5 or not any(c.isdigit() for c in new_password) or not any(c.isalpha() for c in new_password):
                flash('Le mot de passe doit contenir au moins 5 caractères, incluant des lettres et des chiffres.', category='error')
            else:
                utilisateur.set_mot_de_passe(new_password)  # Mise à jour du mot de passe
                db.session.commit()  # Sauvegarde des changements dans la base de données
                flash('Mot de passe mis à jour', category='success')
                return redirect(url_for('settings'))  # Redirection vers la page des paramètres
        else:
            flash('Les nouveaux mots de passe ne correspondent pas', category='error')
    else:
        flash('Ancien mot de passe incorrect', category='error')
    
    return redirect(url_for('settings'))  # Redirection vers la page des paramètres en cas d'erreur



@app.route('/forget_password_backend', methods=['POST'])
def forget_password_backend():
    """
    Cette fonction gère la réinitialisation du mot de passe via le backend.
    Elle récupère le token, le nouveau mot de passe et sa confirmation depuis le formulaire.
    Elle vérifie si le token est valide, si les nouveaux mots de passe correspondent et si le nouveau mot de passe répond aux exigences.
    Si la réinitialisation est réussie, elle redirige vers la page de connexion.
    Si la réinitialisation échoue, elle affiche un message d'erreur.
    """
    # Récupération du token, du nouveau mot de passe et de sa confirmation depuis le formulaire
    token = request.form['token']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_password']
    
    # Recherche de l'utilisateur par son token de réinitialisation de mot de passe
    utilisateur = ResetPassword.query.filter_by(token=token).first() 
    if utilisateur:
        # Recherche de l'utilisateur par son ID
        utilisateur_id = utilisateur.userid
        utilisateur = Utilisateur.query.filter_by(id=utilisateur_id).first()
        if utilisateur:
            # Vérification de la correspondance des nouveaux mots de passe
            if new_password == confirm_new_password:
                # Vérification des exigences du mot de passe (longueur, lettres et chiffres)
                if len(new_password) < 5 or not any(c.isdigit() for c in new_password) or not any(c.isalpha() for c in new_password):
                    flash('Le mot de passe doit contenir au moins 5 caractères, incluant des lettres et des chiffres.', category='error')
                else:
                    # Mise à jour du mot de passe de l'utilisateur
                    utilisateur.set_mot_de_passe(new_password)
                    db.session.commit()
                    flash('Mot de passe mis à jour', category='success')
                    try:
                        # Suppression du token de réinitialisation du mot de passe
                        db.session.delete(utilisateur.reset_password)
                        db.session.commit()
                    except Exception as e:
                        flash('Une erreur mineure est survenue', category='info')

                    return redirect(url_for('login'))
            else:
                flash('Les nouveaux mots de passe ne correspondent pas', category='error')
        else:
            flash('Token invalide', category='error')  
    else:
        flash('Token invalide', category='error')  
    return redirect(url_for('forget_password'))
@app.route('/forget_password_mail', methods=['POST'])
def forget_password_mail():
    """
    Cette fonction gère l'envoi d'un email pour la réinitialisation du mot de passe.
    Elle récupère l'email de l'utilisateur depuis le formulaire, vérifie si l'email existe dans la base de données,
    génère ou met à jour un token de réinitialisation du mot de passe, et envoie un email avec un lien de réinitialisation.
    """
    # Récupération de l'email de l'utilisateur depuis le formulaire
    email = request.form['email']
    # Recherche de l'utilisateur par son email
    utilisateur = Utilisateur.query.filter_by(email=email).first()
    if not utilisateur:
        # Si l'email n'existe pas, afficher un message d'erreur et rediriger vers la page de réinitialisation du mot de passe
        flash('Le mail n\'existe pas', category='error')
        return redirect(url_for('forget_password'))
    else:
        # Recherche du token de réinitialisation du mot de passe associé à l'utilisateur
        reset_password = ResetPassword.query.filter_by(userid=utilisateur.id).first()
        if reset_password:
            # Si le token existe déjà, le mettre à jour avec un nouveau token et une nouvelle date d'expiration
            reset_password.token = secrets.token_urlsafe(16)
            reset_password.expire = datetime.now() + timedelta(minutes=15)
        else:
            # Si le token n'existe pas, en créer un nouveau avec un token et une date d'expiration
            reset_password = ResetPassword(userid=utilisateur.id, token=secrets.token_urlsafe(16), expire=datetime.now() + timedelta(minutes=15))
        
        # Ajouter ou mettre à jour le token de réinitialisation du mot de passe dans la base de données
        db.session.add(reset_password)
        db.session.commit()

        # Création du message email avec le lien de réinitialisation du mot de passe
        msg = Message(
            subject='Réinitialisation du mot de passe',
            recipients=[email], 
            html=f"Cliquez sur le lien pour réinitialiser votre mot de passe <a href='{app.config['BASE_URL']}/set_forget_password?token={quote(reset_password.token)}'>Réinitialiser</a>"
        )

        try:
            # Envoi du message email
            mail.send(msg)
            flash('Un email a été envoyé à votre adresse email', category='success')
        except Exception as e:
            # Gestion de l'erreur en cas d'échec de l'envoi de l'email
            flash('Erreur lors de l\'envoi de l\'email', category='error')
        
        # Redirection vers la page d'accueil après l'envoi de l'email
        return redirect(url_for('home'))