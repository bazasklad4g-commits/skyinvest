import Link from "next/link";

export default function Home() {
  return (
    <main className="chooser">
      <div className="chooser__glow" />
      <section className="chooser__panel">
        <div className="brand brand--dark"><span>SKY</span>INVEST</div>
        <p className="eyebrow eyebrow--ink">Дизайн на утверждение · v0.1</p>
        <h1>Выберите направление для всех лендингов</h1>
        <p className="chooser__intro">
          Обе концепции адаптивны, не показывают цены и ведут в одну двухэтапную форму.
          Сейчас формы работают как прототип и никуда не отправляют данные.
        </p>
        <div className="chooser__grid">
          <Link className="concept-card concept-card--night" href="/concept-a">
            <span className="concept-card__number">01</span>
            <strong>Private Selection</strong>
            <span>Тёмная, кинематографичная, премиальная</span>
            <i>Открыть концепцию →</i>
          </Link>
          <Link className="concept-card concept-card--paper" href="/concept-b">
            <span className="concept-card__number">02</span>
            <strong>Investment Editorial</strong>
            <span>Светлая, редакционная, рациональная</span>
            <i>Открыть концепцию →</i>
          </Link>
        </div>
        <p className="chooser__note">Тексты и фотографии пока служат для проверки композиции.</p>
      </section>
    </main>
  );
}
