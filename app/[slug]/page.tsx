import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import GrantLandingExperience from "../../components/GrantLandingExperience";
import LandingExperience from "../../components/LandingExperience";
import { grantLandingPages, grantPagesBySlug } from "../../content/grant-landing-pages";
import { landingPages, pagesBySlug } from "../../content/landing-pages";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return [...landingPages, ...grantLandingPages].map(({ slug }) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const page = pagesBySlug[slug] ?? grantPagesBySlug[slug];
  if (!page) return {};
  const canonical = `/${page.slug}`;
  return {
    title: page.title,
    description: page.description,
    keywords: page.keywords,
    alternates: { canonical },
    openGraph: {
      title: page.title,
      description: page.description,
      url: canonical,
      type: "website",
      locale: "locale" in page && page.locale === "uk" ? "uk_UA" : "locale" in page && page.locale === "en" ? "en_US" : "ru_RU",
      images: "heroImage" in page ? [{ url: page.heroImage }] : undefined,
    },
  };
}

export default async function LandingPageRoute({ params }: Props) {
  const { slug } = await params;
  if (slug === "re") permanentRedirect("/real-estate");
  const grantPage = grantPagesBySlug[slug];
  if (grantPage) return <GrantLandingExperience page={grantPage} />;
  const page = pagesBySlug[slug];
  if (!page) notFound();
  return <LandingExperience page={page} />;
}
