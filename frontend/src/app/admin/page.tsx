"use client";

import {
  addImageToListing,
  fetchListingsWithImages,
  removeImageFromListing,
  type ListingWithImages,
  updateListing,
} from "@/lib/listings";
import styles from "./page.module.css";
import { useEffect, useMemo, useState } from "react";

type Status = { message: string; tone: "idle" | "success" | "error" };

const emptyStatus: Status = { message: "", tone: "idle" };

export default function AdminPage() {
  const [listings, setListings] = useState<ListingWithImages[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>(emptyStatus);
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState("");

  const [form, setForm] = useState({
    title: "",
    price: "",
    city: "",
    region: "",
    propertyType: "",
    listingType: "",
    rooms: "",
    bathrooms: "",
    surfaceArea: "",
    renovationScore: "",
    dealRating: "",
    pricePerSqm: "",
    features: "",
  });

  useEffect(() => {
    const load = async () => {
      const { listings: data, error } = await fetchListingsWithImages(200);
      if (error) {
        setStatus({ message: error, tone: "error" });
      }
      setListings(data);
      if (data.length > 0) {
        setSelectedId(data[0].id);
      }
    };

    load();
  }, []);

  const selected = useMemo(
    () => listings.find((l) => l.id === selectedId) ?? null,
    [listings, selectedId],
  );

  useEffect(() => {
    if (!selected) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setForm({
      title: selected.title ?? "",
      price: selected.price?.toString() ?? "",
      city: selected.city ?? "",
      region: selected.region ?? "",
      propertyType: selected.propertyType ?? "",
      listingType: selected.listingType ?? "",
      rooms: selected.rooms?.toString() ?? "",
      bathrooms: selected.bathrooms?.toString() ?? "",
      surfaceArea: selected.surfaceArea?.toString() ?? "",
      renovationScore: selected.renovationScore?.toString() ?? "",
      dealRating: selected.dealRating?.toString() ?? "",
      pricePerSqm: selected.pricePerSqm?.toString() ?? "",
      features: selected.features?.join(", ") ?? "",
    });
  }, [selected]);

  const handleChange = (field: keyof typeof form, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    if (!selected) return;
    setLoading(true);
    setStatus(emptyStatus);

    const payload = {
      title: form.title || null,
      price: form.price ? Number(form.price) : null,
      city: form.city || null,
      region: form.region || null,
      propertyType: form.propertyType || null,
      listingType: form.listingType || null,
      rooms: form.rooms ? Number(form.rooms) : null,
      bathrooms: form.bathrooms ? Number(form.bathrooms) : null,
      surfaceArea: form.surfaceArea ? Number(form.surfaceArea) : null,
      renovationScore: form.renovationScore ? Number(form.renovationScore) : null,
      dealRating: form.dealRating ? Number(form.dealRating) : null,
      pricePerSqm: form.pricePerSqm ? Number(form.pricePerSqm) : null,
      features: form.features
        ? form.features
            .split(",")
            .map((f) => f.trim())
            .filter(Boolean)
        : [],
    };

    const result = await updateListing(selected.id, payload);
    if (!result.success) {
      setStatus({ message: result.error ?? "Failed to update listing", tone: "error" });
    } else {
      setStatus({ message: "Listing saved", tone: "success" });
      setListings((prev) =>
        prev.map((item) => (item.id === selected.id ? { ...item, ...payload } : item)),
      );
    }

    setLoading(false);
  };

  const handleAddImage = async () => {
    if (!selected || !imageUrl.trim()) return;
    setLoading(true);
    setStatus(emptyStatus);

    const result = await addImageToListing(selected.id, imageUrl.trim());
    if (!result.success) {
      setStatus({ message: result.error ?? "Failed to add image", tone: "error" });
    } else {
      setStatus({ message: "Image added", tone: "success" });
      setListings((prev) =>
        prev.map((item) =>
          item.id === selected.id
            ? {
                ...item,
                images: Array.from(new Set([...(item.images ?? []), imageUrl.trim()])),
                image: item.image ?? imageUrl.trim(),
              }
            : item,
        ),
      );
      setImageUrl("");
    }

    setLoading(false);
  };

  const handleRemoveImage = async (url: string) => {
    if (!selected) return;
    setLoading(true);
    setStatus(emptyStatus);
    const result = await removeImageFromListing(selected.id, url);
    if (!result.success) {
      setStatus({ message: result.error ?? "Failed to remove image", tone: "error" });
    } else {
      setStatus({ message: "Image removed", tone: "success" });
      setListings((prev) =>
        prev.map((item) =>
          item.id === selected.id
            ? {
                ...item,
                images: item.images.filter((img) => img !== url),
                image: item.image === url ? item.images.find((img) => img !== url) ?? null : item.image,
              }
            : item,
        ),
      );
    }
    setLoading(false);
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <aside className={`${styles.panel}`}>
          <h2>Listings</h2>
          <div className={styles.list}>
            {listings.map((listing) => (
              <button
                key={listing.id}
                className={`${styles.listItem} ${selectedId === listing.id ? styles.active : ""}`}
                onClick={() => setSelectedId(listing.id)}
              >
                <span>{listing.title}</span>
                <span>{listing.city ?? "–"}</span>
              </button>
            ))}
          </div>
        </aside>

        <section className={`${styles.panel} ${styles.editor}`}>
          <header className={styles.actions}>
            <h2>Edit listing</h2>
            <span className={styles.status}>
              {status.message ? `${status.tone === "error" ? "⚠️" : "✅"} ${status.message}` : ""}
            </span>
          </header>

          {selected ? (
            <>
              <div className={styles.field}>
                <label className={styles.label}>Title</label>
                <input
                  className={styles.input}
                  value={form.title}
                  onChange={(e) => handleChange("title", e.target.value)}
                />
              </div>

              <div className={styles.row}>
                <div className={styles.field}>
                  <label className={styles.label}>Price (DT)</label>
                  <input
                    className={styles.input}
                    value={form.price}
                    onChange={(e) => handleChange("price", e.target.value)}
                    inputMode="numeric"
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Price / m²</label>
                  <input
                    className={styles.input}
                    value={form.pricePerSqm}
                    onChange={(e) => handleChange("pricePerSqm", e.target.value)}
                    inputMode="numeric"
                  />
                </div>
              </div>

              <div className={styles.row}>
                <div className={styles.field}>
                  <label className={styles.label}>City</label>
                  <input
                    className={styles.input}
                    value={form.city}
                    onChange={(e) => handleChange("city", e.target.value)}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Region</label>
                  <input
                    className={styles.input}
                    value={form.region}
                    onChange={(e) => handleChange("region", e.target.value)}
                  />
                </div>
              </div>

              <div className={styles.row}>
                <div className={styles.field}>
                  <label className={styles.label}>Property type</label>
                  <input
                    className={styles.input}
                    value={form.propertyType}
                    onChange={(e) => handleChange("propertyType", e.target.value)}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Listing type</label>
                  <input
                    className={styles.input}
                    value={form.listingType}
                    onChange={(e) => handleChange("listingType", e.target.value)}
                  />
                </div>
              </div>

              <div className={styles.row}>
                <div className={styles.field}>
                  <label className={styles.label}>Rooms</label>
                  <input
                    className={styles.input}
                    value={form.rooms}
                    onChange={(e) => handleChange("rooms", e.target.value)}
                    inputMode="numeric"
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Bathrooms</label>
                  <input
                    className={styles.input}
                    value={form.bathrooms}
                    onChange={(e) => handleChange("bathrooms", e.target.value)}
                    inputMode="numeric"
                  />
                </div>
              </div>

              <div className={styles.row}>
                <div className={styles.field}>
                  <label className={styles.label}>Surface (m²)</label>
                  <input
                    className={styles.input}
                    value={form.surfaceArea}
                    onChange={(e) => handleChange("surfaceArea", e.target.value)}
                    inputMode="numeric"
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Renovation score</label>
                  <input
                    className={styles.input}
                    value={form.renovationScore}
                    onChange={(e) => handleChange("renovationScore", e.target.value)}
                    inputMode="numeric"
                  />
                </div>
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Deal rating (%)</label>
                <input
                  className={styles.input}
                  value={form.dealRating}
                  onChange={(e) => handleChange("dealRating", e.target.value)}
                  inputMode="numeric"
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Features (comma separated)</label>
                <textarea
                  className={styles.textarea}
                  value={form.features}
                  onChange={(e) => handleChange("features", e.target.value)}
                  placeholder="balcony, garden, parking"
                />
              </div>

              <div className={styles.actions}>
                <button className={styles.button} onClick={handleSave} disabled={loading}>
                  Save changes
                </button>
                <span className={styles.status}>{loading ? "Saving..." : ""}</span>
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Images</label>
                <div className={styles.images}>
                  {(selected.images ?? []).map((url) => (
                    <span key={url} className={styles.imageChip}>
                      {url}
                      <button className={styles.danger} onClick={() => handleRemoveImage(url)}>
                        remove
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className={styles.actions}>
                <input
                  className={styles.input}
                  placeholder="https://example.com/photo.jpg"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                />
                <button className={`${styles.button} ${styles.secondary}`} onClick={handleAddImage} disabled={loading}>
                  Add image
                </button>
              </div>
            </>
          ) : (
            <p className={styles.status}>{status.message || "Select a listing to edit."}</p>
          )}
        </section>
      </div>
    </div>
  );
}
