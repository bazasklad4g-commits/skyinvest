"use client";

import Link from "next/link";
import { useState } from "react";
import type { LandingPage, SeoSection } from "../content/landing-pages";
import LeadModal from "./LeadModal";
import LeadTeaser from "./LeadTeaser";

type Props = { page: LandingPage };

function seoCopy(page: LandingPage) {
  const locations = page.regions.map((region) => region.name).join(", ");
  // A page may carry its own article. Only then does this section say something
  // the reader has not already read higher up.
  if (page.seoSections && page.seoSections.length > 0) {
    return { title: page.seoTitle ?? page.introTitle, paragraphs: [] as string[], sections: page.seoSections };
  }
  if (page.locale === "uk") {
    return {
      title: `${page.country}: що порівняти до вибору об’єкта`,
      paragraphs: [
        `Запит про ${page.country.toLowerCase()} рідко починається з конкретного будинку. Спершу варто звірити мету, ритм місця й формат використання. ${page.heroText}`,
        `На цій сторінці зібрані орієнтири для першого порівняння: ${locations}. ${page.introText}`,
        `${page.guideText} Це дає предметний список питань перед переглядом об’єкта та розмовою з профільним фахівцем.`,
      ],
      sections: [] as SeoSection[],
    };
  }
  if (page.locale === "en") {
    return {
      title: `${page.country}: what to compare before choosing a property`,
      paragraphs: [
        `A search for property in ${page.country} rarely starts with one specific home. Start by comparing the purpose, the pace of the location, and how the property will be used. ${page.heroText}`,
        `This page gives a first frame for ${locations}. ${page.introText}`,
        `${page.guideText} It leaves you with a useful set of questions before viewing a property or speaking with a local specialist.`,
      ],
      sections: [] as SeoSection[],
    };
  }
  return {
    title: `${page.country}: как выбрать объект и не упустить важное`,
    paragraphs: [
      `Покупка недвижимости в ${page.country.toLowerCase()} начинается не с первой понравившейся квартиры. Сначала стоит понять, для чего вам объект, как часто вы будете им пользоваться и что для вас неприемлемо. ${page.heroText}`,
      `Для первого сравнения мы собрали ${locations}. ${page.introText}`,
      `${page.guideText} До просмотра у вас будет список вопросов к объекту, документам и продавцу.`,
    ],
    sections: [] as SeoSection[],
  };
}

