"use client";

import Link from "next/link";
import { useState } from "react";
import type { LandingPage } from "../content/landing-pages";
import LeadModal from "./LeadModal";

type Props = { page: LandingPage };

const labels = {
  ru: {
    privateSelection: "Private property selection",
    directions: "Направления",
    approach: "Как работаем",
    answers: "Вопросы",
    request: "Получить подборку",
    explore: "Посмотреть направления",
    tailored: "Подбор под ваш сценарий",
    messenger: "Ответ в мессенджере",
    noShowcase: "Без витрины с устаревшими данными",
    notCatalog: "Не каталог ради каталога",
    regions: "Локации",
    method: "Как строится работа",
    stepsTitle: "Четыре шага, чтобы не потеряться на старте",
    finalTitle: "Нужна подборка под ваш план?",
    finalText: "Оставьте номер в мессенджере. Сначала уточним задачу, затем отправим короткий список направлений или объектов.",
    privacy: "Политика конфиденциальности",
    countryLinks: "Другие направления",
    steps: [
      ["Запрос", "Выбираете мессенджер и оставляете номер. Страна может быть уже выбрана или пока нет."],
      ["Короткий разговор", "Уточняем, для чего нужен объект, какие сроки у вас и что точно не подходит."],
      ["Подборка", "Отправляем варианты, в которых есть логика для вашей ситуации, и объясняем, что сравнивать."],
      ["Следующий шаг", "Если подборка откликается, обсуждаем детали объекта и организуем дальнейший процесс."],
    ],
  },
  uk: {
    privateSelection: "Private property selection",
    directions: "Напрямки",
    approach: "Як працюємо",
    answers: "Питання",
    request: "Отримати добірку",
    explore: "Переглянути напрямки",
    tailored: "Підбір під ваш сценарій",
    messenger: "Відповідь у месенджері",
    noShowcase: "Без вітрини із застарілими даними",
    notCatalog: "Не каталог заради каталогу",
    regions: "Локації",
    method: "Як будується робота",
    stepsTitle: "Чотири кроки, щоб не загубитися на старті",
    finalTitle: "Потрібна добірка під ваш план?",
    finalText: "Залиште номер у месенджері. Спершу уточнимо задачу, а потім надішлемо короткий список напрямків або об'єктів.",
    privacy: "Політика конфіденційності",
    countryLinks: "Інші напрямки",
    steps: [
      ["Запит", "Обираєте месенджер і залишаєте номер. Країну вже можна знати або ще ні."],
      ["Коротка розмова", "Уточнюємо, навіщо потрібен об'єкт, які у вас строки і що точно не підходить."],
      ["Добірка", "Надсилаємо варіанти з логікою для вашої ситуації та пояснюємо, що порівнювати."],
      ["Наступний крок", "Якщо добірка відгукується, обговорюємо деталі об'єкта і подальший процес."],
    ],
  },
  en: {
    privateSelection: "Private property selection",
    directions: "Locations",
    approach: "How it works",
    answers: "Questions",
    request: "Get a shortlist",
    explore: "Explore locations",
    tailored: "A shortlist for your plan",
    messenger: "A reply in your messenger",
    noShowcase: "No outdated public stock list",
    notCatalog: "Not a catalogue for its own sake",
    regions: "Locations",
    method: "How we work",
    stepsTitle: "Four steps, without the early noise",
    finalTitle: "Need a shortlist for your plan?",
    finalText: "Leave your number in the messenger you prefer. We will clarify the brief first, then send a concise list of places or properties to consider.",
    privacy: "Privacy policy",
    countryLinks: "Other destinations",
    steps: [
      ["Your brief", "Choose a messenger and leave a number. You may know the country already, or still be deciding."],
      ["A short conversation", "We ask what the property needs to do, your timing, and the things you do not want to compromise on."],
      ["The shortlist", "We send options that fit the brief and explain what is useful to compare."],
      ["The next step", "If the shortlist feels right, we discuss property details and plan the next move."],
    ],
  },
} as const;

const countryLinks = [
  { id: "bali", href: "/bali-ru", ru: "Бали", uk: "Балі", en: "Bali" },
  { id: "tai", href: "/en", ru: "Таиланд и Азия", uk: "Таїланд та Азія", en: "Thailand & Asia" },
  { id: "tur", href: "/turkey-ru", ru: "Турция", uk: "Туреччина", en: "Turkey" },
  { id: "esp", href: "/ispania-ru", ru: "Испания", uk: "Іспанія", en: "Spain" },
  { id: "cypr", href: "/northern-cyprus-ru", ru: "Кипр", uk: "Кіпр", en: "Cyprus" },
  { id: "more", href: "/real-estate", ru: "Другие страны", uk: "Інші країни", en: "More countries" },
];

