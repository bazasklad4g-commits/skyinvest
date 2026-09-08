import Link from "next/link";

// The GTM trigger `Trigger - form_submit_consult` fires on a page view whose URL
// contains "thanks". The route has to exist before that conversion can ever fire.
export const metadata = {
  title: "Запрос принят",
  description: "Запрос отправлен эксперту SkyInvest.",
  robots: { index: false, follow: false },
};

export default function ThanksPage() {
  return (
    <main className="legal-page">
      <Link className="brand brand--dark" href="/real-estate"><span>SKY</span>INVEST</Link>
      <p className="eyebrow eyebrow--ink">Заявка</p>
      <h1>Запрос принят</h1>
      <p>Эксперт напишет в выбранный мессенджер после просмотра запроса.</p>
      <p>Если вы указали несколько стран, в ответе будет сравнение по каждой из них: условия владения, порядок сделки и расходы после покупки.</p>
      <Link className="button button--emerald" href="/real-estate">Вернуться к подбору</Link>
    </main>
  );
}
