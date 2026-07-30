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

type PhoneProfile = {
  code: string;
  name: string;
  prefix: string;
  mask: string;
};

const phoneProfiles: PhoneProfile[] = [
  { code: "UA", name: "Украина", prefix: "+380", mask: "(0__) ___ __ __" },
  { code: "PL", name: "Польша", prefix: "+48", mask: "___ ___ ___" },
  { code: "DE", name: "Германия", prefix: "+49", mask: "___ ________" },
  { code: "ES", name: "Испания", prefix: "+34", mask: "___ ___ ___" },
  { code: "TR", name: "Турция", prefix: "+90", mask: "(5__) ___ __ __" },
  { code: "AE", name: "ОАЭ", prefix: "+971", mask: "__ ___ ____" },
  { code: "GE", name: "Грузия", prefix: "+995", mask: "___ __ __ __" },
  { code: "KZ", name: "Казахстан", prefix: "+7", mask: "___ ___ __ __" },
  { code: "OTHER", name: "Другая страна", prefix: "+", mask: "___ ___ ___ ___" },
];

const timezoneCountry: Record<string, string> = {
  "Europe/Kyiv": "UA", "Europe/Warsaw": "PL", "Europe/Berlin": "DE", "Europe/Madrid": "ES",
  "Europe/Istanbul": "TR", "Asia/Dubai": "AE", "Asia/Tbilisi": "GE", "Asia/Almaty": "KZ",
};

function getPhoneProfile() {
  if (typeof window === "undefined") return phoneProfiles[0];
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const localeCountry = navigator.language.split("-")[1]?.toUpperCase();
  const code = timezoneCountry[timezone] ?? localeCountry;
  return phoneProfiles.find((profile) => profile.code === code) ?? phoneProfiles[0];
}

function formatPhone(value: string, mask: string) {
  let index = 0;
  return mask.replace(/_/g, () => value[index++] ?? "_");
}

function requestedItem(offer: string | undefined, locale: Locale) {
  const value = offer?.toLowerCase() ?? "";
  if (locale === "en") {
    if (value.includes("review") || value.includes("case")) return "reviews and cases";
    if (value.includes("check")) return "the review map";
    if (value.includes("guide") || value.includes("material")) return "the guide";
    if (value.includes("catalogue") || value.includes("catalog")) return "the catalogue";
    return "the shortlist";
  }
  if (locale === "uk") {
    if (value.includes("карт") || value.includes("перевір")) return "карту перевірки";
    if (value.includes("відгук") || value.includes("кейс")) return "відгуки й кейси";
    if (value.includes("матеріал") || value.includes("гід") || value.includes("чек")) return "матеріал";
    if (value.includes("каталог")) return "каталог";
    return "добірку";
  }
  if (value.includes("карт") || value.includes("провер")) return "карту проверки";
  if (value.includes("отзыв") || value.includes("кейс")) return "отзывы и кейсы";
  if (value.includes("материал") || value.includes("гид") || value.includes("чек-лист")) return "материал";
  if (value.includes("каталог")) return "каталог";
  return "подборку";
}

const copy = {
  ru: {
    step: "Шаг 1 из 2", where: "Куда отправить подборку?", phoneText: "Выберите мессенджер и оставьте номер. Не будем звонить без договорённости.", phone: "Номер телефона", send: "Получить подборку", consent: "Нажимая кнопку, вы соглашаетесь на обработку номера для ответа на запрос.", last: "Осталось два ответа", what: "Что подобрать?", details: "Так мы уберём лишнее и пришлём варианты под вашу задачу.", country: "Страна", budget: "Ориентир по бюджету", choose: "Выберите диапазон", submit: "Передать запрос эксперту", success: "Запрос принят", successText: "Эксперт напишет в выбранный мессенджер после просмотра запроса.", return: "Вернуться на страницу", error: "Не удалось отправить запрос. Мы не сохранили ваш номер. Попробуйте ещё раз позже.", countries: ["Испания", "Турция", "Дубай", "Бали", "Северный Кипр", "Грузия", "Камбоджа", "Мальдивы", "Пока не решил(а)"], budgets: ["до 100 тыс.", "100–250 тыс.", "250–500 тыс.", "от 500 тыс.", "Обсудить с экспертом"],
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
  const [phoneProfile, setPhoneProfile] = useState<PhoneProfile>(phoneProfiles[0]);
  const [country, setCountry] = useState("");
  const [budget, setBudget] = useState("");
  const [leadId, setLeadId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);
  const t = copy[locale];
  const item = requestedItem(offer, locale);
  const formTitle = locale === "en" ? `Where should we send ${item}?` : `${locale === "uk" ? "Куди надіслати" : "Куда отправить"} ${item}?`;

  useEffect(() => {
    if (!open) return;
    setPhoneProfile(getPhoneProfile());
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
      body: JSON.stringify({ stage, leadId, source, locale, offer, messenger, phone: `${phoneProfile.prefix} ${phone}`.trim(), country, budget, attribution: attribution() }),
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
      // `form_submit_consult` is the existing GTM conversion trigger. Fire it
      // only after the lead has completed both form steps and was accepted by
      // the delivery API, so GA4/Google Ads do not count abandoned phone input.
      window.dataLayer?.push({
        event: "form_submit_consult",
        form_location: source,
        messenger,
        selected_country: country,
      });
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
      setStep(1); setPhone(""); setCountry(""); setBudget(""); setLeadId(null); setError(""); setPhoneProfile(getPhoneProfile());
    }, 250);
  }

  return (
    <div className={`lead-overlay lead-overlay--${tone}`} role="dialog" aria-modal="true" aria-label={formTitle}>
      <button className="lead-overlay__backdrop" onClick={closeAndReset} aria-label="Close form" />
      <section className="lead-modal">
        <button className="lead-modal__close" onClick={closeAndReset} aria-label="Close">×</button>
        <div className="lead-modal__progress"><span style={{ width: step === 1 ? "50%" : "100%" }} /></div>
        {step === 1 && (
          <form onSubmit={handlePhone}>
            <p className="lead-modal__kicker">{t.step}</p>
            <h2>{formTitle}</h2>
            <p>{t.phoneText}</p>
            <div className="messenger-row" aria-label="Messenger">
              {["Telegram", "WhatsApp", "Viber"].map((item) => <button type="button" key={item} onClick={() => setMessenger(item)} className={messenger === item ? "is-active" : ""}>{item}</button>)}
            </div>
            <label className="field-label" htmlFor={`phone-${source}`}>{t.phone}</label>
            <div className="phone-field">
              <select className="phone-country" aria-label="Страна номера" value={phoneProfile.code} onChange={(event) => {
                const profile = phoneProfiles.find((item) => item.code === event.target.value);
                if (profile) { setPhoneProfile(profile); setPhone(""); }
              }}>
                {phoneProfiles.map((profile) => <option value={profile.code} key={profile.code}>{profile.name} {profile.prefix}</option>)}
              </select>
              <div className="phone-field__number">
                <input id={`phone-${source}`} className="lead-input" type="tel" inputMode="tel" autoComplete="tel-national" aria-label={t.phone} placeholder={phoneProfile.mask} value={phone ? formatPhone(phone, phoneProfile.mask) : ""} onChange={(event) => setPhone(event.target.value.replace(/\D/g, "").slice(0, (phoneProfile.mask.match(/_/g) ?? []).length))} required />
              </div>
            </div>
            <p className="phone-field__hint">Страна определена автоматически — при необходимости выберите другую.</p>
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
