import Link from "next/link";

export const metadata = { title: "Политика конфиденциальности", description: "Как SkyInvest обрабатывает обращения с сайта." };

export default function PrivacyPage() {
  return <main className="legal-page"><Link className="brand brand--dark" href="/real-estate"><span>SKY</span>INVEST</Link><p className="eyebrow eyebrow--ink">Legal</p><h1>Политика конфиденциальности</h1><p>Когда вы оставляете номер и выбираете мессенджер, мы используем эти данные только для ответа на ваш запрос и подготовки подборки недвижимости.</p><p>Данные не публикуются на сайте. Доступ к ним получают только сотрудники, которые обрабатывают обращение. Вы можете попросить удалить данные, ответив на сообщение менеджера.</p><p>На сайте могут использоваться технические cookie и рекламные метки для понимания источника обращения. Рекламные и аналитические сервисы подключаются только после их настройки в проекте.</p><Link className="button button--emerald" href="/real-estate">Вернуться к подбору</Link></main>;
}
