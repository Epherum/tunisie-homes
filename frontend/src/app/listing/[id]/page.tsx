import { ListingDetail } from "./detail-content";
import { formatLocation } from "@/lib/format";
import { fetchListingById } from "@/lib/listings";
import type { Metadata } from "next";
import { notFound } from "next/navigation";

type Props = {
  params: Promise<{ id: string }>;
};

export const revalidate = 60;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const { listing } = await fetchListingById(id);

  if (!listing) {
    return {
      title: "Listing not found | TunisHome Pro",
    };
  }

  return {
    title: `${listing.title} | TunisHome Pro`,
    description: `${formatLocation(listing)} • ${listing.surfaceArea ?? "—"} m²`,
  };
}

export default async function ListingPage({ params }: Props) {
  const { id } = await params;
  const { listing, images, error } = await fetchListingById(id);

  if (!listing) {
    notFound();
  }

  return <ListingDetail listing={listing} images={images} error={error} />;
}
