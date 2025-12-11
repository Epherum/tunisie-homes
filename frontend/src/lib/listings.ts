import { getSupabaseClient } from "./supabaseClient";

export type Listing = {
  id: string;
  title: string;
  price: number | null;
  sourceUrl?: string | null;
  city?: string | null;
  region?: string | null;
  propertyType?: string | null;
  listingType?: string | null;
  rooms?: number | null;
  bathrooms?: number | null;
  surfaceArea?: number | null;
  renovationScore?: number | null;
  dealRating?: number | null;
  pricePerSqm?: number | null;
  features?: string[] | null;
  image?: string | null;
};

export type ListingWithImages = Listing & { images: string[] };

type PropertyRow = {
  id: string;
  title: string;
  price: number | null;
  sourceUrl?: string | null;
  city?: string | null;
  region?: string | null;
  propertyType?: string | null;
  listingType?: string | null;
  rooms?: number | null;
  bathrooms?: number | null;
  surfaceArea?: number | null;
  renovationScore?: number | null;
  dealRating?: number | null;
  pricePerSqm?: number | null;
  features?: string[] | null;
};

type ImageRow = {
  url: string;
  propertyId: string;
};

function stripRef(title?: string | null): string | null {
  if (!title) return title ?? null;
  return title.replace(/^\s*\[?\s*r[eé]f[:\s]*\d+\]?\s*/i, "").trim();
}

export async function fetchListings(limit = 24): Promise<{
  listings: Listing[];
  error?: string;
}> {
  try {
    const supabase = getSupabaseClient();
    const { data: properties, error } = await supabase
      .from("properties")
      .select(
        "id,title,sourceUrl,price,city,region,propertyType,listingType,rooms,bathrooms,surfaceArea,renovationScore,dealRating,pricePerSqm,features",
      )
      .order("scrapedAt", { ascending: false })
      .limit(limit);

    if (error) {
      throw new Error(error.message);
    }

    const propertyIds = (properties ?? []).map((property) => property.id);
    const primaryImages = new Map<string, string>();
    let imageError: string | undefined;

    if (propertyIds.length > 0) {
      const { data: images, error: imagesError } = await supabase
        .from("images")
        .select("propertyId,url")
        .in("propertyId", propertyIds);

      if (imagesError) {
        imageError = imagesError.message;
      }

      images?.forEach((image: ImageRow) => {
        if (!primaryImages.has(image.propertyId)) {
          primaryImages.set(image.propertyId, image.url);
        }
      });
    }

    const listings =
      properties?.map((property: PropertyRow) => {
        const features = Array.isArray(property.features)
          ? property.features
          : [];

        return {
          ...property,
          title: stripRef(property.title) ?? "",
          features,
          image: primaryImages.get(property.id) ?? null,
        };
      }) ?? [];

    return {
      listings,
      error: imageError,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown Supabase error";
    return { listings: [], error: message };
  }
}

export async function fetchListingsWithImages(limit = 100): Promise<{
  listings: ListingWithImages[];
  error?: string;
}> {
  try {
    const supabase = getSupabaseClient();
    let imageError: string | undefined;
    const { data: properties, error } = await supabase
      .from("properties")
      .select(
        "id,title,sourceUrl,price,city,region,propertyType,listingType,rooms,bathrooms,surfaceArea,renovationScore,dealRating,pricePerSqm,features",
      )
      .order("scrapedAt", { ascending: false })
      .limit(limit);

    if (error) {
      throw new Error(error.message);
    }

    const propertyIds = (properties ?? []).map((property) => property.id);
    const imageBuckets = new Map<string, string[]>();

    if (propertyIds.length > 0) {
      const { data: images, error: imagesError } = await supabase
        .from("images")
        .select("propertyId,url")
        .in("propertyId", propertyIds);

      if (imagesError) {
        imageError = imagesError.message;
      }

      images?.forEach((image: ImageRow) => {
        const arr = imageBuckets.get(image.propertyId) ?? [];
        if (!arr.includes(image.url)) {
          arr.push(image.url);
        }
        imageBuckets.set(image.propertyId, arr);
      });
    }

    const listings =
      properties?.map((property: PropertyRow) => {
        const features = Array.isArray(property.features)
          ? property.features
          : [];

        const images = imageBuckets.get(property.id) ?? [];

        return {
          ...property,
          title: stripRef(property.title) ?? "",
          features,
          image: images[0] ?? null,
          images,
        };
      }) ?? [];

    return { listings, error: imageError };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown Supabase error";
    return { listings: [], error: message };
  }
}

export async function fetchListingById(id: string): Promise<{
  listing: Listing | null;
  images: string[];
  error?: string;
}> {
  try {
    const supabase = getSupabaseClient();
    const { data: property, error } = await supabase
      .from("properties")
      .select(
        "id,title,sourceUrl,price,city,region,propertyType,listingType,rooms,bathrooms,surfaceArea,renovationScore,dealRating,pricePerSqm,features",
      )
      .eq("id", id)
      .single();

    if (error) {
      if (error.code === "PGRST116") {
        return { listing: null, images: [], error: "Listing not found" };
      }
      throw new Error(error.message);
    }

    const { data: imageRows, error: imagesError } = await supabase
      .from("images")
      .select("url")
      .eq("propertyId", id);

    const imageError = imagesError?.message;

    const listing = property
      ? {
          ...property,
          title: stripRef(property.title) ?? "",
          features: Array.isArray(property.features) ? property.features : [],
          image: imageRows?.[0]?.url ?? null,
        }
      : null;

    const images = imageRows?.map((image) => image.url) ?? [];

    return { listing, images, error: imageError };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown Supabase error";
    return { listing: null, images: [], error: message };
  }
}

export async function updateListing(
  id: string,
  data: Partial<Omit<Listing, "id">>,
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = getSupabaseClient();
    const payload = {
      ...data,
      features: Array.isArray(data.features) ? data.features : null,
    };

    const { error } = await supabase.from("properties").update(payload).eq("id", id);

    if (error) {
      throw new Error(error.message);
    }

    return { success: true };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown Supabase error";
    return { success: false, error: message };
  }
}

export async function addImageToListing(
  propertyId: string,
  url: string,
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = getSupabaseClient();
    const { error } = await supabase.from("images").insert({ propertyId, url });
    if (error) throw new Error(error.message);
    return { success: true };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown Supabase error";
    return { success: false, error: message };
  }
}

export async function removeImageFromListing(
  propertyId: string,
  url: string,
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = getSupabaseClient();
    const { error } = await supabase.from("images").delete().eq("propertyId", propertyId).eq("url", url);
    if (error) throw new Error(error.message);
    return { success: true };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown Supabase error";
    return { success: false, error: message };
  }
}
