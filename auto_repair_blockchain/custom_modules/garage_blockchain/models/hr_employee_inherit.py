from odoo import models, fields, api, exceptions

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    is_mecanicien = fields.Boolean(string="Est mécanicien", default=False)
    specialite = fields.Char(string="Spécialité")
    certifications = fields.Text(string="Certifications")
    niveau_experience = fields.Selection([
        ('junior', 'Junior'),
        ('confirme', 'Confirmé'),
        ('senior', 'Senior'),
        ('expert', 'Expert')
    ], string="Niveau d'expérience")
    date_embauche_atelier = fields.Date(string="Date d'embauche atelier")
    reparation_ids = fields.One2many(
        'garage_blockchain.reparation', 
        'mecanicien_id', 
        string="Réparations",
        domain="[('mecanicien_id', '=', id)]"
    )
    nombre_reparations = fields.Integer(
        string="Nombre de réparations", 
        compute='_compute_stats',
        store=True
    )
    total_revenus_reparations = fields.Float(
        string="Total revenus", 
        compute='_compute_stats',
        store=True
    )

    @api.depends('reparation_ids', 'reparation_ids.cout_total')
    def _compute_stats(self):
        for record in self:
            record.nombre_reparations = len(record.reparation_ids)
            record.total_revenus_reparations = sum(record.reparation_ids.mapped('cout_total'))

    @api.constrains('is_mecanicien', 'specialite', 'certifications', 'niveau_experience', 'date_embauche_atelier')
    def _check_mecanicien_fields(self):
        for record in self:
            if not record.is_mecanicien and (
                record.specialite or record.certifications or record.niveau_experience or record.date_embauche_atelier
            ):
                raise exceptions.ValidationError(
                    "Les champs spécifiques au mécanicien doivent être vides si 'Est mécanicien' n'est pas coché."
                )

    @api.onchange('is_mecanicien')
    def _onchange_is_mecanicien(self):
        if not self.is_mecanicien:
            self.specialite = False
            self.certifications = False
            self.niveau_experience = False
            self.date_embauche_atelier = False

    @api.model
    def mecanicien_domain(self):
        return [('is_mecanicien', '=', True)]
