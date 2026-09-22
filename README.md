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

## Tested

Odoo 19.0 Community (Docker), Gmail SMTP: quotation sent with To + Cc + Bcc.
To and Cc inboxes show `to:` and `cc:` headers, no Bcc. The Bcc inbox receives
the same single email, and its headers also show no Bcc.
