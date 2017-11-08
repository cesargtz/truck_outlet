# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    truck_outlet_ids = fields.One2many('truck.outlet', 'contract_id', 'No de Contrato')

    
    @api.multi
    def truck_outlet(self):
        self.ensure_one()
        try:
            form_id = self.env['ir.model.data'].get_object_reference('truck_outlet', 'truck_outlet_form_view')[1]
        except ValueError:
            form_id = False

        ctx = dict()
        ctx.update({
            'default_contract_id': self.ids[0],
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'truck.outlet',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            #'target': 'new',
            'context': ctx,
        }