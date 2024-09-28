from flask import render_template, redirect, request, url_for, flash
from flask_login import  current_user  
from app import app
from app.models import Connecteur, ResetPassword, Organisation, Utilisateur, UtilisateurOrganisation  
from datetime import datetime
from functools import wraps 


def login_not_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash('Vous êtes déjà connecté.', 'info')  
            return redirect(url_for('private'))  
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    """
    Décorateur pour vérifier si l'utilisateur a un rôle spécifié avant d'accéder à une fonction.
    Si l'utilisateur n'a pas le rôle spécifié, il est redirigé vers la page 'private' avec un message d'erreur.

    Args:
        allowed_roles (list): Liste des rôles autorisés à accéder à la fonction.

    Returns:
        function: La fonction décorée avec la vérification du rôle.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifie si le rôle de l'utilisateur courant est dans la liste des rôles autorisés
            if current_user.role not in allowed_roles:
                # Si le rôle n'est pas autorisé, affiche un message d'erreur et redirige vers la page 'private'
                flash('Vous n\'avez pas les droits nécessaires pour accéder à cette page.', 'error')
                return redirect(url_for('private'))
            # Si le rôle est autorisé, permet d'accéder à la fonction originale
            return f(*args, **kwargs)
        return decorated_function
    return decorator



def login_required_redirect(f): 
    """
    Décorateur pour vérifier si l'utilisateur est connecté avant d'accéder à une fonction.
    Si l'utilisateur n'est pas connecté, il est redirigé vers la page d'accueil avec un message d'erreur.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifie si l'utilisateur est connecté
        if not current_user.is_authenticated:
            # Si l'utilisateur n'est pas connecté, affiche un message d'erreur et redirige vers la page d'accueil
            flash('Vous devez être connecté', 'error') 
            return redirect(url_for('home'))  
        # Si l'utilisateur est connecté, permet d'accéder à la fonction originale
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/private')
@login_required_redirect 
def private():
    return render_template('account/private.html') 


@app.route('/settings')
@login_required_redirect  
def settings():
    organisations = Organisation.query.filter_by(rootid=current_user.id).all()
    return render_template('account/settings.html', organisations=organisations)  

@app.route('/forget_password')
@login_not_required  
def forget_password():
    return render_template('/forget_password.html')

@app.route('/set_forget_password')
@login_not_required
def set_forget_password():
    token = request.args.get('token')
    
    if not token:
        flash('Aucun token fourni. Redirection vers la page d\'accueil.', 'error')  
        return redirect('/')  

    # Vérifie le token dans la base de données
    reset_request = ResetPassword.query.filter_by(token=token).first()
    
    if reset_request and reset_request.expire > datetime.now():
        return render_template('/set_forget_password.html', token=token) 
    else:
        flash('Le token est expiré ou invalide.', 'error')  
        return redirect('/')  


@app.route("/create_orga")
@role_required(['admin', 'orga'])
@login_required_redirect
def create_orga():
    return render_template('/account/orga/create_orga.html')

@app.route("/manage_orga")
@role_required(['admin', 'orga'])
@login_required_redirect
def manage_orga():
    user_id = current_user.id
    organisations = Organisation.query.filter_by(rootid=user_id).all()
    
    return render_template('/account/orga/manage_orga.html', organisations=organisations)

@app.get("/edit_orga/<int:org_id>")
@role_required(['admin', 'orga'])
@login_required_redirect
def edit_orga(org_id):
    if not org_id:
        flash('Aucun ID d\'organisation fourni.', 'error')
        return redirect('/manage_orga') 
    
    organisation = Organisation.query.filter_by(id=org_id).first()
    if not organisation:
        flash('L\'organisation spécifiée n\'existe pas.', 'error')
        return redirect('/manage_orga')

    utilisateurs_associes = [
        {
            'id': utilisateur_organisation.utilisateur_id,
            'email': Utilisateur.query.get(utilisateur_organisation.utilisateur_id).email
        } 
        for utilisateur_organisation in UtilisateurOrganisation.query.filter_by(organisation_id=org_id).all()
        if utilisateur_organisation.utilisateur_id != current_user.id  
    ]
    
    return render_template('/account/orga/edit_orga.html', organisation=organisation, utilisateurs_associes=utilisateurs_associes)

@app.route("/manage_role")
@role_required(['admin'])
@login_required_redirect
def manage_role():
    utilisateurs = Utilisateur.query.order_by(Utilisateur.date_inscription.desc()).all()  
    utilisateurs_et_roles = [
        {
            'id': utilisateur.id,
            'email': utilisateur.email,
            'role': utilisateur.role,
            'actif': utilisateur.actif,
            'date_inscription': utilisateur.date_inscription
        } for utilisateur in utilisateurs
    ]
    return render_template('/account/admin/manage_role.html', utilisateurs_et_roles=utilisateurs_et_roles)

@app.route("/manage_connecteur")
@role_required(['admin'])
@login_required_redirect 
def manage_connecteur():
    """
    Cette fonction gère la page de gestion des connecteurs pour les utilisateurs avec le rôle 'admin'.
    Elle récupère tous les connecteurs associés à l'utilisateur actuel et les affiche dans une page HTML.
    """
    connecteurs = Connecteur.query.filter_by(userid=current_user.id).all()
    return render_template('/account/admin/manage_connecteur.html', connecteurs=connecteurs) 

@app.route("/manage_upload")
@role_required(['admin'])
@login_required_redirect 
def manage_upload():
    return render_template('/account/admin/manage_upload.html')