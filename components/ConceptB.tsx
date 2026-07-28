"use client";

import Link from "next/link";
import { useState } from "react";
import LeadModal from "./LeadModal";

export default function ConceptB() {
  const [modalOpen, setModalOpen] = useState(false);
  const openLead = () => setModalOpen(true);

  return (
    <main className="concept-b">
      <header className="b-nav">
        <div className="brand brand--dark"><span>SKY</span>INVEST</div>
        <nav>
          <a href="#method">Метод</a>
          <a href="#markets">Рынки</a>
          <a href="#guide">Гайд</a>
        </nav>
        <button onClick={openLead}>Обсудить задачу <span>↗</span></button>
      </header>

      <section className="b-hero">
        <div className="b-hero__copy">
          <p className="b-label">Независимый подбор зарубежной недвижимости</p>
          <h1>Покупка за рубежом начинается <em>не с каталога</em></h1>
          <p>
            Сначала цель, горизонт и допустимый риск. После этого эксперт собирает 15 объектов и пишет вам в удобный мессенджер.
          </p>
          <button className="button button--emerald" onClick={openLead}>Собрать мою подборку <span>→</span></button>
          <small>Первый шаг займёт меньше минуты: мессенджер и телефон.</small>
        </div>
        <div className="b-hero__visual">
          <div className="b-hero__stamp">PRIVATE<br />SELECTION</div>
          <div className="b-hero__caption"><span>В фокусе</span><strong>Бали · Испания · Турция · Дубай</strong></div>
        </div>
      </section>

      <section className="b-method" id="method">
        <div className="b-section-title">
          <p className="b-label">01 / Метод</p>
          <h2>Мы сокращаем выбор,<br />а не расширяем его.</h2>
        </div>
        <div className="b-method__grid">
          <article><span>01</span><h3>Задача</h3><p>Для жизни, аренды, переезда или диверсификации капитала.</p></article>
          <article><span>02</span><h3>Фильтр</h3><p>Отсекаем объекты без понятной логики покупки и выхода.</p></article>
          <article><span>03</span><h3>Разбор</h3><p>Объясняем различия человеческим языком, без рекламной мишуры.</p></article>
          <article><span>04</span><h3>Сопровождение</h3><p>Организуем коммуникацию и проверку по ходу сделки.</p></article>
        </div>
      </section>

      <section className="b-markets" id="markets">
        <div className="b-markets__aside">
          <p className="b-label b-label--light">02 / Направления</p>
          <h2>Одна цель.<br />Разные рынки.</h2>
          <p>Страна должна подходить под ваш сценарий, а не под красивую рекламную кампанию.</p>
          <button onClick={openLead}>Сравнить направления →</button>
        </div>
        <div className="b-market-list">
          <article><span>01</span><div><h3>Испания</h3><p>Жизнь у моря · Аликанте · Коста-Бланка</p></div><b>↗</b></article>
          <article><span>02</span><div><h3>Бали</h3><p>Курортная аренда · виллы · управление</p></div><b>↗</b></article>
          <article><span>03</span><div><h3>Дубай</h3><p>Новые проекты · рассрочка · ликвидность</p></div><b>↗</b></article>
          <article><span>04</span><div><h3>Турция</h3><p>Переезд · море · большой выбор регионов</p></div><b>↗</b></article>
        </div>
      </section>

      <section className="b-guide" id="guide">
        <div className="b-guide__cover">
          <span>SKYINVEST / 2026</span>
          <strong>15 объектов<br />для частного<br />инвестора</strong>
          <i>PRIVATE BRIEF №01</i>
        </div>
        <div className="b-guide__copy">
          <p className="b-label">Закрытый инвестиционный бриф</p>
          <h2>Получите не прайс, а рабочую выборку</h2>
          <p>Внутри будут объекты, которые подходят под выбранную страну, бюджет и план использования. Эксперт добавит пояснения в сообщении.</p>
          <ul>
            <li>15 объектов под ваш запрос</li>
            <li>Сильные и слабые стороны каждого сценария</li>
            <li>Вопросы, которые стоит задать до сделки</li>
          </ul>
          <button className="button button--emerald" onClick={openLead}>Отправить бриф в мессенджер</button>
        </div>
      </section>

      <section className="b-final">
        <p className="b-label b-label--light">Начать с двух ответов</p>
        <h2>Страна может быть неизвестна.<br />Цель должна быть ясной.</h2>
        <button onClick={openLead}>Получить консультацию эксперта <span>→</span></button>
      </section>

      <footer className="b-footer">
        <div className="brand brand--dark"><span>SKY</span>INVEST</div>
        <p>Подбор недвижимости за рубежом.</p>
        <Link href="/">← Сравнить концепции</Link>
      </footer>
      <button className="mobile-sticky mobile-sticky--green" onClick={openLead}>Собрать подборку</button>
      <LeadModal open={modalOpen} onClose={() => setModalOpen(false)} tone="light" source="concept-b" />
    </main>
  );
}
