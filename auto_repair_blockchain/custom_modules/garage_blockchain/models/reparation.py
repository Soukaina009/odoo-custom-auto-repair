from odoo import models, fields, api, exceptions
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class Reparation(models.Model):
    _name = 'mecanicien_v2.reparation'
    _description = "Réparation"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # ← AJOUTER CETTE LIGNE
    _order = 'date_debut desc'

    name = fields.Char(string="Référence", compute='_compute_name', store=True)
    mecanicien_id = fields.Many2one(
        'hr.employee', 
        string="Mécanicien", 
        required=True, 
        domain="[('is_mecanicien', '=', True)]"
    )
    voiture_id = fields.Many2one('mecanicien_v2.voiture', string="Voiture", required=True)
    date_debut = fields.Datetime(string="Date début", required=True, default=fields.Datetime.now)
    date_fin = fields.Datetime(string="Date fin")
    duree = fields.Float(string="Durée (heures)", compute='_compute_duree', store=True)
    type_reparation = fields.Selection([
        ('revision', 'Révision'),
        ('reparation', 'Réparation'),
        ('diagnostic', 'Diagnostic'),
        ('entretien', 'Entretien'),
        ('autre', 'Autre')
    ], string="Type", required=True, default='reparation')
    description = fields.Text(string="Description", required=True)
    pieces_utilisees = fields.Text(string="Pièces utilisées")
    cout_pieces = fields.Float(string="Coût pièces", default=0.0)
    cout_main_oeuvre = fields.Float(string="Coût main d'œuvre", default=0.0)
    cout_total = fields.Float(string="Coût total", compute='_compute_cout_total', store=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    kilometrage_intervention = fields.Integer(string="Kilométrage")
    priorite = fields.Selection([
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente')
    ], string="Priorité", default='normale')
    state = fields.Selection([
        ('planifie', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminée'),
        ('facture', 'Facturée'),
        ('annule', 'Annulée')
    ], string="État", default='planifie', tracking=True)
    facture = fields.Boolean(string="Facturée", default=False)
    notes_techniques = fields.Text(string="Notes techniques")
    satisfaction_client = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐')
    ], string="Satisfaction client")

    # ── Champs Blockchain ─────────────────────────────────────────
    blockchain_tx = fields.Char(
        string="Transaction Blockchain",
        readonly=True,
        copy=False,
        help="Hash de la transaction sur Polygon Amoy Testnet",
    )
    blockchain_hash = fields.Char(
        string="Hash données",
        readonly=True,
        copy=False,
        help="SHA-256 des données de la réparation enregistré sur la blockchain",
    )
    blockchain_url = fields.Char(
        string="Lien Explorateur",
        compute='_compute_blockchain_url',
        store=False,
    )

    def _compute_blockchain_url(self):
        for record in self:
            if record.blockchain_tx:
                record.blockchain_url = (
                    f"https://sepolia.etherscan.io/tx/{record.blockchain_tx}"
                )
            else:
                record.blockchain_url = False

    @api.depends('voiture_id', 'voiture_id.name', 'date_debut')
    def _compute_name(self):
        for record in self:
            if record.voiture_id and record.date_debut:
                date_str = fields.Datetime.to_string(record.date_debut)[:10]
                record.name = f"{record.voiture_id.name} - {date_str}"
            else:
                record.name = "Nouvelle réparation"

    @api.depends('cout_pieces', 'cout_main_oeuvre')
    def _compute_cout_total(self):
        for record in self:
            record.cout_total = (record.cout_pieces or 0.0) + (record.cout_main_oeuvre or 0.0)

    @api.depends('date_debut', 'date_fin')
    def _compute_duree(self):
        for record in self:
            if record.date_debut and record.date_fin:
                delta = record.date_fin - record.date_debut
                record.duree = delta.total_seconds() / 3600
            else:
                record.duree = 0.0

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_fin and record.date_debut and record.date_fin < record.date_debut:
                raise exceptions.ValidationError("La date de fin doit être après la date de début!")

    @api.constrains('mecanicien_id')
    def _check_mecanicien(self):
        for record in self:
            if record.mecanicien_id and not record.mecanicien_id.is_mecanicien:
                raise exceptions.ValidationError(
                    "Seuls les employés avec 'Est mécanicien' peuvent être assignés!"
                )

    @api.constrains('cout_pieces', 'cout_main_oeuvre')
    def _check_couts(self):
        """Validation des coûts (pas de valeurs négatives)"""
        for record in self:
            if record.cout_pieces < 0:
                raise exceptions.ValidationError("Le coût des pièces ne peut pas être négatif!")
            if record.cout_main_oeuvre < 0:
                raise exceptions.ValidationError("Le coût de la main d'œuvre ne peut pas être négatif!")

    def action_start(self):
        """Démarre la réparation"""
        self.ensure_one()
        if self.state != 'planifie':
            raise exceptions.UserError("Seule une réparation planifiée peut être démarrée!")
        self.write({
            'state': 'en_cours',
            'date_debut': fields.Datetime.now()
        })
        if self.voiture_id:
            self.voiture_id.write({'state': 'reparation'})
        return True

    def action_complete(self):
        """Termine la réparation"""
        self.ensure_one()
        if self.state != 'en_cours':
            raise exceptions.UserError("Seule une réparation en cours peut être terminée!")
        self.write({
            'state': 'termine',
            'date_fin': fields.Datetime.now()
        })
        if self.voiture_id:
            self.voiture_id.write({'state': 'termine'})
        return True

    def action_invoice(self):
        """Marque la réparation comme facturée"""
        self.ensure_one()
        if self.state != 'termine':
            raise exceptions.UserError("Seule une réparation terminée peut être facturée!")
        self.write({
            'state': 'facture',
            'facture': True,
        })
        return True

    def action_cancel(self):
        """Annule la réparation"""
        self.ensure_one()
        if self.state in ('termine', 'facture'):
            raise exceptions.UserError("Une réparation terminée ou facturée ne peut pas être annulée!")
        self.write({'state': 'annule'})
        if self.voiture_id:
            self.voiture_id.write({'state': 'disponible'})
        return True

    # ── Action Blockchain ─────────────────────────────────────────
    def action_blockchain_transfer(self):
        """
        Enregistre une preuve d'immuabilité de la réparation sur la
        blockchain Polygon Amoy Testnet via le smart contract GarageRegistry.
        """
        self.ensure_one()

        if self.blockchain_tx:
            raise exceptions.UserError(
                "Cette réparation a déjà été enregistrée sur la blockchain!\n"
                f"TX : {self.blockchain_tx}"
            )

        if self.state not in ('termine', 'facture'):
            raise exceptions.UserError(
                "Seule une réparation terminée ou facturée peut être "
                "enregistrée sur la blockchain."
            )

        try:
            from ..blockchain.blockchain_service import (
                compute_reparation_hash,
                enregistrer_sur_blockchain,
            )
        except ImportError as exc:
            raise exceptions.UserError(
                "Bibliothèques blockchain manquantes.\n"
                "Installez-les avec : pip install web3 python-dotenv\n\n"
                f"Détail : {exc}"
            ) from exc

        # 1. Calculer le hash des données de la réparation
        data_hash = compute_reparation_hash(self)
        _logger.info(
            "Blockchain — hash calculé pour réparation #%s : %s",
            self.id, data_hash,
        )

        # 2. Envoyer la transaction au smart contract
        try:
            tx_hash = enregistrer_sur_blockchain(self.id, data_hash)
        except EnvironmentError as exc:
            raise exceptions.UserError(
                "Configuration blockchain incomplète.\n"
                f"Détail : {exc}"
            ) from exc
        except ConnectionError as exc:
            raise exceptions.UserError(
                "Impossible de se connecter au réseau blockchain.\n"
                f"Détail : {exc}"
            ) from exc
        except Exception as exc:
            _logger.exception("Erreur lors de la transaction blockchain")
            raise exceptions.UserError(
                "Erreur lors de l'enregistrement sur la blockchain.\n"
                f"Détail : {exc}"
            ) from exc

        # 3. Sauvegarder le résultat
        self.write({
            'blockchain_tx': tx_hash,
            'blockchain_hash': data_hash,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Blockchain',
                'message': f'Réparation enregistrée avec succès !\nTX : {tx_hash}',
                'type': 'success',
                'sticky': True,
            },
        }