from datetime import datetime, timedelta
import os
import secrets
from urllib.parse import quote
from app.routes import role_required
from flask import flash, redirect, url_for, request
import re
from app import db
from flask_login import login_required
from app import app
from app.models import Connecteur, Invitation, Organisation, Utilisateur
from flask_login import current_user
from app.models import UtilisateurOrganisation
from flask_mail import Message
from app import mail
from werkzeug.utils import secure_filename

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

@app.route('/create_organisation', methods=['POST'])
@login_required
def create_organisation():
    nom = request.form['name']
    
    if Organisation.query.filter_by(nom=nom).first():
        flash("Le nom existe déjà.", "error")
        return redirect(url_for('create_orga'))
    
    if not (4 <= len(nom) <= 20) or not re.match(r'^[\w-]+$', nom):
        flash("Le nom doit être composé de 4 à 20 caractères, sans espaces, avec des chiffres, lettres, - ou _.", "error")
        return redirect(url_for('create_orga'))  

    new_org = Organisation(nom=nom, rootid=current_user.id) 
    db.session.add(new_org)
    db.session.commit()
    
    utilisateur_org = UtilisateurOrganisation(utilisateur_id=current_user.id, organisation_id=new_org.id)
    db.session.add(utilisateur_org)
    db.session.commit()  
    flash("Organisation créée avec succès.", "success")
    return redirect(url_for('manage_orga'))


@app.route('/edit_organisation/<int:org_id>', methods=['POST'])
@login_required
def edit_organisation(org_id):
    nom = request.form['name']
    
    org = Organisation.query.get(org_id)
    if not org:
        flash("Organisation non trouve.", "error")
        return redirect(url_for('manage_orga'))

    if Organisation.query.filter_by(nom=nom).first() and org.nom != nom:
        flash("Le nom existe déjà.", "error")
        return redirect(url_for('manage_orga'))
    
    if not (4 <= len(nom) <= 20) or not re.match(r'^[\w-]+$', nom):
        flash("Le nom doit être composé de 4 à 20 caractères, sans espaces, avec des chiffres, lettres, - ou _.", "error")
        return redirect(url_for('manage_orga'))  

    org.nom = nom 
    db.session.commit()
    flash("Organisation mise à jour avec succès.", "success")
    return redirect(url_for('manage_orga'))

@app.route('/delete_organisation/<int:org_id>')
@login_required
def delete_organisation(org_id):
    org = Organisation.query.get(org_id)
    if not org:
        flash("Organisation non trouvée.", "error")
        return redirect(url_for('manage_orga'))
    
    UtilisateurOrganisation.query.filter_by(organisation_id=org.id).delete()
    
    db.session.delete(org)
    db.session.commit()
    flash("Organisation supprimée avec succès.", "success")
    return redirect(url_for('manage_orga'))

@app.route('/invite_user_to_orga/<int:org_id>', methods=['POST'])
@login_required
def invite_user_to_orga(org_id):
    email = request.form['email']
    token = secrets.token_urlsafe(16)

    user = Utilisateur.query.filter_by(email=email).first()
    if not user:
        flash("Utilisateur non trouvé.", "error")
        return redirect(url_for('edit_orga', org_id=org_id))
    
    org = Organisation.query.get(org_id)
    if not org:
        flash("Organisation non trouvée.", "error")
        return redirect(url_for('edit_orga', org_id=org_id))
    
    existing_association = UtilisateurOrganisation.query.filter_by(utilisateur_id=user.id, organisation_id=org.id).first()
    if existing_association:
        flash("L'utilisateur est déjà associé / invité.", "info")
        return redirect(url_for('edit_orga', org_id=org_id))
    
    msg = Message(
        subject='Invitation à particitper a une organisation',
        recipients=[email], 
        html=f"Cliquez sur le lien pour valider votre invitation <a href='{app.config['BASE_URL']}/valid_invite_orga?token={quote(token)}'>Valider</a>"
    )

    try:
        mail.send(msg)
        flash('L\'invitation a été envoyé', category='success')
    except Exception as e:
        flash('Erreur lors de l\'envoi de l\'invitation', category='error')

    invitation = Invitation(
        userid=user.id,
        organisationid=org.id,
        token=token,
        expire=datetime.now() + timedelta(days=30)
    )
    db.session.add(invitation)
    db.session.commit()

    return redirect(url_for('edit_orga', org_id=org_id))


