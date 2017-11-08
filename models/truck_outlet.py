# -*- coding: utf-8 -*-

from openerp import api, fields, models, api
import json
import requests

class TruckOutlet(models.Model):
    _inherit = ['truck', 'vehicle.outlet', 'mail.thread']
    _name = 'truck.outlet'


    name = fields.Char('Truck outlet reference', required=True, select=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('reg_code_to'), help="Unique number of the Truck outlet")
    state = fields.Selection([
        ('analysis', 'Analisis'),
        ('weight_input', 'Entrada den Peso'),
        ('loading', 'Cargando'),
        ('weight_output', 'Salida de Peso'),
        ('done', 'Hecho'),
    ], default='analysis')


    @api.one
    def truck_reception_stats_sensor_update(self):
        url = 'http://nvryecora.ddns.net:8080'
        response = requests.get(url)
        json_data = json.loads(response.text)
        self.humidity_rate = float(json_data['humedad'].strip())
        self.density = float(json_data['densidad'].strip())
        self.temperature = float(json_data['temperatura'].strip())

    @api.one
    def weight_update(self):
        url = 'http://nvryecora.ddns.net:8081'
        response = requests.get(url)
        json_data = json.loads(response.text)
        self.input_kilos = float(json_data['peso_entrada'])
        self.output_kilos = float(json_data['peso_salida'])
        self.raw_kilos = float(json_data['peso_neto'])

    @api.one
    @api.depends('contract_id')
    def _compute_product_id(self):
        product_id = False
        for line in self.contract_id.order_line:
            product_id = line.product_id.id
            break
        self.product_id = product_id

    @api.one
    @api.depends('input_kilos', 'output_kilos')
    def _compute_raw_kilos(self):
        self.raw_kilos = self.output_kilos -self.input_kilos

    @api.one
    @api.depends('contract_id', 'raw_kilos')
    def _compute_delivered(self):
        self.delivered = sum(record.raw_kilos for record in self.contract_id.truck_outlet_ids) / 1000

    @api.one
    def fun_load(self):
        self.state = 'weight_output'

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'analysis':
                self.write({'state': 'weight_input'}, 'r')
            elif self.state == 'weight_input':
                self.write({'state': 'loading'}, 'r')
            elif self.state == 'loading':
                self.write({'state': 'weight_output'}, 'r')
            elif self.state == 'weight_output':
                self.write({'state': 'done'}, 'r')

        res = super(TruckOutlet, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals['state'] = 'weight_input'
        res = super(TruckOutlet, self).create(vals)
        return res
