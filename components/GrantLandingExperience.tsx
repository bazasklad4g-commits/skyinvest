"use client";

import Link from "next/link";
import { useState } from "react";
import type { GrantLandingPage } from "../content/grant-landing-pages";
import LeadModal from "./LeadModal";

type Props = { page: GrantLandingPage };

const projectUrl = "https://www.nezalezhnist.org.ua/";

function seoCopy(page: GrantLandingPage) {
  const places = page.regions.map((region) => region.name).join(", ");
  return [
    `Материал по теме «${page.h1}» помогает подготовиться до обращения к посреднику или обсуждения конкретного объекта. ${page.heroText}`,
    `Внутри есть контекст для сравнения: ${places}. ${page.introText}`,
    `${page.guideText} Материал не заменяет юридическое заключение, но помогает прийти к специалисту с понятными фактами и вопросами.`,
  ];
}

export default function GrantLandingExperience({ page }: Props) {
  const [modalOpen, setModalOpen] = useState(false);
  const seo = seoCopy(page);
  const openLead = () => setModalOpen(true);

  return (
    <main className="landing grant-landing" lang="ru">
      <header className="landing-nav">
        <Link href="/real-estate" className="brand brand--light" aria-label="SkyInvest home"><span>SKY</span>INVEST</Link>
        <nav aria-label="Навигация по странице">
          <a href="#material">Материал</a>
          <a href="#countries">Страны</a>
          <a href="#faq">Вопросы</a>
        </nav>
        <button type="button" onClick={openLead}>{page.offer}</button>
      </header>

      <section className="landing-hero">
        <div className="landing-hero__image" style={{ backgroundImage: `url(${page.heroImage})`, backgroundPosition: page.heroPosition ?? "center" }} />
        <div className="landing-hero__shade" />
        <div className="landing-hero__content">
          <p className="eyebrow">{page.eyebrow}</p>
          <h1>{page.h1}</h1>
          <p className="landing-hero__lead">{page.heroText}</p>
          <div className="landing-hero__actions">
            <button type="button" className="button button--champagne" onClick={openLead}>{page.offer}</button>
            <a href="#material">Посмотреть, что внутри ↓</a>
          </div>
          <div className="landing-hero__trust" aria-label="Принципы проекта">
            <span>бесплатный материал</span><span>без прайса на странице</span><span>ответ в мессенджере</span>
          </div>
        </div>
        <span className="landing-hero__number">01 / GUIDE</span>
      </section>

      <section className="trust-strip" aria-label="Формат помощи">
        <div><strong>01</strong><span>понятная карта вопроса</span></div>
        <div><strong>02</strong><span>материал для самостоятельной проверки</span></div>
        <div><strong>03</strong><span>контакт в удобном мессенджере</span></div>
      </section>

      <section className="landing-intro">
        <p className="section-index">01</p>
        <div><p className="eyebrow eyebrow--gold">Без лишнего шума</p><h2>{page.introTitle}</h2></div>
        <p>{page.introText}</p>
      </section>

      <section className="landing-proof" aria-label="Карта проверки">
        <div className="landing-proof__intro"><p className="eyebrow eyebrow--gold">Карта проверки</p><h2>{page.proofTitle}</h2><p>{page.proofText}</p></div>
        <div className="landing-proof__grid">
          {page.proofItems.map(([number, title, text]) => <article key={number}><span>{number}</span><h3>{title}</h3><p>{text}</p></article>)}
        </div>
      </section>

      <section className="landing-dossier">
        <div className="landing-dossier__image" style={{ backgroundImage: `url(${page.guideImage})` }} />
        <div className="landing-dossier__copy"><p className="eyebrow eyebrow--gold">ГО «Незалежність»</p><h2>{page.guideTitle}</h2><p>{page.guideText}</p><button type="button" className="button button--champagne" onClick={openLead}>{page.offer}</button></div>
      </section>

      <section className="landing-guide" id="material">
        <div className="landing-guide__image" style={{ backgroundImage: `url(${page.guideImage})` }}><span>Бесплатный материал</span><strong>{page.guideMark}</strong><i>в выбранный мессенджер</i></div>
        <div className="landing-guide__copy"><p className="eyebrow eyebrow--gold">Что внутри</p><h2>Материал, с которым проще вести разговор.</h2><p>Его можно открыть до встречи, отметить нужные пункты и вернуться к ним, когда появятся документы или условия конкретного проекта.</p><ul>{page.guidePoints.map((point) => <li key={point}>{point}</li>)}</ul><button type="button" className="button button--emerald" onClick={openLead}>{page.offer}</button></div>
      </section>

      <section className="region-section" id="countries">
        <div className="section-heading"><p className="eyebrow eyebrow--gold">Страны и контекст</p><h2>{page.regionTitle}</h2></div>
        <div className="region-grid">{page.regions.map((region, index) => <article className="region-card" key={region.name}><div className="region-card__image" style={{ backgroundImage: `url(${region.image})` }} /><div className="region-card__shade" /><div className="region-card__copy"><span>{String(index + 1).padStart(2, "0")}</span><h3>{region.name}</h3><p>{region.description}</p><button type="button" onClick={openLead}>{page.offer}</button></div></article>)}</div>
      </section>

      <section className="seo-notes" aria-label={`Справка: ${page.h1}`}>
        <p className="eyebrow eyebrow--gold">Справка по теме</p>
        <h2>{page.h1}</h2>
        {seo.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
      </section>

      <section className="landing-questions">
        <div className="landing-questions__heading"><p className="eyebrow eyebrow--gold">До следующего шага</p><h2>{page.questionsTitle}</h2></div>
        <div className="landing-questions__grid">{page.questions.map(([title, text], index) => <article key={title}><span>{String(index + 1).padStart(2, "0")}</span><h3>{title}</h3><p>{text}</p></article>)}</div>
      </section>

      <section className="review-section">
        <div className="review-section__image" style={{ backgroundImage: `url(${page.regions.at(-1)?.image ?? page.heroImage})` }} />
        <div className="review-section__copy"><p className="eyebrow eyebrow--gold">Благотворительная миссия</p><h2>{page.slug === "proverka-zastrojshchika" ? "Знания о рисках сделки должны быть доступны до первого платежа." : "Материал подготовлен в рамках просветительской работы ГО «Незалежність»."}</h2><p>{page.slug === "proverka-zastrojshchika" ? "ГО «Незалежність» делает базовые материалы о проверке зарубежной недвижимости открытыми: чтобы человек мог задать нужные вопросы до разговора о деньгах, а не после него. Это постоянная часть образовательной и благотворительной миссии организации." : "Организация публикует бесплатные материалы, которые помогают людям разобраться в вопросе до обращения к коммерческим предложениям. Подробности о проектах и миссии есть на основном сайте ГО «Незалежність»."}</p><button type="button" className="button button--champagne" onClick={openLead}>{page.offer}</button><p className="grant-project-link"><a href={projectUrl} target="_blank" rel="noreferrer">Открыть сайт организации ↗</a></p></div>
      </section>

      <section className="landing-faq" id="faq">
        <div className="landing-faq__heading"><p className="eyebrow eyebrow--gold">FAQ</p><h2>Перед первым разговором</h2></div>
        <div className="faq-list">{page.faqs.map((faq, index) => <details key={faq.question} open={index === 0}><summary>{faq.question}</summary><p>{faq.answer}</p></details>)}</div>
      </section>

      <section className="landing-final"><p className="eyebrow">Бесплатный материал</p><h2>Нужна ясная точка, с которой можно начать?</h2><p>Оставьте контакт в привычном мессенджере, и мы отправим материал по этой теме.</p><button type="button" className="button button--champagne" onClick={openLead}>{page.offer}</button></section>

      <footer className="landing-footer"><Link href="/real-estate" className="brand brand--light"><span>SKY</span>INVEST</Link><p>Проект ГО «Незалежність». Бесплатные образовательные материалы о рисках и осознанном выборе зарубежной недвижимости.</p><Link href="/privacy">Политика конфиденциальности</Link></footer>
      <button type="button" className="mobile-sticky mobile-sticky--gold" onClick={openLead}>{page.offer}</button>
      <LeadModal open={modalOpen} onClose={() => setModalOpen(false)} tone="dark" source={page.slug} locale="ru" offer={page.offer} />
    </main>
  );
}
