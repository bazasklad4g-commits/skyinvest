import Link from "next/link";

// The GTM trigger `Trigger - form_submit_consult` fires on a page view whose URL
// contains "thanks", and the Google Ads conversion hangs on that trigger. The
// lead form sends people here only after both steps went through, so a view of
// this page is one finished lead.
export const metadata = {
  title: "Запрос принят",
  description: "Запрос отправлен эксперту SkyInvest.",
  robots: { index: false, follow: false },
};

const copy = {
  ru: {
    kicker: "Заявка",
    title: "Запрос принят",
    text: "Эксперт напишет в выбранный мессенджер после просмотра запроса.",
    more: "Если вы указали несколько стран, в ответе будет сравнение по каждой из них: условия владения, порядок сделки и расходы после покупки.",
    back: "Вернуться на страницу",
  },
  uk: {
    kicker: "Заявка",
    title: "Запит прийнято",
    text: "Експерт напише у вибраний месенджер після перегляду запиту.",
    more: "Якщо ви вказали кілька країн, у відповіді буде порівняння по кожній із них: умови володіння, порядок угоди та витрати після купівлі.",
    back: "Повернутися на сторінку",
  },
  en: {
    kicker: "Request",
    title: "Request received",
    text: "An expert will write to you in the messenger you selected after reviewing the brief.",
    more: "If you chose several countries, the reply will compare each of them: ownership rules, how the deal works and the costs after purchase.",
    back: "Return to the page",
  },
};

type Props = { searchParams: Promise<{ l?: string; from?: string }> };

export default async function ThanksPage({ searchParams }: Props) {
  const { l, from } = await searchParams;
  const locale = l === "uk" || l === "en" ? l : "ru";
  const t = copy[locale];
  // Only a path on this site: never an outside address.
  const back = from && from.startsWith("/") && !from.startsWith("//") ? from : "/real-estate";
  return (
    <main className="legal-page" lang={locale}>
      <Link className="brand brand--dark" href="/real-estate"><span>SKY</span>INVEST</Link>
      <p className="eyebrow eyebrow--ink">{t.kicker}</p>
      <h1>{t.title}</h1>
      <p>{t.text}</p>
      <p>{t.more}</p>
      <Link className="button button--emerald" href={back}>{t.back}</Link>
    </main>
  );
}
