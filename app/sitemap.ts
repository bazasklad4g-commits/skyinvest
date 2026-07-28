import type { MetadataRoute } from "next";
import { landingPages } from "../content/landing-pages";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://nezalegnist.vercel.app";
  return landingPages.map(({ slug }) => ({ url: `${base}/${slug}`, lastModified: new Date(), changeFrequency: "weekly", priority: slug === "bali-ru" || slug === "ispania-ru" || slug === "turkey-ru" || slug === "dubai" ? 1 : 0.7 }));
}
