from odoo import fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    partner_cc_ids = fields.Many2many(
        "res.partner",
        "composer_cc_bcc_wizard_cc_rel",
        "wizard_id",
        "partner_id",
        string="Cc",
        help="Contacts receiving a visible copy: they appear in the Cc header "
             "and every recipient can see them.",
    )
    partner_bcc_ids = fields.Many2many(
        "res.partner",
        "composer_cc_bcc_wizard_bcc_rel",
        "wizard_id",
        "partner_id",
        string="Bcc",
        help="Contacts receiving a blind copy: nobody else can see that they "
             "received it.",
    )

    def _action_send_mail_comment(self, res_ids):
        """Pass the Cc/Bcc choice down to the notification pipeline via context.

        The actual posting stays 100% core. ``mail.thread`` picks the values
        up in ``_notify_by_email_get_final_mail_values`` (see
        models/mail_thread.py), for the outgoing email addressed to the
        composer's "To" partners only.
        """
        self.ensure_one()
        cc_emails = [p.email_formatted for p in self.partner_cc_ids if p.email]
        bcc_emails = [p.email_formatted for p in self.partner_bcc_ids if p.email]
        if cc_emails or bcc_emails:
            self = self.with_context(
                composer_cc_bcc_to_partner_ids=self.partner_ids.ids,
                composer_cc_bcc_cc_emails=cc_emails,
                composer_cc_bcc_bcc_emails=bcc_emails,
            )
        return super()._action_send_mail_comment(res_ids)
