"use client";

type Locale = "ru" | "uk" | "en";

type Props = {
  title: string;
  action: string;
  onOpen: (offer?: string) => void;
  compact?: boolean;
  locale?: Locale;
};

/** Aria label and reassurance line follow the page language, not the default Russian. */
const copy: Record<Locale, { pick: string; note: string }> = {
  ru: {
    pick: "Выберите удобный мессенджер",
    note: "Без неожиданных звонков: номер нужен только для ответа в выбранном мессенджере.",
  },
  uk: {
    pick: "Оберіть зручний месенджер",
    note: "Без несподіваних дзвінків: номер потрібен лише для відповіді в обраному месенджері.",
  },
  en: {
    pick: "Choose your messenger",
    note: "No unexpected calls: your number is used only to reply in the messenger you pick.",
  },
};

/** Visual entry point to the existing two-step lead form. */
export default function LeadTeaser({ title, action, onOpen, compact = false, locale = "ru" }: Props) {
  const t = copy[locale];
  return (
    <div className={`lead-teaser${compact ? " lead-teaser--compact" : ""}`}>
      <p>{title}</p>
      <div className="lead-teaser__messengers" aria-label={t.pick}>
        <button type="button" className="lead-teaser__whatsapp" onClick={() => onOpen(action)}>WhatsApp</button>
        <button type="button" onClick={() => onOpen(action)}>Telegram</button>
        <button type="button" onClick={() => onOpen(action)}>Viber</button>
      </div>
      <button type="button" className="lead-teaser__submit" onClick={() => onOpen(action)}>{action} <span>→</span></button>
      <small>{t.note}</small>
    </div>
  );
}
