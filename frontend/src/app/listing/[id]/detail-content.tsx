"use client";

/* eslint-disable @next/next/no-img-element */
import { formatLocation, formatPrice } from "@/lib/format";
import type { Listing } from "@/lib/listings";
import TransitionLink from "@/components/TransitionLink";
import { motion } from "framer-motion";
import styles from "./page.module.css";

type Props = {
  listing: Listing;
  images: string[];
  error?: string;
};

const fadeIn = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] },
  },
};

export function ListingDetail({ listing, images, error }: Props) {
  const gallery = images.length > 0 ? images : listing.image ? [listing.image] : [];

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <motion.div
          className={styles.topBar}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          <TransitionLink href="/" className={styles.backLink}>
            ← Back to all listings
          </TransitionLink>
          <div className={styles.topBadge}>Live Supabase feed</div>
        </motion.div>

        {error ? (
          <motion.div className={styles.alert} initial="hidden" animate="show" variants={fadeIn}>
            Supabase responded, but we&apos;re missing some media: {error}
          </motion.div>
        ) : null}

        <motion.section className={styles.detailHeader} initial="hidden" animate="show" variants={fadeIn}>
          <div className={styles.headerText}>
            <p className={styles.eyebrow}>{formatLocation(listing)}</p>
            <h1 className={styles.title}>{listing.title}</h1>
            <div className={styles.detailMetaRow}>
              <span className={styles.priceLarge}>{formatPrice(listing.price)}</span>
              {listing.surfaceArea ? (
                <span className={styles.surface}>{listing.surfaceArea} m²</span>
              ) : null}
              {listing.listingType ? (
                <span className={`${styles.badge} ${styles.ghost}`}>{listing.listingType}</span>
              ) : null}
              {listing.propertyType ? <span className={styles.badge}>{listing.propertyType}</span> : null}
            </div>
            <p className={styles.detailSubtitle}>
              Data comes straight from Supabase (`properties` + `images`) with smooth view transitions
              enabled for browsing between homes.
            </p>
            {listing.sourceUrl ? (
              <a
                className={styles.sourceLink}
                href={listing.sourceUrl}
                target="_blank"
                rel="noreferrer"
              >
                View original listing ↗
              </a>
            ) : null}
          </div>

          <div
            className={styles.heroMedia}
            style={{ viewTransitionName: `listing-${listing.id}-media` }}
          >
            {listing.image ? (
              <img src={listing.image} alt={listing.title} />
            ) : (
              <div className={styles.placeholder}>No photo yet</div>
            )}
          </div>
        </motion.section>

        <motion.section className={styles.quickFacts} initial="hidden" animate="show" variants={fadeIn}>
          <div className={styles.factCard}>
            <p>Deal rating</p>
            <strong>
              {typeof listing.dealRating === "number" ? `${listing.dealRating}%` : "No rating yet"}
            </strong>
          </div>
          <div className={styles.factCard}>
            <p>Renovation</p>
            <strong>
              {typeof listing.renovationScore === "number"
                ? `${listing.renovationScore}/10`
                : "Unknown"}
            </strong>
          </div>
          <div className={styles.factCard}>
            <p>Rooms</p>
            <strong>{listing.rooms ? `${listing.rooms} rooms` : "N/A"}</strong>
          </div>
          <div className={styles.factCard}>
            <p>Bathrooms</p>
            <strong>{listing.bathrooms ? `${listing.bathrooms} baths` : "N/A"}</strong>
          </div>
          <div className={styles.factCard}>
            <p>Price per m²</p>
            <strong>
              {listing.pricePerSqm ? `${formatPrice(listing.pricePerSqm)}/m²` : "Not provided"}
            </strong>
          </div>
        </motion.section>

        <motion.section className={styles.detailGrid} initial="hidden" animate="show" variants={fadeIn}>
          <div className={styles.detailCard}>
            <div className={styles.cardHeader}>
              <h3>Highlights</h3>
              <span className={styles.pill}>Data Factory v1</span>
            </div>
            <p className={styles.bodyText}>
              Primed for agents and investors who need a clean, fast overview with smooth load-in
              motion. This view pairs live Supabase data with Lenis scrolling and Framer Motion to keep
              browsing feeling premium.
            </p>
            {listing.features && listing.features.length > 0 ? (
              <div className={styles.tags}>
                {listing.features.map((feature) => (
                  <span key={feature} className={styles.tag}>
                    {feature}
                  </span>
                ))}
              </div>
            ) : (
              <p className={styles.subtle}>No feature tags provided yet.</p>
            )}
          </div>

          <div className={styles.detailCard}>
            <div className={styles.cardHeader}>
              <h3>Gallery</h3>
              <span className={styles.pill}>{gallery.length} photos</span>
            </div>
            {gallery.length === 0 ? (
              <div className={styles.galleryEmpty}>No imagery attached yet.</div>
            ) : (
              <div className={styles.gallery}>
                {gallery.map((url, index) => (
                  <div key={url + index} className={styles.galleryItem}>
                    <img src={url} alt={`${listing.title} photo ${index + 1}`} loading="lazy" />
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.section>
      </div>
    </div>
  );
}
