# JobMail

## A private job-email tracker

JobMail reads unread job-related Gmail messages on the user's computer and can add selected structured details to the user's own Google Sheet. A read-only preview comes first; message bodies stay out of Sheets and CSV by default.

### Who it may help

Active job seekers who already use Gmail and Sheets, and lose time copying interview, application, and offer updates into a tracker.

### Why use it

- Start with a Gmail read-only dry-run; inspect matches before authorizing writes.
- Keep the data destination in the user's own Google account.
- Recover safely from an interrupted Sheet write using message-ID reconciliation.
- See optional match-signal labels without exposing email subjects or bodies in logs.

### Current limits

Local Python CLI only; Google OAuth setup is required. No hosted account, mobile app, AI resume claims, automatic job applications, or paid subscription is offered. Job classification is a keyword filter and can miss or misclassify messages. Validate important rows before relying on them.

### Business hypothesis

Offer a fixed-scope paid setup session for OAuth, sheet columns, filters, and a safe first preview. Price, target user, and willingness to pay are unvalidated. Do not promise job outcomes or send outreach without approved recipients and message review.

### Next validation

Interview 5–8 job seekers about their current tracker, missed updates, Gmail permissions, and willingness to pay for setup. Continue only if a buyer agrees to a bounded pilot and the privacy review passes.
