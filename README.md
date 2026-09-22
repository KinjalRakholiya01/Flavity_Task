# Composer Cc & Bcc (Odoo 19 Community)

Adds **Cc** and **Bcc** fields to Odoo's mail composer (`mail.compose.message`),
the "Send by Email" popup used from sales orders, quotations and CRM leads
(and anywhere else the full composer is opened).

- **Cc**: visible copy. Cc recipients appear in the `Cc` header and every
  recipient can see them.
- **Bcc**: blind copy. Bcc recipients receive the email, but their address is
  never written in any header of the transmitted message, so nobody (not
  even the Bcc recipient) can see who received a blind copy. This matches
  the task requirement: "Bcc must NOT appear in any header sent to
  recipients".

## Installation

1. Copy the `composer_cc_bcc` folder into an addons path of your Odoo 19
   Community instance.
2. Restart Odoo, enable developer mode, then Apps > Update Apps List.
3. Search for **Composer Cc & Bcc** and click Install.

Only dependency: `mail`. No configuration needed.

## Usage

1. Open a quotation / sales order (Send by Email) or a CRM lead (send
   message > full composer).
2. Fill **To** as usual, and add contacts in **Cc** and/or **Bcc** (existing
   contacts, or type an email address: a contact is created on the fly, like
   the To field).
3. Send. One single email goes out:
   - `To:` the chosen recipients, `Cc:` the Cc contacts;
   - the Bcc contacts are only in the SMTP envelope.
4. The stored values can be checked in Settings > Technical > Email > Emails
   (the `Bcc` field is shown next to `Cc`).

## Workflow

Standard Odoo 19 vs this module:

| Step | Standard Odoo 19 | With this module |
| --- | --- | --- |
| Composer | Only "Recipients" (To) | Cc and Bcc fields under To |
| Cc | Stored on `mail.mail` but sent as a *separate* email; the customer's email has no Cc header | One email: To + `Cc:` header |
| Bcc | No field; `mail.mail` never passes Bcc to the mail server | Delivered through the SMTP envelope only |
| Mail server | Supports Cc/Bcc headers, strips `Bcc` before sending | Unchanged (the module relies on it) |

## Assumptions and limitations

**Assumptions**

- Emails are sent from a single record (quotation, sales order, CRM lead): the
  composer's "comment" mode. Cc/Bcc are hidden for mass mailing and Log note.
- "To" recipients are contacts (`res.partner`); a typed address becomes a
  contact automatically, as in standard Odoo.
- An outgoing mail server is configured; delivery is done by Odoo core.

**Limitations**

- Not wired for mass mailing / Email Marketing (one personalized email per
  recipient would send the Bcc once per customer).
- Contacts without an email address are skipped in Cc/Bcc, like in To.
- The Bcc recipient sees no `bcc:` line: one email with Bcc only in the SMTP
  envelope cannot leak by construction (a per-Bcc copy was tested and leaked).
- Cc/Bcc are stored on the outgoing email (Settings > Technical > Email >
  Emails), not on the chatter message.
- Only the customer's email gets Cc/Bcc; internal follower notifications of
  the same send do not.
- No default Cc/Bcc per company or template; chosen per send.
- Spam placement depends on the mail server setup (company identity,
  Reply-To, sender reputation), not on this module.
- Relies on three Odoo 19 core methods (`_action_send_mail_comment`,
  `_notify_by_email_get_final_mail_values`, `_prepare_outgoing_list`); a
  future change to them needs a re-check.
- No automated tests included; tested manually with Gmail SMTP.
- No new access rules: no new model, only fields on `mail.compose.message`
  and `mail.mail`, already covered by the `mail` module's ACLs.

## Tested

Odoo 19.0 Community (Docker), Gmail SMTP: quotation sent with To + Cc + Bcc.
To and Cc inboxes show `to:` and `cc:` headers, no Bcc. The Bcc inbox receives
the same single email, and its headers also show no Bcc.
