"use client";

import { FormEvent, useEffect, useState } from "react";

type LeadModalProps = {
  open: boolean;
  onClose: () => void;
  tone?: "dark" | "light";
  source?: string;
};

const countries = ["Испания", "Турция", "Дубай", "Бали", "Северный Кипр", "Пока не решил(а)"];
const budgets = ["до 100 тыс.", "100–250 тыс.", "250–500 тыс.", "от 500 тыс.", "Обсудить с экспертом"];

export default function LeadModal({ open, onClose, tone = "dark", source = "catalog" }: LeadModalProps) {
  const [step, setStep] = useState(1);
  const [messenger, setMessenger] = useState("Telegram");
  const [country, setCountry] = useState("");
  const [budget, setBudget] = useState("");

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

  function handlePhone(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStep(2);
  }

  function handleDetails(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStep(3);
  }

  function closeAndReset() {
    onClose();
    window.setTimeout(() => {
      setStep(1);
      setCountry("");
      setBudget("");
    }, 250);
  }

  return (
    <div className={`lead-overlay lead-overlay--${tone}`} role="dialog" aria-modal="true" aria-label="Получить подборку">
      <button className="lead-overlay__backdrop" onClick={closeAndReset} aria-label="Закрыть форму" />
      <section className="lead-modal">
        <button className="lead-modal__close" onClick={closeAndReset} aria-label="Закрыть">×</button>
        <div className="lead-modal__progress"><span style={{ width: step === 1 ? "50%" : "100%" }} /></div>
        {step === 1 && (
          <form onSubmit={handlePhone}>
            <p className="lead-modal__kicker">Шаг 1 из 2</p>
            <h2>Куда отправить подборку?</h2>
            <p>Выберите мессенджер и оставьте номер. Никаких рассылок и звонков без договорённости.</p>
            <div className="messenger-row" aria-label="Выберите мессенджер">
              {["Telegram", "WhatsApp", "Viber"].map((item) => (
                <button type="button" key={item} onClick={() => setMessenger(item)} className={messenger === item ? "is-active" : ""}>
                  {item}
                </button>
              ))}
            </div>
            <label className="field-label" htmlFor={`phone-${source}`}>Номер телефона</label>
            <input id={`phone-${source}`} className="lead-input" type="tel" inputMode="tel" placeholder="+380 00 000 00 00" required />
            <button className="lead-submit" type="submit">Получить каталог из 15 объектов</button>
            <small>Нажимая кнопку, вы соглашаетесь на обработку номера для ответа на запрос.</small>
          </form>
        )}
        {step === 2 && (
          <form onSubmit={handleDetails}>
            <p className="lead-modal__kicker">Осталось два ответа</p>
            <h2>Что подобрать?</h2>
            <p>Так эксперт уберёт лишнее и пришлёт варианты под вашу задачу.</p>
            <label className="field-label">Страна</label>
            <div className="choice-grid">
              {countries.map((item) => (
                <button type="button" key={item} onClick={() => setCountry(item)} className={country === item ? "is-active" : ""}>{item}</button>
              ))}
            </div>
            <label className="field-label">Ориентир по бюджету, €</label>
            <select className="lead-input" value={budget} onChange={(event) => setBudget(event.target.value)} required>
              <option value="" disabled>Выберите диапазон</option>
              {budgets.map((item) => <option key={item}>{item}</option>)}
            </select>
            <button className="lead-submit" type="submit" disabled={!country}>Передать запрос эксперту</button>
          </form>
        )}
        {step === 3 && (
          <div className="lead-success">
            <span>✓</span>
            <p className="lead-modal__kicker">Прототип завершён</p>
            <h2>Так выглядит успешная отправка</h2>
            <p>В рабочей версии заявка появится в Telegram и Google Sheets, а пользователь получит сообщение в выбранном мессенджере.</p>
            <button className="lead-submit" onClick={closeAndReset}>Вернуться на страницу</button>
          </div>
        )}
      </section>
    </div>
  );
}