export default function LandingExperience({ page }: Props) {
  const [modalOpen, setModalOpen] = useState(false);
  const copy = labels[page.locale];
  const openLead = () => setModalOpen(true);

  return (
    <main className="landing" lang={page.locale}>
      <header className="landing-nav">
        <Link href="/real-estate" className="brand brand--light" aria-label="SkyInvest home"><span>SKY</span>INVEST</Link>
        <nav aria-label="Page navigation">
          <a href="#locations">{copy.directions}</a>
          <a href="#process">{copy.approach}</a>
          <a href="#faq">{copy.answers}</a>
        </nav>
        <button type="button" onClick={openLead}>{copy.request}</button>
      </header>

      <section className="landing-hero">
        <div className="landing-hero__image" style={{ backgroundImage: `url(${page.heroImage})`, backgroundPosition: page.heroPosition ?? "center" }} />
        <div className="landing-hero__shade" />
        <div className="landing-hero__content">
          <p className="eyebrow">{copy.privateSelection} · {page.country}</p>
          <h1>{page.h1}</h1>
          <p className="landing-hero__lead">{page.heroText}</p>
          <div className="landing-hero__actions">
            <button type="button" className="button button--champagne" onClick={openLead}>{page.offer}</button>
            <a href="#locations">{copy.explore} ↓</a>
          </div>
          <div className="landing-hero__trust" aria-label="Service principles">
            <span>{copy.tailored}</span>
            <span>{copy.messenger}</span>
            <span>{copy.noShowcase}</span>
          </div>
        </div>
        <span className="landing-hero__number">01 / {page.country}</span>
      </section>

      <section className="landing-intro" id="locations">
        <p className="section-index">01</p>
        <div>
          <p className="eyebrow eyebrow--gold">{copy.notCatalog}</p>
          <h2>{page.introTitle}</h2>
        </div>
        <p>{page.introText}</p>
      </section>

      {page.countryAnchors && (
        <section className="country-jump" aria-label={copy.countryLinks}>
          <p>{copy.countryLinks}</p>
          <div>
            {countryLinks.map((link) => <Link id={link.id} key={link.id} href={link.href}>{link[page.locale]}</Link>)}
          </div>
        </section>
      )}

      <section className="region-section">
        <div className="section-heading">
          <p className="eyebrow eyebrow--gold">{copy.regions}</p>
          <h2>{page.regionTitle}</h2>
        </div>
        <div className="region-grid">
          {page.regions.map((region, index) => (
            <article className="region-card" key={region.name}>
              <div className="region-card__image" style={{ backgroundImage: `url(${region.image})` }} />
              <div className="region-card__shade" />
              <div className="region-card__copy">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h3>{region.name}</h3>
                <p>{region.description}</p>
                <button type="button" onClick={openLead}>{copy.request}</button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-guide">
        <div className="landing-guide__image" style={{ backgroundImage: `url(${page.regions[0].image})` }}>
          <span>{page.country}</span>
          <strong>Sky<br />Invest</strong>
          <i>{page.offer}</i>
        </div>
        <div className="landing-guide__copy">
          <p className="eyebrow eyebrow--gold">Private shortlist</p>
          <h2>{page.guideTitle}</h2>
          <p>{page.guideText}</p>
          <ul>{page.guidePoints.map((point) => <li key={point}>{point}</li>)}</ul>
          <button type="button" className="button button--emerald" onClick={openLead}>{page.offer}</button>
        </div>
      </section>

      <section className="landing-process" id="process">
        <div>
          <p className="eyebrow eyebrow--gold">{copy.method}</p>
          <h2>{copy.stepsTitle}</h2>
        </div>
        <ol>
          {copy.steps.map(([title, text], index) => (
            <li key={title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div><h3>{title}</h3><p>{text}</p></div>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing-faq" id="faq">
        <div className="landing-faq__heading">
          <p className="eyebrow eyebrow--gold">FAQ</p>
          <h2>{page.locale === "en" ? "Before the first conversation" : page.locale === "uk" ? "Перед першою розмовою" : "Перед первым разговором"}</h2>
        </div>
        <div className="faq-list">
          {page.faqs.map((faq, index) => (
            <details key={faq.question} open={index === 0}>
              <summary>{faq.question}</summary>
              <p>{faq.answer}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="landing-final">
        <p className="eyebrow">{page.country}</p>
        <h2>{copy.finalTitle}</h2>
        <p>{copy.finalText}</p>
        <button type="button" className="button button--champagne" onClick={openLead}>{page.offer}</button>
      </section>

      <footer className="landing-footer">
        <Link href="/real-estate" className="brand brand--light"><span>SKY</span>INVEST</Link>
        <p>{page.locale === "en" ? "Overseas property, selected for a real plan." : page.locale === "uk" ? "Закордонна нерухомість під реальний план." : "Зарубежная недвижимость под реальный план."}</p>
        <Link href="/privacy">{copy.privacy}</Link>
      </footer>
      <button type="button" className="mobile-sticky mobile-sticky--gold" onClick={openLead}>{copy.request}</button>
      <LeadModal open={modalOpen} onClose={() => setModalOpen(false)} tone="dark" source={page.slug} locale={page.locale} offer={page.offer} />
    </main>
  );
}
