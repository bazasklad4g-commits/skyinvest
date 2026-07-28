"use client";

import { FormEvent, useEffect, useState } from "react";
import type { Locale } from "../content/landing-pages";

declare global {
  interface Window { dataLayer?: Array<Record<string, unknown>>; }
}

type LeadModalProps = {
  open: boolean;
  onClose: () => void;
  tone?: "dark" | "light";
  source?: string;
  locale?: Locale;
  offer?: string;
};

const copy = {
  ru: {
    step: "Шаг 1 из 2", where: "Куда отправить подборку?", phoneText: "Выберите мессенджер и оставьте номер. Не будем звонить без договорённости.", phone: "Номер телефона", send: "Получить подборку", consent: "Нажимая кнопку, вы соглашаетесь на обработку номера для ответа на запрос.", last: "Осталось два ответа", what: "Что подобрать?", details: "Так мы уберём лишнее и пришлём варианты под вашу задачу.", country: "Страна", budget: "Ориентир по бюджету", choose: "Выберите диапазон", submit: "Передать запрос эксперту", success: "Запрос принят", successText: "Эксперт напишет в выбранный мессенджер после просмотра запроса.", return: "Вернуться на страницу", error: "Не удалось отправить запрос. Мы не сохранили ваш номер. Попробуйте ещё раз позже.", countries: ["Испания", "Турция", "Дубай", "Бали", "Северный Кипр", "Пока не решил(а)"], budgets: ["до 100 тыс.", "100–250 тыс.", "250–500 тыс.", "от 500 тыс.", "Обсудить с экспертом"],
  },
  uk: {
    step: "Крок 1 з 2", where: "Куди надіслати добірку?", phoneText: "Оберіть месенджер і залиште номер. Не будемо телефонувати без домовленості.", phone: "Номер телефону", send: "Отримати добірку", consent: "Натискаючи кнопку, ви погоджуєтеся на обробку номера для відповіді на запит.", last: "Ще два відповіді", what: "Що підібрати?", details: "Так ми відсіємо зайве та надішлемо варіанти під вашу задачу.", country: "Країна", budget: "Орієнтир по бюджету", choose: "Оберіть діапазон", submit: "Передати запит експерту", success: "Запит прийнято", successText: "Експерт напише у вибраний месенджер після перегляду запиту.", return: "Повернутися на сторінку", error: "Не вдалося надіслати запит. Ми не зберегли ваш номер. Спробуйте пізніше.", countries: ["Іспанія", "Туреччина", "Дубай", "Балі", "Північний Кіпр", "Ще не вирішив(ла)"], budgets: ["до 100 тис.", "100–250 тис.", "250–500 тис.", "від 500 тис.", "Обговорити з експертом"],
  },
  en: {
    step: "Step 1 of 2", where: "Where should we send the shortlist?", phoneText: "Choose a messenger and leave your number. We will not call without an agreement.", phone: "Phone number", send: "Get the shortlist", consent: "By continuing, you agree that we may use your number to respond to this request.", last: "Two quick answers", what: "What should we look for?", details: "This helps us remove the noise and send options relevant to your brief.", country: "Country", budget: "Budget range", choose: "Choose a range", submit: "Send the request", success: "Request received", successText: "An expert will write to you in the messenger you selected after reviewing the brief.", return: "Return to the page", error: "We could not send the request, and did not save your number. Please try again later.", countries: ["Spain", "Turkey", "Dubai", "Bali", "Northern Cyprus", "I am still deciding"], budgets: ["under 100k", "100–250k", "250–500k", "over 500k", "Discuss with an expert"],
  },
} as const;

