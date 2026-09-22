from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_by_email_get_final_mail_values(self, recipient_ids, mail_values,
                                               additional_values=None):
        """Put the composer's Cc/Bcc on the mail.mail built for the "To" partners.

        ``_notify_thread_by_email`` calls this once per recipient group, just
        before creating that group's mail.mail, with the exact partner ids it
        is for. A single send can create several groups (e.g. the customer,
        plus an internal follower such as the salesperson); only the group
        that contains the composer's "To" partners gets the Cc/Bcc.
        """
        values = super()._notify_by_email_get_final_mail_values(
            recipient_ids, mail_values, additional_values=additional_values,
        )
        ctx = self.env.context
        to_ids = ctx.get("composer_cc_bcc_to_partner_ids")
        if not to_ids or not set(recipient_ids or []) & set(to_ids):
            return values
        cc_emails = ctx.get("composer_cc_bcc_cc_emails")
        bcc_emails = ctx.get("composer_cc_bcc_bcc_emails")
        if cc_emails:
            values["email_cc"] = ",".join(cc_emails)
        if bcc_emails:
            values["email_bcc"] = ",".join(bcc_emails)
        if cc_emails or bcc_emails:
            values["composer_cc_bcc"] = True
        return values
