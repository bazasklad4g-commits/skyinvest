import type { MetadataRoute } from "next";
import { grantLandingPages } from "../content/grant-landing-pages";
import { landingPages } from "../content/landing-pages";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://m.nezalezhnist.org.ua";
  return [...landingPages, ...grantLandingPages].map(({ slug }) => ({ url: `${base}/${slug}`, lastModified: new Date(), changeFrequency: "weekly", priority: grantLandingPages.some((page) => page.slug === slug) ? 0.8 : slug === "bali-ru" || slug === "ispania-ru" || slug === "turkey-ru" || slug === "dubai" ? 1 : 0.7 }));
}