export default function LeadModal({ open, onClose, tone = "dark", source = "catalog", locale = "ru", offer }: LeadModalProps) {
  const [step, setStep] = useState(1);
  const [messenger, setMessenger] = useState("Telegram");
  const [phone, setPhone] = useState("");
  const [country, setCountry] = useState("");
  const [budget, setBudget] = useState("");
  const [leadId, setLeadId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);
  const t = copy[locale];

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  function attribution() {
    const search = new URLSearchParams(window.location.search);
    return Object.fromEntries(["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"].flatMap((key) => {
      const value = search.get(key);
      return value ? [[key, value]] : [];
    }));
  }

  async function sendLead(stage: "phone" | "qualified") {
    const response = await fetch("/api/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stage, leadId, source, locale, offer, messenger, phone, country, budget, attribution: attribution() }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.message ?? "Lead delivery failed");
    return payload.leadId as string | undefined;
  }

  async function handlePhone(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSending(true);
    try {
      window.dataLayer?.push({ event: "lead_form_phone_submit", form_location: source, messenger });
      const id = await sendLead("phone");
      setLeadId(id ?? null);
      setStep(2);
    } catch {
      setError(t.error);
    } finally {
      setSending(false);
    }
  }

  async function handleDetails(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSending(true);
    try {
      await sendLead("qualified");
      window.dataLayer?.push({ event: "lead_form_complete", form_location: source, messenger, selected_country: country });
      setStep(3);
    } catch {
      setError(t.error);
    } finally {
      setSending(false);
    }
  }

  function closeAndReset() {
    onClose();
    window.setTimeout(() => {
      setStep(1); setPhone(""); setCountry(""); setBudget(""); setLeadId(null); setError("");
    }, 250);
  }

  return (
    <div className={`lead-overlay lead-overlay--${tone}`} role="dialog" aria-modal="true" aria-label={t.where}>
      <button className="lead-overlay__backdrop" onClick={closeAndReset} aria-label="Close form" />
      <section className="lead-modal">
        <button className="lead-modal__close" onClick={closeAndReset} aria-label="Close">×</button>
        <div className="lead-modal__progress"><span style={{ width: step === 1 ? "50%" : "100%" }} /></div>
        {step === 1 && (
          <form onSubmit={handlePhone}>
            <p className="lead-modal__kicker">{t.step}</p>
            <h2>{t.where}</h2>
            <p>{t.phoneText}</p>
            <div className="messenger-row" aria-label="Messenger">
              {["Telegram", "WhatsApp", "Viber"].map((item) => <button type="button" key={item} onClick={() => setMessenger(item)} className={messenger === item ? "is-active" : ""}>{item}</button>)}
            </div>
            <label className="field-label" htmlFor={`phone-${source}`}>{t.phone}</label>
            <input id={`phone-${source}`} className="lead-input" type="tel" inputMode="tel" autoComplete="tel" placeholder="+380 00 000 00 00" value={phone} onChange={(event) => setPhone(event.target.value)} required />
            {error && <p className="lead-error" role="alert">{error}</p>}
            <button className="lead-submit" type="submit" disabled={sending}>{sending ? "…" : offer ?? t.send}</button>
            <small>{t.consent}</small>
          </form>
        )}
        {step === 2 && (
          <form onSubmit={handleDetails}>
            <p className="lead-modal__kicker">{t.last}</p>
            <h2>{t.what}</h2>
            <p>{t.details}</p>
            <label className="field-label">{t.country}</label>
            <div className="choice-grid">
              {t.countries.map((item) => <button type="button" key={item} onClick={() => setCountry(item)} className={country === item ? "is-active" : ""}>{item}</button>)}
            </div>
            <label className="field-label">{t.budget}</label>
            <select className="lead-input" value={budget} onChange={(event) => setBudget(event.target.value)} required>
              <option value="" disabled>{t.choose}</option>
              {t.budgets.map((item) => <option key={item}>{item}</option>)}
            </select>
            {error && <p className="lead-error" role="alert">{error}</p>}
            <button className="lead-submit" type="submit" disabled={!country || sending}>{sending ? "…" : t.submit}</button>
          </form>
        )}
        {step === 3 && (
          <div className="lead-success">
            <span>✓</span>
            <p className="lead-modal__kicker">{t.success}</p>
            <h2>{t.success}</h2>
            <p>{t.successText}</p>
            <button className="lead-submit" onClick={closeAndReset}>{t.return}</button>
          </div>
        )}
      </section>
    </div>
  );
}
