# Dataset V2: operational labeling and adjudication guide

**Status:** Researcher-authored guideline; not independently annotated or expert-approved. All 118 subcategories are generation/audit metadata. The predictive task has only three classes.

1. **Valid** — The message communicates an identifiable barangay/community concern, service problem, request for action, or report of a harmful event. Allegations need not be substantiated before classifying text. Informal language, anger, questions, anonymity, spelling errors, no photograph, or missing exact location **do not by themselves make a report Suspicious**. Jurisdictional referral does not negate validity. Reports *about* scams, threats, hate speech, and domestic abuse are Valid when an issue is clear. Dangerous reports should trigger a separate **human-urgent escalation flag**, regardless of class, where product workflow supports it.
2. **Suspicious** — Text appears to attempt to report something but lacks *essential semantic information to identify what happened*, contains materially unresolved anaphora, contradictions, an unlocatable unidentified urgent event, a referred but absent only description, or a corrupted passage. Do not equate suspicion with dishonesty. Missing personal details or optional attachments alone are not enough. Form-field contradictions are text-learnable only when explicitly included in the text.
3. **Spam** — Primary submission lacks a comprehensible community-reporting intent and is promotional, off-topic conversation, scam solicitation, meaningless strings, or classification manipulation. A resident *reporting receipt* of a phishing message is Valid, not Spam. A personal greeting in a detailed complaint does not turn it into Spam.

## Boundary cases

| Text (illustrative) | Label | Rationale |
| --- | --- | --- |
| `Wala pa gihapon nahakot ang basura.` | Valid | Clear report, short and without exact address |
| `May nagmessage po na scammer asking for OTP; paki-report.` | Valid | Scam reported as incident, not solicited |
| `Send your OTP for this bonus offer.` | Spam | Solicitation with no report |
| `Naay naipit somewhere, di ko sure kinsa o asa.` | Suspicious + manual urgent triage | Issue cannot be located/identified by text |
| `May child na sinasaktan sa bahay sa tapat ng tindahan.` | Valid + urgent triage | Actionable safety report; no mediation or conciliation for VAWC |
| `Yung dati na report, ayusin na lang.` | Suspicious | Missing referent if earlier report not accessible |
| `May baradong canal, no photo yet.` | Valid | Photo is not essential to grasp the issue |

## Review process needed before deployment

- Independently annotate a stratified sample, with at least two reviewers where resources permit, track disagreements and adjudicate; **this has not happened in V2**.
- Check Bisaya/Filipino/English/mixed-linguistic naturalness with fluent reviewers; generator-assigned languages are not proven language-identification ground truth.
- Review overlap: Valid vs Suspicious due to missing context, and Valid reporting Spam vs Spam solicitation.
- Store corrections in PostgreSQL with original text, original model prediction, final human decision, reason, timestamp and model version; do not immediately retrain on every correction.
- Keep a frozen untouched blind test for future model updates. The v2 synthetic test and challenge sets have already been evaluated and are not blind for further optimization.
