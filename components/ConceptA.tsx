"use client";

import Link from "next/link";
import { useState } from "react";
import LeadModal from "./LeadModal";

export default function ConceptA() {
  const [modalOpen, setModalOpen] = useState(false);
  const openLead = () => setModalOpen(true);

  return (
    <main className="concept-a">
      <header className="a-nav">
        <div className="brand brand--light"><span>SKY</span>INVEST</div>
        <nav aria-label="Основная навигация">
          <a href="#directions">Направления</a>
          <a href="#process">Как работаем</a>
          <a href="#answers">Вопросы</a>
        </nav>
        <button onClick={openLead}>Получить подборку</button>
      </header>

      <section className="a-hero">
        <div className="a-hero__shade" />
        <div className="a-hero__content">
          <p className="eyebrow">Private property selection · Bali</p>
          <h1>Недвижимость за рубежом,<br />которая работает на вашу цель</h1>
          <p className="a-hero__sub">
            Отберём 15 объектов под инвестицию, переезд или личное пользование. Без открытых прайсов, случайных вариантов и бесконечных созвонов.
          </p>
          <div className="a-hero__actions">
            <button className="button button--champagne" onClick={openLead}>Получить закрытый каталог</button>
            <a href="#directions">Посмотреть подход ↓</a>
          </div>
          <div className="a-hero__trust">
            <span>Подбор под запрос</span>
            <span>Контакт в мессенджере</span>
            <span>Сопровождение до сделки</span>
          </div>
        </div>
        <div className="a-hero__side-note">01 / БАЛИ</div>
      </section>

      <section className="a-intro" id="directions">
        <p className="section-index">01</p>
        <div>
          <p className="eyebrow eyebrow--gold">Не каталог ради каталога</p>
          <h2>Сначала разбираемся, зачем вам недвижимость. Потом показываем объекты.</h2>
        </div>
        <p className="a-intro__text">
          Один и тот же апартамент не может одинаково хорошо подходить для аренды, переезда и сохранения капитала. Поэтому общая база остаётся за кадром; вы получаете короткую выборку с понятной логикой.
        </p>
      </section>

      <section className="a-destinations">
        <article className="destination destination--bali">
          <div><span>01</span><h3>Бали</h3><p>Виллы, курортная аренда, управление объектом</p></div>
          <button onClick={openLead}>Получить подборку</button>
        </article>
        <article className="destination destination--spain">
          <div><span>02</span><h3>Испания</h3><p>Аликанте, Коста-Бланка, жильё у моря</p></div>
          <button onClick={openLead}>Получить подборку</button>
        </article>
        <article className="destination destination--dubai">
          <div><span>03</span><h3>Дубай</h3><p>Новые проекты, рассрочка, аренда</p></div>
          <button onClick={openLead}>Получить подборку</button>
        </article>
      </section>

      <section className="a-process" id="process">
        <div className="a-process__heading">
          <p className="eyebrow eyebrow--gold">Путь без лишнего шума</p>
          <h2>Четыре шага. Один человек на связи.</h2>
        </div>
        <ol>
          <li><span>01</span><div><h3>Запрос</h3><p>Фиксируем страну, задачу, бюджет и удобный мессенджер.</p></div></li>
          <li><span>02</span><div><h3>Короткая выборка</h3><p>Убираем всё, что не проходит под ваш сценарий.</p></div></li>
          <li><span>03</span><div><h3>Проверка</h3><p>Координируем документы, расчёты и вопросы по объекту.</p></div></li>
          <li><span>04</span><div><h3>Сделка</h3><p>Держим процесс в одном окне до получения ключей.</p></div></li>
        </ol>
      </section>

      <section className="a-lead-band">
        <div>
          <p className="eyebrow">Персональный выпуск · 15 объектов</p>
          <h2>Не знаете, с какой страны начать?</h2>
          <p>Сравним варианты под вашу цель и объясним, что отсеяли и почему.</p>
        </div>
        <button className="button button--champagne" onClick={openLead}>Получить каталог в мессенджер</button>
      </section>

      <section className="a-faq" id="answers">
        <p className="section-index">02</p>
        <div>
          <p className="eyebrow eyebrow--gold">Коротко о главном</p>
          <h2>Вопросы перед первым разговором</h2>
        </div>
        <div className="faq-list">
          <details open><summary>Почему на сайте нет цен?</summary><p>Финальные условия зависят от этапа проекта, способа оплаты и доступности. Вместо устаревшей витрины отправляем актуальную выборку под запрос.</p></details>
          <details><summary>Каталог действительно бесплатный?</summary><p>Да. Сначала вы получаете выборку и решаете, есть ли смысл обсуждать её с экспертом.</p></details>
          <details><summary>Можно выбрать несколько стран?</summary><p>Да. Сравним направления по вашей задаче, сроку покупки и плану использования объекта.</p></details>
          <details><summary>Что происходит после заявки?</summary><p>Эксперт пишет в выбранный мессенджер, уточняет контекст и отправляет подборку.</p></details>
        </div>
      </section>

      <footer className="a-footer">
        <div className="brand brand--light"><span>SKY</span>INVEST</div>
        <p>Зарубежная недвижимость под конкретную задачу.</p>
        <Link href="/">← Сравнить концепции</Link>
      </footer>
      <button className="mobile-sticky mobile-sticky--gold" onClick={openLead}>Получить каталог</button>
      <LeadModal open={modalOpen} onClose={() => setModalOpen(false)} tone="dark" source="concept-a" />
    </main>
  );
}
