import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import LandingExperience from "../../components/LandingExperience";
import { landingPages, pagesBySlug } from "../../content/landing-pages";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return landingPages.map(({ slug }) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const page = pagesBySlug[slug];
  if (!page) return {};
  const canonical = `/${page.slug}`;
  return {
    title: page.title,
    description: page.description,
    keywords: page.keywords,
    alternates: { canonical },
    openGraph: { title: page.title, description: page.description, url: canonical, type: "website", locale: page.locale === "uk" ? "uk_UA" : page.locale === "en" ? "en_US" : "ru_RU" },
  };
}

export default async function LandingPageRoute({ params }: Props) {
  const { slug } = await params;
  if (slug === "re") permanentRedirect("/real-estate");
  const page = pagesBySlug[slug];
  if (!page) notFound();
  return <LandingExperience page={page} />;
}
