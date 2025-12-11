import type { Listing } from "./listings";

export function formatPrice(value?: number | null) {
  if (value === null || value === undefined) return "Prix sur demande";
  return `${new Intl.NumberFormat("fr-FR", {
    maximumFractionDigits: 0,
  }).format(value)} DT`;
}

export function formatLocation(listing: Pick<Listing, "city" | "region">) {
  const parts = [listing.city, listing.region].filter(Boolean);
  return parts.length ? parts.join(" • ") : "Tunisia";
}
