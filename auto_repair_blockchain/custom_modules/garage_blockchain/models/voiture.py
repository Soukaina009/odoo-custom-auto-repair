from odoo import models, fields, api, exceptions
from datetime import date

class Voiture(models.Model):
    _name = 'garage_blockchain.voiture'
    _description = "Voiture"
    _order = 'name'

    name = fields.Char(string="Référence", compute='_compute_name', store=True)
    marque = fields.Char(string="Marque", required=True)
    modele = fields.Char(string="Modèle")
    annee = fields.Integer(string="Année")
    proprietaire = fields.Char(string="Propriétaire", required=True)
    telephone_proprietaire = fields.Char(string="Téléphone")
    email_proprietaire = fields.Char(string="Email")
    immatriculation = fields.Char(string="Immatriculation")  # Unicité gérée par contrainte Python
    kilometrage = fields.Integer(string="Kilométrage")
    couleur = fields.Char(string="Couleur")
    vin = fields.Char(string="Numéro VIN")
    date_mise_circulation = fields.Date(string="Mise en circulation")
    reparation_ids = fields.One2many('garage_blockchain.reparation', 'voiture_id', string="Réparations")
    nombre_reparations = fields.Integer(string="Nombre réparations", compute='_compute_stats', store=True)
    cout_total_reparations = fields.Float(string="Coût total", compute='_compute_stats', store=True)
    derniere_reparation = fields.Date(string="Dernière réparation", compute='_compute_stats', store=True)
    mecanicien_ids = fields.Many2many('hr.employee', string="Mécaniciens", compute='_compute_mecaniciens', store=False)
    state = fields.Selection([
        ('attente', 'En attente'),
        ('reparation', 'En réparation'),
        ('termine', 'Terminée'),
        ('livre', 'Livrée')
    ], string="État", default='attente')
    notes = fields.Text(string="Notes")


    @api.depends('marque', 'immatriculation')
    def _compute_name(self):
        for record in self:
            if record.immatriculation:
                record.name = f"{record.marque} - {record.immatriculation}"
            else:
                record.name = record.marque or "Nouvelle voiture"

    @api.depends('reparation_ids', 'reparation_ids.cout_total', 'reparation_ids.date_debut')
    def _compute_stats(self):
        for record in self:
            record.nombre_reparations = len(record.reparation_ids)
            record.cout_total_reparations = sum(record.reparation_ids.mapped('cout_total'))
            if record.reparation_ids:
                dates = [r.date_debut for r in record.reparation_ids if r.date_debut]
                record.derniere_reparation = max(dates) if dates else False
            else:
                record.derniere_reparation = False

    @api.depends('reparation_ids.mecanicien_id')
    def _compute_mecaniciens(self):
        for record in self:
            record.mecanicien_ids = record.reparation_ids.mapped('mecanicien_id')

    @api.constrains('annee')
    def _check_annee(self):
        """Validation de l'année"""
        for record in self:
            if record.annee:
                annee_actuelle = date.today().year
                if record.annee < 1900 or record.annee > annee_actuelle + 1:
                    raise exceptions.ValidationError(
                        f"L'année doit être entre 1900 et {annee_actuelle + 1}!"
                    )
