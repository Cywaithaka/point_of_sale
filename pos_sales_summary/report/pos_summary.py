# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more summary.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from openerp.osv import fields, osv
from openerp.report import report_sxw

class pos_summary(report_sxw.rml_parse):

    def _get_all_users(self):
        user_obj = self.pool.get('res.users')
        return user_obj.search(self.cr, self.uid, [])

    def _get_all_locations(self):
        location_obj = self.pool.get('stock.location')
        return location_obj.search(self.cr, self.uid, [])

    def _pos_sales_details(self, form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        #user_ids = form['user_ids'] or self._get_all_users()
        location_ids = form['location_ids'] or self._get_all_locations()

        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start2']),
                                                     ('date_order','<=',form['date_end2']),
                                                     ('location_id','in',location_ids),
                                                     #('state','in',['done','paid','invoiced']),
                                                     ('company_id','=',company_id)])
        for pos in pos_obj.browse(self.cr, self.uid, pos_ids):
            if pos.state in ['paid', 'done']:
                subtotal = pos.amount_subtotal,
                tax = pos.amount_tax,
                total = pos.amount_total,
            else:
                subtotal = tax = total = 0

            result = {
                'pos_name': pos.name,
                'date_order': pos.date_order,
                'subtotal': subtotal,
                'tax': tax,
                'total': total,
                'state': pos.state
            }
            data.append(result)
            if pos.state in ['done','paid']:
                #self.base += (pol.price_unit * pol.qty)
                self.subtotal += pos.amount_subtotal
                self.total += pos.amount_total
                #self.qty += pol.qty
        if data:
            return data
        else:
            return {}

    def _credit_sales_details(self, form):
        invoice_obj = self.pool.get('account.invoice')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        #user_ids = form['user_ids'] or self._get_all_users()
        location_ids = form['location_ids'] or self._get_all_locations()

        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        invoice_ids = invoice_obj.search(self.cr, self.uid, [('date_invoice','>=',form['date_start2']),
                                                     ('date_invoice','<=',form['date_end2']),
                                                     #('location_id','in',location_ids),
                                                     ('type','in',['out_invoice','out_refund']),
                                                     ('company_id','=',company_id)])

        for invoice in invoice_obj.browse(self.cr, self.uid, invoice_ids):
            if invoice.state in ['paid', 'done']:
                subtotal = invoice.amount_untaxed,
                tax = invoice.amount_tax,
                total = invoice.amount_total,
            else:
                subtotal = tax = total = 0

            result = {
                'pos_name': invoice.number,
                'date_order': invoice.date_invoice,
                'subtotal': subtotal,
                'tax': tax,
                'total': total,
                'state': invoice.state
            }
            data.append(result)
            if invoice.state in ['done','paid']:
                #self.base += (pol.price_unit * pol.qty)
                self.invoice_subtotal += invoice.amount_untaxed
                self.invoice_total += invoice.amount_total
                #self.qty += pol.qty
        if data:
            return data
        else:
            return {}

    def _pos_sales_summary(self, form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')

        location_ids = form['location_ids'] or self._get_all_locations()

        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start2']),
                                                     ('date_order','<=',form['date_end2']),
                                                     ('location_id','in',location_ids),
                                                     ('state','in',['done','paid']),
                                                     ('company_id','=',company_id)])
        for pos in pos_obj.browse(self.cr, self.uid, pos_ids):
            for pol in pos.lines:
                self.base += (pol.price_unit * pol.qty)
                self.subtotal += pol.price_subtotal
                self.total += pol.price_subtotal_incl
                self.qty += pol.qty
        self.discount = self.base - self.subtotal 
        return {}

    def _get_qty_total_2(self):
        return self.qty

    def _get_sales_total_2(self):
        return self.total

    def _get_sales_subtotal_2(self):
        return self.subtotal
    """
    def _get_sum_invoice_2(self, form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start2']),('date_order','<=',form['date_end2']),
                                                     ('user_id','in',user_ids),('company_id','=',company_id),('invoice_id','<>',False)])
        for pos in pos_obj.browse(self.cr, self.uid, pos_ids):
            for pol in pos.lines:
                self.total_invoiced += (pol.price_unit * pol.qty * (1 - (pol.discount) / 100.0))
        return self.total_invoiced or False
    """


    def _get_sum_discount(self, form):
        return self.discount

    def _get_payments(self, form):
        if not form['show_details']:
            self._pos_sales_summary(form)  #load totals as line details are not printed
        
        statement_line_obj = self.pool.get("account.bank.statement.line")
        pos_order_obj = self.pool.get("pos.order")
        location_ids = form['location_ids'] or self._get_all_locations()
        pos_ids = pos_order_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start2']),
                                                           ('date_order','<=',form['date_end2']),
                                                           ('state','in',['paid','invoiced','done']),
                                                           ('location_id','in',location_ids)])
        data=[]
        if pos_ids:
            st_line_ids = statement_line_obj.search(self.cr, self.uid, [('pos_statement_id', 'in', pos_ids)])
            if st_line_ids:
                st_id = statement_line_obj.browse(self.cr, self.uid, st_line_ids)
                a_l=[]
                for r in st_id:
                    a_l.append(r['id'])
                self.cr.execute("select aj.name,sum(amount), 0.0 sum2, absl.date fecha from account_bank_statement_line as absl,account_bank_statement as abs,account_journal as aj " \
                                "where absl.statement_id = abs.id and abs.journal_id = aj.id  and absl.id IN %s " \
                                "group by aj.name, absl.date order by absl.date",(tuple(a_l),))

                allRecords = self.cr.dictfetchall()
                if allRecords:
                    currentDate = allRecords[0]['fecha']
                    dayTotal = 0.0
                    for currentRecord in allRecords:
                        if currentRecord['fecha'] <> currentDate:
                            data.append({'name': 'TOTAL', 'fecha': '', 'sum': 0, 'sum2': dayTotal})
                            dayTotal = currentRecord['sum']
                            currentDate = currentRecord['fecha']
                        else:
                            dayTotal += currentRecord['sum']
                        data.append(currentRecord)
                    data.append({'name': 'TOTAL', 'fecha': '', 'sum': 0, 'sum2': dayTotal})
                    return data
        return {}
    """
    def _total_of_the_day(self, objects):
        if self.total:
             if self.total == self.total_invoiced:
                 return self.total
             else:
                 return ((self.total or 0.00) - (self.total_invoiced or 0.00))
        else:
            return False
    
    def _sum_invoice(self, objects):
        return reduce(lambda acc, obj:
                        acc + obj.invoice_id.amount_total,
                        [o for o in objects if o.invoice_id and o.invoice_id.number],
                        0.0)
    """

    def _ellipsis(self, orig_str, maxlen=100, ellipsis='...'):
        maxlen = maxlen - len(ellipsis)
        if maxlen <= 0:
            maxlen = 1
        new_str = orig_str[:maxlen]
        return new_str

    def _strip_name(self, name, maxlen=50):
        return self._ellipsis(name, maxlen, ' ...')
    
    """
    def _get_tax_amount(self, form):
        taxes = {}
        account_tax_obj = self.pool.get('account.tax')
        user_ids = form['user_ids'] or self._get_all_users()
        pos_order_obj = self.pool.get('pos.order')
        pos_ids = pos_order_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start2']),('date_order','<=',form['date_end2']),
                                                           ('state','in',['paid','invoiced','done']),('user_id','in',user_ids)])
        for order in pos_order_obj.browse(self.cr, self.uid, pos_ids):
            for line in order.lines:
                line_taxes = account_tax_obj.compute_all(self.cr, self.uid, line.product_id.taxes_id, line.price_unit, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                for tax in line_taxes['taxes']:
                    taxes.setdefault(tax['id'], {'name': tax['name'], 'amount':0.0})
                    taxes[tax['id']]['amount'] += tax['amount']
        return taxes.values()
    """
    
    def _get_tax_amount2(self):
        return self.total - self.subtotal

    def _get_credit_tax_amount2(self):
        return self.invoice_total - self.invoice_subtotal

    def _get_credit_sales_total_2(self):
        return self.invoice_total

    def _get_credit_sales_subtotal_2(self):
        return self.invoice_subtotal

    def _get_location_names(self, location_ids):
        location_obj = self.pool.get('stock.location')
        return ', '.join(map(lambda x: x.name, location_obj.browse(self.cr, self.uid, location_ids)))

    def __init__(self, cr, uid, name, context):
        super(pos_summary, self).__init__(cr, uid, name, context=context)

        self.base = 0.0
        self.subtotal = 0.0
        self.total = 0.0
        self.invoice_base = 0.0
        self.invoice_subtotal = 0.0
        self.invoice_total = 0.0
        self.qty = 0.0
        self.total_invoiced = 0.0
        self.discount = 0.0
        self.total_discount = 0.0
        self.localcontext.update({
            'time': time,
            'strip_name': self._strip_name,
            'getpayments': self._get_payments,
            'getsumdisc': self._get_sum_discount,
            #'gettotaloftheday': self._total_of_the_day,
            #'gettaxamount': self._get_tax_amount,
            'gettaxamount2': self._get_tax_amount2,
            'pos_sales_details':self._pos_sales_details,
            'credit_sales_details':self._credit_sales_details,
            'pos_sales_summary':self._pos_sales_summary,
            'getqtytotal2': self._get_qty_total_2,
            'getsalessubtotal2': self._get_sales_subtotal_2,
            'getsalestotal2': self._get_sales_total_2,
            #'getsuminvoice2':self._get_sum_invoice_2,
            'get_location_names': self._get_location_names,
            'getcreditsalessubtotal2': self._get_credit_sales_subtotal_2,
            'getcredittaxamount2': self._get_credit_tax_amount2,
            'getcreditsalestotal2': self._get_credit_sales_total_2,
        })


class report_pos_summary(osv.AbstractModel):
    _name = 'report.pos_sales_summary.report_summaryofsales'
    _inherit = 'report.abstract_report'
    _template = 'pos_sales_summary.report_summaryofsales'
    _wrapped_report_class = pos_summary

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
