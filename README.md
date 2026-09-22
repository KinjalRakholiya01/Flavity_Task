# Composer Cc & Bcc (Odoo 19 Community)

Adds **Cc** and **Bcc** fields to the Odoo mail composer, used when sending
emails from sales orders, quotations and CRM leads.

- **Cc**: visible copy. Cc recipients appear in the `Cc` header and every
  recipient can see them.
- **Bcc**: blind copy. Bcc recipients receive the email, but their address is
  not written in any header of the sent email, so no other recipient can see
  that a blind copy was sent, or to whom.

## Installation

1. Copy the `composer_cc_bcc` folder into the addons path of your Odoo 19
   Community instance.
2. Restart Odoo, enable developer mode, then go to Apps > Update Apps List.
3. Search for **Composer Cc & Bcc** and click Install.

Depends only on `mail`. No configuration needed.

## Usage

1. Open a quotation / sales order (Send by Email) or a CRM lead (full
   composer).
2. Fill **To** as usual and add contacts in **Cc** and/or **Bcc**.
3. Click Send. One email goes out with `To` and `Cc` headers; Bcc contacts
   receive it without being listed.
4. The sent values can be checked in Settings > Technical > Email > Emails.

## Assumptions and limitations

- Works when sending from a single record (quotation, order, lead). Not
  available for mass mailing / Email Marketing.
- "To" recipients are contacts; a typed address becomes a contact, as in
  standard Odoo.
- Contacts without an email address are skipped.
- The Bcc recipient sees no `bcc:` line in the received email.
- Cc/Bcc are stored on the outgoing email, not on the chatter message.
- No default Cc/Bcc per company or template.
- Spam placement depends on the mail server configuration.
- Tested manually on Odoo 19.0 Community with Gmail SMTP; no automated tests.

## Screenshots

See `composer_cc_bcc/static/description/screenshots/` (also shown on the
app's description page in Odoo).