const labels = {
  ru: {
    privateSelection: "Личный подбор",
    directions: "Направления",
    approach: "Как работаем",
    answers: "Вопросы",
    request: "Получить подборку",
    explore: "Посмотреть направления",
    tailored: "Подбор под вашу задачу",
    messenger: "Ответ в мессенджере",
    noShowcase: "Только актуальные варианты",
    trustMetrics: [
      ["12 лет", "практики команды и партнёров"],
      ["700+", "отзывов и рекомендаций"],
      ["1 окно", "для подбора, проверки и сделки"],
    ],
    serviceKicker: "Проверка до бронирования",
    serviceTitle: "Сначала проверяем главное, потом говорим об объекте.",
    serviceText: "Красивых рендеров достаточно у всех. Мы смотрим документы, условия договора, расходы и репутацию проекта, чтобы в подборке были не только эффектные картинки.",
    serviceItems: [
      ["Подбор", "Отбираем варианты по стране, срокам и цели покупки, а не по самой громкой цифре в рекламе."],
      ["Проверка", "Собираем вопросы по проекту, договору, земле, срокам и управлению объектом."],
      ["Переговоры", "Помогаем задать застройщику нужные вопросы и сверить условия, которые доступны сейчас."],
      ["После сделки", "Остаёмся рядом, если нужно вернуться к документам, аренде или следующей покупке."],
    ],
    reviewsKicker: "Люди приходят не за витриной",
    reviewsTitle: "Отзывы без вымышленных историй.",
    reviewsText: "По запросу пришлём отзывы и кейсы с понятной задачей клиента, страной и результатом работы. Без анонимных восторгов и скриншотов без контекста.",
    reviewsCta: "Получить отзывы и кейсы",
    notCatalog: "Не каталог ради каталога",
    proofKicker: "Карта проверки",
    proofTitle: "Рендер продаёт мечту. Решение принимают по фактам.",
    proofText: "Собираем сведения о проекте и локации, отмечаем сильные стороны, риски и вопросы, на которые нужен ответ до бронирования.",
    proofItems: [
      ["01", "Документы и права", "Проверяем, какие документы есть у проекта и что именно покупает инвестор."],
      ["02", "Застройщик", "Смотрим прошлые проекты, темп стройки и логику обязательств в договоре."],
      ["03", "Финмодель", "Отделяем выручку от расходов, чтобы доходность не оставалась цифрой из презентации."],
      ["04", "Выход из сделки", "Смотрим ликвидность, спрос на перепродажу и варианты, если планы изменятся."],
    ],
    dossierTitle: "Что нужно выяснить до решения",
    dossierText: "Земля, разрешения, договор, сроки, ход строительства, аренда, управляющая компания и перепродажа. Мы не заменяем юриста, но помогаем прийти к нему с конкретными вопросами и документами.",
    dossierCta: "Получить карту проверки",
    questionsKicker: "Вместо выдуманных отзывов",
    questionsTitle: "Хороший объект не боится прямых вопросов.",
    questions: [
      ["Почему эта локация?", "Сравниваем спрос, сезонность, инфраструктуру и предложение вокруг, а не только вид из окна."],
      ["Откуда берётся прогноз?", "Разбираем расчёт и отдельно называем то, чего рынок не гарантирует."],
      ["Что будет, если планы изменятся?", "Обсуждаем варианты использования, аренды и выхода ещё до бронирования."],
      ["Какие условия можно запросить?", "Фиксируем вопросы к застройщику и запрашиваем доступные условия напрямую."],
    ],
    regions: "Локации",
    method: "Как строится работа",
    stepsTitle: "Как проходит работа",
    finalTitle: "Нужна подборка под ваш план?",
    finalText: "Оставьте номер в мессенджере. Сначала уточним задачу, затем отправим короткий список направлений или объектов.",
    privacy: "Политика конфиденциальности",
    seoKicker: "Справка по направлению",
    shortlistKicker: "Индивидуальная подборка",
    countryLinks: "Другие направления",
    steps: [
      ["Запрос", "Выбираете мессенджер и оставляете номер. Страна может быть уже выбрана или пока нет."],
      ["Короткий разговор", "Уточняем, для чего нужен объект, какие сроки у вас и что точно не подходит."],
      ["Подборка", "Присылаем варианты под вашу задачу и объясняем, что в них сравнивать."],
      ["Следующий шаг", "Если варианты подходят, обсуждаем детали и планируем дальнейшие действия."],
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
    trustMetrics: [
      ["12 років", "практики команди й партнерів"],
      ["700+", "відгуків і рекомендацій"],
      ["1 вікно", "для добірки, перевірки та угоди"],
    ],
    serviceKicker: "Перевірка до бронювання",
    serviceTitle: "Не надсилаємо об'єкт, поки не розуміємо, що за ним стоїть.",
    serviceText: "Замість гарного рендеру в першій добірці важливі документи, сценарій володіння, розрахунок витрат і питання до забудовника. Якщо на питання немає зрозумілої відповіді, це теж результат перевірки.",
    serviceItems: [
      ["Добірка", "Збираємо короткий список за метою, країною та горизонтом, а не за найвищою заявленою дохідністю."],
      ["Перевірка", "Фіксуємо, що варто перевірити щодо проєкту, договору, ділянки, строків і моделі управління."],
      ["Переговори", "Допомагаємо зібрати питання до забудовника та звірити доступні на момент запиту умови."],
      ["Після угоди", "Залишаємося на зв'язку, коли треба повернутися до документів, управління або наступного рішення."],
    ],
    reviewsKicker: "Люди приходять не за вітриною",
    reviewsTitle: "Відгуки, у яких можна перевірити контекст.",
    reviewsText: "За запитом надішлемо добірку реальних відгуків і кейсів із задачею клієнта, країною та тим, що саме порівнювали. Не публікуємо анонімні захоплені слова без деталей.",
    reviewsCta: "Отримати відгуки й кейси",
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
    seoKicker: "Довідка про напрямок",
    shortlistKicker: "Індивідуальна добірка",
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
    trustMetrics: [
      ["12 years", "of combined team and partner practice"],
      ["700+", "reviews and recommendations"],
      ["One team", "for selection, review, and the deal"],
    ],
    serviceKicker: "Review before a reservation",
    serviceTitle: "We do not send a property until we understand what sits behind it.",
    serviceText: "A beautiful render is not enough. The first shortlist should cover documents, ownership structure, costs, and the questions a developer needs to answer. An unclear answer is useful information too.",
    serviceItems: [
      ["Selection", "A concise list built around the purpose, country, and timing, rather than the largest projected return."],
      ["Review", "We outline what needs checking in the project, agreement, plot, delivery, and management model."],
      ["Negotiation", "We help frame questions for a developer and compare the terms available at the time of the request."],
      ["After the deal", "We remain available when you need to revisit paperwork, management, or the next decision."],
    ],
    reviewsKicker: "People do not come for a listing feed",
    reviewsTitle: "Reviews with context you can inspect.",
    reviewsText: "On request, we will send real reviews and cases with the client brief, country, and what was compared. We do not publish anonymous praise without a useful detail.",
    reviewsCta: "Get reviews and cases",
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
    seoKicker: "About this destination",
    shortlistKicker: "A tailored shortlist",
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
  { id: "georgia", href: "/gruziya-ru", ru: "Грузия", uk: "Грузія", en: "Georgia" },
  { id: "cambodia", href: "/kambodzha-ru", ru: "Камбоджа", uk: "Камбоджа", en: "Cambodia" },
  { id: "maldives", href: "/maldivy-ru", ru: "Мальдивы", uk: "Мальдіви", en: "Maldives" },
  { id: "citizenship", href: "/grazhdanstvo-grenady", ru: "Гражданство", uk: "Громадянство", en: "Citizenship guides" },
  { id: "more", href: "/real-estate", ru: "Другие страны", uk: "Інші країни", en: "More countries" },
];

export default function LandingExperience({ page }: Props) {
  const [modalOpen, setModalOpen] = useState(false);
  const [leadOffer, setLeadOffer] = useState(page.offer);
  const copy = labels[page.locale];
  const seo = seoCopy(page);
  const openLead = (offer = page.offer) => { setLeadOffer(offer); setModalOpen(true); };

  // Google Ads reads the top of the page when it suggests keywords for a campaign.
  // A hand-written article is therefore placed high, right after the trust strip;
  // the auto-assembled fallback stays where it was, low, since it only repeats copy.
  const seoHigh = seo.sections.length > 0;
  const seoBlock = (
    <section className="seo-notes" aria-label={seo.title}>
      <p className="eyebrow eyebrow--gold">{copy.seoKicker}</p>
      <h2>{seo.title}</h2>
      {seo.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
      {seo.sections.map((section) => (
        <div key={section.heading}>
          <h3>{section.heading}</h3>
          <p>{section.text}</p>
        </div>
      ))}
    </section>
  );

  return (
    <main className="landing" lang={page.locale}>
      <header className="landing-nav">
        <Link href="/real-estate" className="brand brand--light" aria-label="SkyInvest home"><span>SKY</span>INVEST</Link>
        <nav aria-label="Page navigation">
          <a href="#locations">{copy.directions}</a>
          <a href="#process">{copy.approach}</a>
          <a href="#faq">{copy.answers}</a>
        </nav>
        <button type="button" onClick={() => openLead(copy.request)}>{copy.request}</button>
      </header>

      <section className="landing-hero">
        <div className="landing-hero__image" style={{ backgroundImage: `url(${page.heroImage})`, backgroundPosition: page.heroPosition ?? "center" }} />
        <div className="landing-hero__shade" />
        <div className="landing-hero__content">
          <p className="eyebrow">{copy.privateSelection} · {page.country}</p>
          <h1>{page.h1}</h1>
          <p className="landing-hero__lead">{page.heroText}</p>
          <LeadTeaser
            title={page.locale === "en" ? "Where should we send the shortlist?"
              : page.locale === "uk" ? "Куди надіслати добірку?" : "Куда отправить подборку?"}
            action={page.offer} onOpen={openLead} locale={page.locale} />
          <div className="landing-hero__actions">
            <a href="#locations">{copy.explore} ↓</a>
          </div>
          <div className="landing-hero__trust" aria-label="Service principles">
            <span>{copy.tailored}</span>
            <span>{copy.messenger}</span>
            <span>{copy.noShowcase}</span>
          </div>
        </div>
        <span className="landing-hero__number">{page.country}</span>
      </section>

      <section className="trust-strip" aria-label="SkyInvest service proof">
        {copy.trustMetrics.map(([value, label]) => (
          <div key={value}>
            <strong>{value}</strong>
            <span>{label}</span>
          </div>
        ))}
      </section>

      {seoHigh ? seoBlock : null}

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

      <section className="service-section">
        <div className="service-section__intro">
          <p className="eyebrow eyebrow--gold">{copy.serviceKicker}</p>
          <h2>{copy.serviceTitle}</h2>
          <p>{copy.serviceText}</p>
          <button type="button" className="button button--champagne" onClick={() => openLead(copy.dossierCta)}>{copy.dossierCta}</button>
        </div>
        <div className="service-section__grid">
          {copy.serviceItems.map(([title, text], index) => (
            <article key={title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-dossier">
        <div className="landing-dossier__image" style={{ backgroundImage: `url(${page.regions[1]?.image ?? page.regions[0].image})` }} />
        <div className="landing-dossier__copy">
          <p className="eyebrow eyebrow--gold">{page.locale === "en" ? "Checks before you buy"
            : page.locale === "uk" ? "Перевірка перед купівлею" : "Проверка перед покупкой"}</p>
          <h2>{copy.dossierTitle}</h2>
          <p>{copy.dossierText}</p>
          <button type="button" className="button button--champagne" onClick={() => openLead(copy.dossierCta)}>{copy.dossierCta}</button>
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
                <button type="button" onClick={() => openLead(copy.request)}>{copy.request}</button>
              </div>
            </article>
          ))}
        </div>
        {page.slug === "real-estate" && (
          <Link className="region-citizenship" href="/grazhdanstvo-grenady">
            <span>Гражданство</span>
            <strong>Гиды по проверке программ, документов и рисков →</strong>
          </Link>
        )}
      </section>

      {seoHigh ? null : seoBlock}

      <section className="landing-guide">
        <div className="landing-guide__image" style={{ backgroundImage: `url(${page.regions[0].image})` }}>
          <span>{page.country}</span>
          <strong>{page.country}</strong>
          <i>{page.offer}</i>
        </div>
        <div className="landing-guide__copy">
          <p className="eyebrow eyebrow--gold">{copy.shortlistKicker}</p>
          <h2>{page.guideTitle}</h2>
          <p>{page.guideText}</p>
          <ul>{page.guidePoints.map((point) => <li key={point}>{point}</li>)}</ul>
          <button type="button" className="button button--emerald" onClick={() => openLead(page.offer)}>{page.offer}</button>
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

      <section className="review-section">
        <div className="review-section__image" style={{ backgroundImage: `url(${page.regions[2]?.image ?? page.heroImage})` }} />
        <div className="review-section__copy">
          <p className="eyebrow eyebrow--gold">{copy.reviewsKicker}</p>
          <h2>{copy.reviewsTitle}</h2>
          <p>{copy.reviewsText}</p>
          <button type="button" className="button button--champagne" onClick={() => openLead(copy.reviewsCta)}>{copy.reviewsCta}</button>
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
        <button type="button" className="button button--champagne" onClick={() => openLead(page.offer)}>{page.offer}</button>
      </section>

      <footer className="landing-footer">
        <Link href="/real-estate" className="brand brand--light"><span>SKY</span>INVEST</Link>
        <p>{page.locale === "en" ? "Overseas property, selected for a real plan." : page.locale === "uk" ? "Закордонна нерухомість під реальний план." : "Зарубежная недвижимость под реальный план."}</p>
        <Link href="/privacy">{copy.privacy}</Link>
      </footer>
      <button type="button" className="mobile-sticky mobile-sticky--gold" onClick={() => openLead(copy.request)}>{copy.request}</button>
      <LeadModal open={modalOpen} onClose={() => setModalOpen(false)} tone="dark" source={page.slug} locale={page.locale} offer={leadOffer} />
    </main>
  );
}
