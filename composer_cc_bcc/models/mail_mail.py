from odoo import fields, models, tools


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char(
        string="Bcc",
        help="Blind copy recipients. They are added to the SMTP envelope "
             "only; the Bcc header is removed by Odoo before sending, so no "
             "recipient can see them.",
    )
    composer_cc_bcc = fields.Boolean(
        string="Cc/Bcc from Composer",
        help="Technical flag: this email got its Cc/Bcc from the mail "
             "composer, so it must go out as ONE email to To + Cc + Bcc.",
    )

    def _prepare_outgoing_list(self, mail_server=False, doc_to_followers=None):
        """Send To, Cc and Bcc in a single email.

        Two core behaviours of Odoo 19 need correcting, only for emails
        flagged by our composer:

        1. Cc: a notification email has its recipients in ``recipient_ids``
           and an empty ``email_to``. Core then does NOT put ``email_cc`` on
           the partner's email but creates a *separate* Cc-only email. We move
           the Cc header back onto the "To" email(s) and drop that extra one.

        2. Bcc: ``ir.mail_server`` builds the real SMTP recipients from the
           To/Cc/Bcc headers, but only keeps addresses listed in
           ``email_to_normalized`` (passed as ``send_validated_to``). So we
           set a ``Bcc`` header AND add the Bcc addresses to that list.
           ``ir.mail_server`` computes the SMTP recipient list first, then
           deletes the ``Bcc`` header (``_alter_message__``), so the blind
           copy is delivered but never visible in any header.

        Extra Cc/Bcc addresses are only added to the FIRST "To" email, so each
        Cc/Bcc recipient receives exactly one copy.
        """
        emails = super()._prepare_outgoing_list(
            mail_server=mail_server, doc_to_followers=doc_to_followers,
        )
        if not self.composer_cc_bcc:
            return emails

        to_emails = [e for e in emails if e["email_to"]]
        if not to_emails:
            return emails

        # 1. Cc: merge core's separate Cc-only email into the "To" email(s)
        cc_only = [e for e in emails if not e["email_to"] and e["email_cc"]]
        cc_list, cc_normalized = [], []
        if self.email_cc and len(cc_only) == 1:
            cc_list = list(cc_only[0]["email_cc"])
            cc_normalized = list(cc_only[0]["email_to_normalized"])
            emails = [e for e in emails if e is not cc_only[0]]

        # 2. Bcc
        bcc_list = tools.mail.email_split_and_format_normalize(self.email_bcc or "")
        bcc_normalized = tools.mail.email_normalize_all(self.email_bcc or "")

        for index, entry in enumerate(to_emails):
            if cc_list:
                entry["email_cc"] = list(cc_list)
            if index == 0:
                entry["email_to_normalized"] = (
                    list(entry["email_to_normalized"])
                    + cc_normalized + bcc_normalized
                )
                if bcc_list:
                    # copy: core shares one headers dict across all entries
                    entry["headers"] = {**entry["headers"], "Bcc": ", ".join(bcc_list)}
        return emails
