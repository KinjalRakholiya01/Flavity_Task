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

What happens when you click Send (module steps marked *):

```
Composer (To, Cc, Bcc) -> Send
  * wizard: puts To partner ids + Cc/Bcc addresses in the context
  core: message_post -> _notify_thread_by_email (one group per recipient type)
  * mail.thread: only the group containing the To partners gets
                 email_cc + email_bcc + flag composer_cc_bcc
  core: mail.mail created
  * mail.mail._prepare_outgoing_list: Cc header on the customer's email
    (core's separate Cc-only email dropped), Bcc header added,
    Cc/Bcc addresses added to the allowed SMTP recipients
  core ir.mail_server: SMTP recipients = To + Cc + Bcc,
    then deletes the Bcc header, then sends ONE email
```

## How it works

Built from Odoo 19's own sending code (`mail.thread`, `mail.mail`,
`ir.mail_server`). Three small overrides, no copy of any core method body.

### 1. Composer (`wizard/mail_compose_message.py`)

Adds `partner_cc_ids` and `partner_bcc_ids` (Many2many `res.partner`). In
`_action_send_mail_comment` the chosen Cc/Bcc addresses and the "To" partner
ids are put in the context, then core's method runs unchanged.

### 2. Choosing the right outgoing email (`models/mail_thread.py`)

One send can create several `mail.mail` records (e.g. one for the customer,
another one for an internal follower like the salesperson).
`_notify_by_email_get_final_mail_values` is called once per recipient group,
just before that group's `mail.mail` is created, with the exact partner ids
of the group. Only the group containing the composer's "To" partners gets
`email_cc`, `email_bcc` and a technical flag `composer_cc_bcc`. Internal
notifications never carry Cc/Bcc.

### 3. Building the email (`models/mail_mail.py`)

Two behaviours of Odoo 19 core had to be corrected for flagged emails, in
`_prepare_outgoing_list`:

- **Cc is split off by core.** A notification email stores its recipient in
  `recipient_ids` with an empty `email_to`. In that case core does not add
  `email_cc` to the partner's email; it sends a *separate* email only to the
  Cc addresses, and the customer's email has no Cc header. The module moves
  the Cc header back onto the customer's email and drops the separate one.
- **Bcc is filtered out by core.** `mail.mail._send()` never passes Bcc to
  the mail server, and `ir.mail_server._prepare_smtp_to_list` builds the SMTP
  recipients from the To/Cc/Bcc headers but keeps only the addresses listed
  in `send_validated_to` (the email's `email_to_normalized`). The module sets
  a `Bcc` header **and** adds the Bcc addresses to that list.

Bcc stays invisible thanks to core itself: `ir.mail_server` computes the SMTP
recipient list first, then `_alter_message__` deletes the `Bcc` header before
the message is transmitted.

Extra Cc/Bcc addresses are added to the first "To" email only, so each Cc/Bcc
recipient gets exactly one copy.

### Why the Bcc recipient does not see a "bcc:" line

A variant that sent each Bcc recipient a separate copy with `Bcc: <them>`
(like some mail clients do) was tried and rejected: through Gmail SMTP that
copy also reached the To recipient, i.e. the Bcc address leaked, which is the
one thing the task forbids. A single email with Bcc in the SMTP envelope only
cannot leak by construction. The Bcc recipient can still tell it was a blind
copy: their address is in neither To nor Cc.

## Assumptions and limitations

- Works in the composer's "comment" mode (one record: quotation, order,
  lead...), which is how sales and CRM send emails. Not wired for mass
  mailing / Email Marketing, where one Bcc per personalized email would be
  wrong.
- The "To" recipients are contacts (`res.partner`), which is always the case
  from sales orders, quotations and leads. A To that is a bare email with no
  contact is not matched.
- Contacts without an email address are skipped in Cc/Bcc (same as To).
- Cc/Bcc are not stored on the chatter message; the values are on the
  outgoing `mail.mail` (Settings > Technical > Email > Emails).
- Deliverability (spam folder) depends on the mail server setup: a real
  company identity and a Reply-To matching the sending domain. It is not
  related to this module.
- No new access rules: only fields on existing models (`mail.compose.message`,
  `mail.mail`) whose access is already managed by `mail`.

## Screenshots

Located in `static/description/screenshots/`:

| File | Shows |
| --- | --- |
| `01_installed.png` | Module installed in Apps (Odoo 19 Community) |
| `02_composer.png` | Quotation "Send by Email" with To, Cc and Bcc filled |
| `03_email_record.png` | Settings > Technical > Emails: Cc and Bcc stored, state Sent |
| `04_to_inbox.png` | To mailbox header: `to:` + `cc:`, no Bcc |
| `05_cc_inbox.png` | Cc mailbox: same email, no Bcc |
| `06_bcc_inbox.png` | Bcc mailbox: email received, no Bcc in headers |

## Tested

Odoo 19.0 Community (Docker), Gmail SMTP: quotation sent with To + Cc + Bcc.
To and Cc inboxes show `to:` and `cc:` headers, no Bcc. The Bcc inbox receives
the same single email, and its headers also show no Bcc.
