from datetime import datetime  # Add timezone import
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login_manager

class Utilisateur(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    date_inscription = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    reset_password = db.relationship('ResetPassword', backref='utilisateur', uselist=False)
    organisations = db.relationship('UtilisateurOrganisation', backref='utilisateur', lazy='dynamic')
    connecteurs = db.relationship('Connecteur', backref='utilisateur', lazy='dynamic')

    def set_mot_de_passe(self, mot_de_passe):
        self.mot_de_passe_hash = generate_password_hash(mot_de_passe)

    def check_mot_de_passe(self, mot_de_passe):
        return check_password_hash(self.mot_de_passe_hash, mot_de_passe)

class ResetPassword(db.Model):
    userid = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False, unique=True, primary_key=True)
    token = db.Column(db.String(200), nullable=False)
    expire = db.Column(db.DateTime, nullable=False)

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    rootid = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=True)
    utilisateurs = db.relationship('UtilisateurOrganisation', backref='organisation', lazy='dynamic')

    def delete_organisation(self):
        # Dissocier les utilisateurs de l'organisation
        for user in self.utilisateurs:
            db.session.delete(user)  # Dissocier l'organisation
        db.session.commit()  # Valider les changements

        # Supprimer l'organisation
        db.session.delete(self)
        db.session.commit()  # Valider la suppression

class UtilisateurOrganisation(db.Model):
    __tablename__ = 'utilisateur_organisation'
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), primary_key=True)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    organisationid = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    token = db.Column(db.String(200), nullable=False)
    expire = db.Column(db.DateTime, nullable=False)

class Connecteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    userid = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))