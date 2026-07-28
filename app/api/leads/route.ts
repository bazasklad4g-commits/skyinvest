import { randomUUID } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

type Lead = {
  id: string;
  stage: "phone" | "qualified";
  source: string;
  locale: string;
  offer?: string;
  messenger: string;
  phone: string;
  country?: string;
  budget?: string;
  attribution?: Record<string, string>;
  createdAt: string;
};

function asText(value: unknown, limit = 250) {
  return typeof value === "string" ? value.trim().slice(0, limit) : "";
}

function telegramText(lead: Lead) {
  const context = Object.entries(lead.attribution ?? {}).map(([key, value]) => `${key}: ${value}`).join("\n");
  return [
    `Новая заявка SkyInvest · ${lead.stage === "phone" ? "телефон" : "уточнение"}`,
    `ID: ${lead.id}`,
    `Страница: ${lead.source}`,
    `Язык: ${lead.locale}`,
    `Мессенджер: ${lead.messenger}`,
    `Телефон: ${lead.phone}`,
    lead.country ? `Страна: ${lead.country}` : "",
    lead.budget ? `Бюджет: ${lead.budget}` : "",
    lead.offer ? `Оффер: ${lead.offer}` : "",
    context ? `Атрибуция:\n${context}` : "",
  ].filter(Boolean).join("\n");
}

async function sendToTelegram(lead: Lead) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return false;
  const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text: telegramText(lead) }),
  });
  if (!response.ok) throw new Error("Telegram delivery failed");
  return true;
}

async function sendToSheetWebhook(lead: Lead) {
  const webhook = process.env.GOOGLE_SHEETS_WEBHOOK_URL;
  if (!webhook) return false;
  const endpoint = new URL(webhook);
  const secret = process.env.GOOGLE_SHEETS_WEBHOOK_SECRET;
  if (secret) endpoint.searchParams.set("key", secret);
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lead),
  });
  if (!response.ok) throw new Error("Sheets webhook delivery failed");
  return true;
}

export async function POST(request: NextRequest) {
  try {
    const raw = await request.json();
    const phone = asText(raw.phone, 50);
    const stage = raw.stage === "qualified" ? "qualified" : "phone";
    if (phone.length < 6) {
      return NextResponse.json({ message: "A phone number is required." }, { status: 400 });
    }

    const lead: Lead = {
      id: asText(raw.leadId, 100) || randomUUID(),
      stage,
      source: asText(raw.source, 100),
      locale: asText(raw.locale, 10),
      offer: asText(raw.offer, 120),
      messenger: asText(raw.messenger, 40),
      phone,
      country: asText(raw.country, 100),
      budget: asText(raw.budget, 100),
      attribution: typeof raw.attribution === "object" && raw.attribution ? raw.attribution : {},
      createdAt: new Date().toISOString(),
    };

    const delivered = await Promise.all([sendToTelegram(lead), sendToSheetWebhook(lead)]);
    if (!delivered.some(Boolean)) {
      return NextResponse.json({ message: "Lead delivery is not configured." }, { status: 503 });
    }
    return NextResponse.json({ leadId: lead.id, delivered: delivered.filter(Boolean).length });
  } catch {
    return NextResponse.json({ message: "Unable to deliver the lead." }, { status: 502 });
  }
}
