"use client";

type Props = {
  title: string;
  action: string;
  onOpen: (offer?: string) => void;
  compact?: boolean;
};

/** Visual entry point to the existing two-step lead form. */
export default function LeadTeaser({ title, action, onOpen, compact = false }: Props) {
  return (
    <div className={`lead-teaser${compact ? " lead-teaser--compact" : ""}`}>
      <p>{title}</p>
      <div className="lead-teaser__messengers" aria-label="Выберите удобный мессенджер">
        <button type="button" className="lead-teaser__whatsapp" onClick={() => onOpen(action)}>WhatsApp</button>
        <button type="button" onClick={() => onOpen(action)}>Telegram</button>
        <button type="button" onClick={() => onOpen(action)}>Viber</button>
      </div>
      <button type="button" className="lead-teaser__submit" onClick={() => onOpen(action)}>{action} <span>→</span></button>
      <small>Без неожиданных звонков: номер нужен только для ответа в выбранном мессенджере.</small>
    </div>
  );
}
