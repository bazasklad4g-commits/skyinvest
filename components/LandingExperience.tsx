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
    proofKicker: "Карта проверки",
    proofTitle: "Покупать объект — не значит верить рендеру.",
    proofText: "Сначала собираем факты по проекту и локации, затем показываем, что в них сильного, где есть риск и что нужно уточнить до решения.",
    proofItems: [
      ["01", "Документы и права", "Проверяем, какие документы есть у проекта и что именно покупает инвестор."],
      ["02", "Застройщик", "Смотрим прошлые проекты, темп стройки и логику обязательств в договоре."],
      ["03", "Финмодель", "Разделяем выручку, расходы и сценарии, чтобы доходность не жила только в презентации."],
      ["04", "Выход из сделки", "Разбираем ликвидность, спрос на перепродажу и план Б, если ваш сценарий изменится."],
    ],
    dossierTitle: "Восемь пунктов, которые должны выдержать проверку",
    dossierText: "Земля, разрешения, договор, сроки, темп строительства, рынок аренды, управляющая компания и сценарий выхода. Мы не заменяем юристов, зато помогаем прийти к ним с правильными вопросами.",
    dossierCta: "Получить карту проверки",
    questionsKicker: "Вместо выдуманных отзывов",
    questionsTitle: "Хороший объект отвечает на неудобные вопросы.",
    questions: [
      ["Почему эта локация?", "Сравниваем спрос, сезонность, инфраструктуру и предложение вокруг, а не только вид из окна."],
      ["Откуда берётся прогноз?", "Показываем допущения финмодели и отдельно называем то, чего рынок не гарантирует."],
      ["Что будет, если планы изменятся?", "Обсуждаем варианты использования, аренды и выхода ещё до бронирования."],
      ["Какие условия можно запросить?", "Фиксируем вопросы к застройщику и запрашиваем доступные условия напрямую."],
    ],
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
    proofKicker: "Карта перевірки",
    proofTitle: "Купити об'єкт — не означає повірити рендеру.",
    proofText: "Спершу збираємо факти про проєкт і локацію, а потім показуємо сильні сторони, ризики та питання, які варто закрити до рішення.",
    proofItems: [
      ["01", "Документи й права", "Перевіряємо, які документи має проєкт і що саме купує інвестор."],
      ["02", "Забудовник", "Дивимося попередні проєкти, темп будівництва та логіку зобов'язань у договорі."],
      ["03", "Фінмодель", "Відокремлюємо виручку, витрати й сценарії, щоб дохідність не жила лише в презентації."],
      ["04", "Вихід з угоди", "Розбираємо ліквідність, попит на перепродаж і план Б, якщо ваш сценарій зміниться."],
    ],
    dossierTitle: "Вісім пунктів, які мають витримати перевірку",
    dossierText: "Земля, дозволи, договір, строки, темп будівництва, ринок оренди, керуюча компанія та сценарій виходу. Ми не замінюємо юристів, але допомагаємо прийти до них із правильними питаннями.",
    dossierCta: "Отримати карту перевірки",
    questionsKicker: "Замість вигаданих відгуків",
    questionsTitle: "Хороший об'єкт відповідає на незручні запитання.",
    questions: [
      ["Чому ця локація?", "Порівнюємо попит, сезонність, інфраструктуру та пропозицію поруч, а не лише вид із вікна."],
      ["Звідки береться прогноз?", "Показуємо припущення фінмоделі й окремо називаємо те, чого ринок не гарантує."],
      ["Що буде, якщо плани зміняться?", "Обговорюємо використання, оренду та вихід ще до бронювання."],
      ["Які умови можна запросити?", "Фіксуємо питання до забудовника й запитуємо доступні умови напряму."],
    ],
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
    proofKicker: "The review map",
    proofTitle: "Buying a property should not mean trusting a render.",
    proofText: "We collect the facts around a project and location first, then show what holds up, where the risk sits, and what needs answering before a decision.",
    proofItems: [
      ["01", "Documents and rights", "We check the documents behind a project and what an investor is actually acquiring."],
      ["02", "Developer", "We look at prior projects, build pace, and the obligations written into the agreement."],
      ["03", "Financial model", "Revenue, costs, and scenarios are separated so the projected return does not live only in a brochure."],
      ["04", "Exit path", "We discuss liquidity, resale demand, and a plan B if your use case changes."],
    ],
    dossierTitle: "Eight points a property should withstand",
    dossierText: "Land, permits, agreement, delivery, construction pace, rental market, management, and an exit path. We do not replace lawyers; we help you arrive with the questions worth asking.",
    dossierCta: "Get the review map",
    questionsKicker: "Instead of invented reviews",
    questionsTitle: "A good property can take an uncomfortable question.",
    questions: [
      ["Why this location?", "We compare demand, seasonality, infrastructure, and nearby supply, not only the view."],
      ["Where does the forecast come from?", "We show model assumptions and name the things a market cannot guarantee."],
      ["What if the plan changes?", "Use, rental, and exit options are discussed before a reservation."],
      ["What terms can be requested?", "We put the questions to a developer and ask directly about the currently available terms."],
    ],
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

      <section className="landing-proof" aria-label={copy.proofKicker}>
        <div className="landing-proof__intro">
          <p className="eyebrow eyebrow--gold">{copy.proofKicker}</p>
          <h2>{copy.proofTitle}</h2>
          <p>{copy.proofText}</p>
        </div>
        <div className="landing-proof__grid">
          {copy.proofItems.map(([number, title, text]) => (
            <article key={number}>
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-dossier">
        <div className="landing-dossier__image" style={{ backgroundImage: `url(${page.regions[1]?.image ?? page.regions[0].image})` }} />
        <div className="landing-dossier__copy">
          <p className="eyebrow eyebrow--gold">SkyInvest / 08</p>
          <h2>{copy.dossierTitle}</h2>
          <p>{copy.dossierText}</p>
          <button type="button" className="button button--champagne" onClick={openLead}>{copy.dossierCta}</button>
        </div>
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

      <section className="landing-questions">
        <div className="landing-questions__heading">
          <p className="eyebrow eyebrow--gold">{copy.questionsKicker}</p>
          <h2>{copy.questionsTitle}</h2>
        </div>
        <div className="landing-questions__grid">
          {copy.questions.map(([title, text], index) => (
            <article key={title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
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
