# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class pos_session(osv.osv):
    _inherit = 'pos.session'

    def _compute_cash_all(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict()

        for record in self.browse(cr, uid, ids, context=context):
            result[record.id] = {
                'cash_journal_id' : False,
                'cash_register_id' : False,
                'cash_control' : False,
            }
            for st in record.statement_ids:
                if st.journal_id.cash_control == True:
                    if st.journal_id.currency and st.journal_id.currency.name == 'CRC':
                        result[record.id]['cash_control'] = True
                        result[record.id]['crc_cash_journal_id'] = st.journal_id.id
                        result[record.id]['crc_cash_register_id'] = st.id
                    else:
                        result[record.id]['cash_control'] = True
                        result[record.id]['cash_journal_id'] = st.journal_id.id
                        result[record.id]['cash_register_id'] = st.id

        return result

    def register_deposit(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if not ids:
            return {}

        move_pool = self.pool.get('account.move')
        move_line_proxy = self.pool.get('account.move.line')
        period_pool = self.pool.get('account.period')
        receiptDate = fields.date.context_today(self, cr, uid, context=context)
        search_periods = period_pool.find(cr, uid, receiptDate, context=context)
        period_id = search_periods[0]

        for record in self.browse(cr, uid, ids, context=context):
            if record.crc_cash_register_balance_end_real:
                line_ids = []
                name = _('Salida x Deposito a ') + record.crc_journal_id.name
                debit_line = (0, 0, {
                    'name': name,
                    'date': receiptDate,
                    #'partner_id': partner_id,
                    'account_id': record.crc_cash_journal_id.default_debit_account_id.id,
                    'journal_id': record.crc_cash_journal_id.id,
                    'period_id': period_id,
                    'debit': record.crc_cash_register_balance_end_real,
                    'credit': 0.0,
                    #'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    #'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    #'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                line_ids.append(debit_line)

                credit_line = (0, 0, {
                    'name': name,
                    'date': receiptDate,
                    #'partner_id': partner_id,
                    'account_id': record.crc_journal_id.default_credit_account_id.id,
                    'journal_id': record.crc_cash_journal_id.id,
                    'period_id': period_id,
                    'credit': record.crc_cash_register_balance_end_real,
                    'debit': 0.0,
                    #'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    #'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    #'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                line_ids.append(credit_line)
                move = {
                    'narration': name,
                    'date': receiptDate,
                    'ref': record.name,
                    'journal_id': record.crc_cash_journal_id.id,
                    'line_id': line_ids,
                    'period_id': period_id,
                }
                move_id = move_pool.create(cr, uid, move, context=context)

            if record.usd_cash_register_balance_end_real:
                line_ids = []
                name = _('Salida x Deposito a ') + record.usd_journal_id.name
                debit_line = (0, 0, {
                    'name': name,
                    'date': receiptDate,
                    #'partner_id': partner_id,
                    'account_id': record.cash_journal_id.default_debit_account_id.id,
                    'journal_id': record.cash_journal_id.id,
                    'period_id': period_id,
                    'debit': record.usd_cash_register_balance_end_real,
                    'credit': 0.0,
                    #'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    #'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    #'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                line_ids.append(debit_line)

                credit_line = (0, 0, {
                    'name': name,
                    'date': receiptDate,
                    #'partner_id': partner_id,
                    'account_id': record.usd_journal_id.default_credit_account_id.id,
                    'journal_id': record.cash_journal_id.id,
                    'period_id': period_id,
                    'credit': record.usd_cash_register_balance_end_real,
                    'debit': 0.0,
                    #'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    #'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    #'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                line_ids.append(credit_line)
                move = {
                    'narration': name,
                    'date': receiptDate,
                    'ref': record.name,
                    'journal_id': record.cash_journal_id.id,
                    'line_id': line_ids,
                    'period_id': period_id,
                }
                move_id = move_pool.create(cr, uid, move, context=context)

        return {}


    _columns = {
        'cash_control' : fields.function(_compute_cash_all,
                                         multi='cash',
                                         type='boolean', string='Has Cash Control'),
        'cash_journal_id' : fields.function(_compute_cash_all,
                                            multi='cash',
                                            type='many2one', relation='account.journal',
                                            string='Cash Journal', store=True),
        'cash_register_id' : fields.function(_compute_cash_all,
                                             multi='cash',
                                             type='many2one', relation='account.bank.statement',
                                             string='Cash Register', store=True),

        'crc_cash_journal_id' : fields.function(_compute_cash_all,
                                            multi='cash',
                                            type='many2one', relation='account.journal',
                                            string='CRC Cash Journal', store=True),
        'crc_cash_register_id' : fields.function(_compute_cash_all,
                                             multi='cash',
                                             type='many2one', relation='account.bank.statement',
                                             string='CRC Cash Register', store=True),
        'crc_cash_register_difference' : fields.related('crc_cash_register_id', 'difference',
                type='float',
                string='CRC Difference',
                help="Difference between the theoretical closing balance and the real closing balance.",
                readonly=True),

        'usd_cash_register_balance_end_real' : fields.related('cash_register_id', 'balance_end_real',
                type='float',
                digits_compute=dp.get_precision('Account'),
                string="USD Ending Balance",
                help="Total of closing cash control lines.",
                readonly=False),
        'crc_cash_register_balance_end_real' : fields.related('crc_cash_register_id', 'balance_end_real',
                type='float',
                digits_compute=dp.get_precision('Account'),
                string="CRC Ending Balance",
                help="Total of closing cash control lines.",
                readonly=False),

        'cash_register_balance_start' : fields.related('cash_register_id', 'balance_start',
                type='float',
                digits_compute=dp.get_precision('Account'),
                string="Starting Balance",
                help="Total of opening cash control lines.",
                readonly=True),
        'cash_register_total_entry_encoding' : fields.related('cash_register_id', 'total_entry_encoding',
                string='Total Cash Transaction',
                readonly=True,
                help="Total of all paid sale orders"),
        'cash_register_balance_end' : fields.related('cash_register_id', 'balance_end',
                type='float',
                digits_compute=dp.get_precision('Account'),
                string="Theoretical Closing Balance",
                help="Sum of opening balance and transactions.",
                readonly=True),
        'crc_cash_register_balance_end' : fields.related('crc_cash_register_id', 'balance_end',
                type='float',
                digits_compute=dp.get_precision('Account'),
                string="Theoretical Closing Balance",
                help="Sum of opening balance and transactions.",
                readonly=True),
        'cash_register_difference' : fields.related('cash_register_id', 'difference',
                type='float',
                string='Difference',
                help="Difference between the theoretical closing balance and the real closing balance.",
                readonly=True),

        'usd_journal_id' : fields.many2one('account.journal', 'Deposito USD',
             domain=[('type', '=', 'bank')],
             help="Cuenta en que se deposito el efectivo en dolares."),
        'crc_journal_id' : fields.many2one('account.journal', 'Deposito CRC',
             domain=[('type', '=', 'bank')],
             help="Cuenta en que se deposito el efectivo en colones."),
        'usd_deposit_reference': fields.char('USD No. depósito', copy=False),
        'crc_deposit_reference': fields.char('CRC No. depósito', copy=False),
    }

    def _check_cash_control(self, cr, uid, ids, context=None):
        return all(
            (sum(int(journal.cash_control) for journal in record.journal_ids) <= 2)
            for record in self.browse(cr, uid, ids, context=context)
        )

    _constraints = [
        (_check_cash_control, "You cannot have more than two cash controls in one Point Of Sale !", ['journal_ids']),
    ]


class account_cash_statement(osv.osv):

    _inherit = 'account.bank.statement'

    def _update_balances(self, cr, uid, ids, context=None):
        return {}