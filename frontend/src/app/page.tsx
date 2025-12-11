import { HomeContent } from "./home-content";
import { fetchListings } from "@/lib/listings";

export const revalidate = 60;

export default async function Home() {
  const { listings, error } = await fetchListings(24);

  return <HomeContent listings={listings} error={error} />;
}