@app.route('/valid_invite_orga')
@login_required
def valid_invite_orga():
    token = request.args.get('token')
    invitation = Invitation.query.filter_by(token=token).first()

    if not invitation or invitation.expire < datetime.now():
        flash("L'invitation est invalide ou a expiré.", "error")
        return redirect(url_for('home'))
    user_id = invitation.userid
    user = Utilisateur.query.get(user_id)
    if not user:
        flash("L'utilisateur invité n'existe pas.", "error")
        return redirect(url_for('home'))
    # Check if the association already exists
    existing_association = UtilisateurOrganisation.query.filter_by(
        utilisateur_id=user.id,
        organisation_id=invitation.organisationid
    ).first()

    if not existing_association: 
        utilisateur_org = UtilisateurOrganisation(
            utilisateur_id=user.id,
            organisation_id=invitation.organisationid
        )
        db.session.add(utilisateur_org)

    db.session.delete(invitation)
    db.session.commit()
    
    flash("Invitation acceptée avec succès.", "success")
    return redirect(url_for('home'))

@app.route('/delete_user_orga')
@login_required
def delete_user_orga():
    org_id = request.args.get('org_id')
    user_id = request.args.get('user_id')
    
    if not org_id or not user_id:
        flash('Aucun ID d\'organisation ou d\'utilisateur fourni.', 'error')
        return redirect(url_for('home'))
    
    association = UtilisateurOrganisation.query.filter_by(
        utilisateur_id=user_id,
        organisation_id=org_id
    ).first()
    
    if not association:
        flash('L\'association utilisateur-organisation spécifiée n\'existe pas.', 'error')
        return redirect(url_for('home'))
    
    db.session.delete(association)
    db.session.commit()
    
    flash('Association utilisateur-organisation supprimée avec succès.', 'success')
    return redirect(url_for('edit_orga', org_id=org_id))

@app.route('/update_role/<int:utilisateur_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def update_role(utilisateur_id):
    role = request.form['role']
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur:
        flash('Utilisateur non trouvé.', 'error')
        return redirect(url_for('manage_role'))
    utilisateur.role = role
    db.session.commit()
    flash('Role mis à jour avec succès.', 'success')
    return redirect(url_for('manage_role'))

@app.route('/update_status/<int:utilisateur_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def update_status(utilisateur_id):
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur:
        flash('Utilisateur non trouvé.', 'error')
        return redirect(url_for('manage_role'))
    
    # Inverser l'état de 'actif'
    utilisateur.actif = not utilisateur.actif
    db.session.commit()
    flash(f'Statut de l\'utilisateur mis à jour : {"actif" if utilisateur.actif else "inactif"}', 'success')
    return redirect(url_for('manage_role'))

@app.route('/add_connecteur', methods=['POST'])
@login_required
@role_required(['admin'])
def add_connecteur():
    name = request.form['name']
    type = request.form['type']
    details = request.form['details']

    # Vérifier si les champs sont vides
    if not name or not type or not details:
        flash('Tous les champs doivent être remplis.', 'error')
        return redirect(url_for('manage_connecteur'))

    new_connecteur = Connecteur(
        name=name,
        type=type,
        details=details,
        userid=current_user.id
    )
    
    try:
        db.session.add(new_connecteur)
        db.session.commit()
        flash('Connecteur ajouté avec succès.', 'success')
    except Exception as e:
        db.session.rollback()  # Annuler la session en cas d'erreur
        flash('Erreur lors de l\'ajout du connecteur : ' + str(e), 'error')
    
    return redirect(url_for('manage_connecteur'))

@app.route('/delete_connecteur/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def delete_connecteur(id):
    connecteur = Connecteur.query.get(id)
    if not connecteur:
        flash('Connecteur non trouvé.', 'error')
        return redirect(url_for('manage_connecteur'))
    db.session.delete(connecteur)
    db.session.commit()
    flash('Connecteur supprimé avec succès.', 'success')
    return redirect(url_for('manage_connecteur'))

@app.route('/upload_file_form', methods=['POST'])
@login_required
@role_required(['admin'])
def upload_file_form():
    if 'files' not in request.files:
        flash('Aucun fichier fourni.', 'error')
        return redirect(url_for('manage_upload'))
    
    files = request.files.getlist('files')
    for file in files:
        if file.filename == '':
            flash('Aucun fichier sélectionné.', 'error')
            return redirect(url_for('manage_upload'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Nettoyer le nom de fichier
            cleaned_filename = clean_filename(filename)
            # Ajouter un timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"{timestamp}_{cleaned_filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_filename))
    
    flash('Fichiers uploadés avec succès.', 'success')
    return redirect(url_for('manage_upload'))

