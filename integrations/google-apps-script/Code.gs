/* SkyInvest lead receiver for a Google Sheet.
 *
 * 1. Open a new Google Sheet → Extensions → Apps Script.
 * 2. Replace the default code with this file.
 * 3. Run setup() once and set Script Property WEBHOOK_SECRET.
 * 4. Deploy as a Web app. Execute as yourself; access: Anyone.
 */

const SHEET_NAME = "Leads";
const HEADERS = [
  "lead_id", "stage", "created_at", "updated_at", "page", "locale", "offer",
  "messenger", "phone", "country", "budget", "utm_source", "utm_medium",
  "utm_campaign", "utm_term", "utm_content", "gclid", "page_url", "form_type", "purpose"
];

function setup() {
  const sheet = getSheet_();
  ensureHeaders_(sheet);
}

function ensureHeaders_(sheet) {
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length)
      .setFontWeight("bold")
      .setBackground("#0E513D")
      .setFontColor("#FFFFFF");
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, HEADERS.length);
    return;
  }

  // Existing sheets may have been created before new lead fields were added.
  // Only append missing columns, so historical leads keep their original order.
  const existing = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const missing = HEADERS.filter((header) => !existing.includes(header));
  if (!missing.length) return;
  const startColumn = sheet.getLastColumn() + 1;
  sheet.getRange(1, startColumn, 1, missing.length)
    .setValues([missing])
    .setFontWeight("bold")
    .setBackground("#0E513D")
    .setFontColor("#FFFFFF");
  sheet.autoResizeColumns(startColumn, missing.length);
}

function doGet() {
  return reply_({ ok: true, service: "SkyInvest lead receiver" });
}

function doPost(event) {
  const secret = PropertiesService.getScriptProperties().getProperty("WEBHOOK_SECRET");
  const key = event && event.parameter ? event.parameter.key : "";
  if (!secret || key !== secret) return reply_({ ok: false, error: "Unauthorized" });

  try {
    const lead = JSON.parse(event.postData.contents);
    if (!lead.id || !lead.phone) return reply_({ ok: false, error: "Missing lead id or phone" });

    const sheet = getSheet_();
    const existingRow = findLeadRow_(sheet, lead.id);
    const createdAt = existingRow
      ? sheet.getRange(existingRow, 3).getValue()
      : lead.createdAt || new Date().toISOString();
    const row = rowForLead_(lead, createdAt);

    if (existingRow) {
      sheet.getRange(existingRow, 1, 1, HEADERS.length).setValues([row]);
    } else {
      sheet.appendRow(row);
    }
    return reply_({ ok: true, leadId: lead.id, updated: Boolean(existingRow) });
  } catch (error) {
    return reply_({ ok: false, error: String(error) });
  }
}

function getSheet_() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME)
    || SpreadsheetApp.getActiveSpreadsheet().insertSheet(SHEET_NAME);
  ensureHeaders_(sheet);
  return sheet;
}

function findLeadRow_(sheet, leadId) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return 0;
  const ids = sheet.getRange(2, 1, lastRow - 1, 1).getValues().flat();
  const offset = ids.findIndex((id) => String(id) === String(leadId));
  return offset === -1 ? 0 : offset + 2;
}

function rowForLead_(lead, createdAt) {
  const attribution = lead.attribution || {};
  return [
    lead.id, lead.stage || "phone", createdAt, new Date().toISOString(),
    lead.source || "", lead.locale || "", lead.offer || "", lead.messenger || "",
    lead.phone || "", lead.country || "", lead.budget || "", attribution.utm_source || "",
    attribution.utm_medium || "", attribution.utm_campaign || "", attribution.utm_term || "",
    attribution.utm_content || "", attribution.gclid || "", lead.pageUrl || "", lead.formType || "", lead.purpose || ""
  ];
}

function reply_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
