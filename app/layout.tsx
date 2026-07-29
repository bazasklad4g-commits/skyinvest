import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://m.nezalezhnist.org.ua"),
  title: { default: "SkyInvest — недвижимость за рубежом", template: "%s | SkyInvest" },
  description: "Подбор зарубежной недвижимости под жизнь, отдых или инвестиции.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  // The container ID is public by design. Environment value lets us replace it per deployment.
  const gtmId = process.env.NEXT_PUBLIC_GTM_ID ?? "GTM-WLNZBWMX";
  return (
    <html lang="ru">
      <body>
        {gtmId && <Script id="gtm-base" strategy="afterInteractive">{`window.dataLayer=window.dataLayer||[];window.dataLayer.push({'gtm.start':new Date().getTime(),event:'gtm.js'});(function(w,d,s,l,i){var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','${gtmId}');`}</Script>}
        {children}
      </body>
    </html>
  );
}
