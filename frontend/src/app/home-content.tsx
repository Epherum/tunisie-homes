"use client";

/* eslint-disable @next/next/no-img-element */
import { formatLocation, formatPrice } from "@/lib/format";
import type { Listing } from "@/lib/listings";
import { motion } from "framer-motion";
import TransitionLink from "@/components/TransitionLink";
import styles from "./page.module.css";

type Props = {
  listings: Listing[];
  error?: string;
};

const fadeIn = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } },
};

const listVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.12,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 18, scale: 0.98 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] },
  },
};

export function HomeContent({ listings, error }: Props) {
  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <motion.header
          className={styles.hero}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className={styles.eyebrow}>Supabase live feed</p>
          <div className={styles.heroRow}>
            <h1 className={styles.title}>TunisHome Pro listings</h1>
            <div className={styles.badge}>v1 Data Factory</div>
          </div>
          <p className={styles.subhead}>
            Fresh properties pulled directly from Supabase (`properties` + `images`). Use this as the
            showroom while the scraper keeps feeding the database.
          </p>
          <motion.div
            className={styles.metrics}
            variants={listVariants}
            initial="hidden"
            animate="show"
          >
            <motion.div className={styles.metric} variants={fadeIn}>
              <span>Listings shown</span>
              <strong>{listings.length}</strong>
            </motion.div>
            <motion.div className={styles.metric} variants={fadeIn}>
              <span>Refresh cadence</span>
              <strong>ISR 60s</strong>
            </motion.div>
            <motion.div className={styles.metric} variants={fadeIn}>
              <span>Pipeline</span>
              <strong>Supabase → Next.js</strong>
            </motion.div>
          </motion.div>
        </motion.header>

        {error ? (
          <motion.div className={styles.alert} initial="hidden" animate="show" variants={fadeIn}>
            Couldn&apos;t load all Supabase data: {error}
          </motion.div>
        ) : null}

        {listings.length === 0 ? (
          <motion.div className={styles.empty} initial="hidden" animate="show" variants={fadeIn}>
            No properties available yet. Confirm your Supabase URL/anon key and make sure the scraper
            has populated `properties` and `images`.
          </motion.div>
        ) : (
          <motion.section
            className={styles.grid}
            variants={listVariants}
            initial="hidden"
            animate="show"
          >
            {listings.map((listing) => (
              <motion.article key={listing.id} variants={cardVariants}>
                <TransitionLink
                  href={`/listing/${listing.id}`}
                  className={styles.card}
                  aria-label={`Voir ${listing.title}`}
                >
                  <div
                    className={styles.media}
                    style={{ viewTransitionName: `listing-${listing.id}-media` }}
                  >
                    {listing.image ? (
                      <img src={listing.image} alt={listing.title} loading="lazy" />
                    ) : (
                      <div className={styles.placeholder}>No photo yet</div>
                    )}
                    <div className={styles.badgeRow}>
                      {listing.listingType ? (
                        <span className={styles.badge}>{listing.listingType}</span>
                      ) : null}
                      {listing.propertyType ? (
                        <span className={`${styles.badge} ${styles.ghost}`}>
                          {listing.propertyType}
                        </span>
                      ) : null}
                      {typeof listing.dealRating === "number" ? (
                        <span
                          className={`${styles.badge} ${
                            listing.dealRating >= 60 ? styles.positive : styles.neutral
                          }`}
                        >
                          Deal {listing.dealRating}%
                        </span>
                      ) : null}
                      {typeof listing.renovationScore === "number" ? (
                        <span className={`${styles.badge} ${styles.soft}`}>
                          Renov. {listing.renovationScore}/10
                        </span>
                      ) : null}
                    </div>
                  </div>

                  <div className={styles.cardBody}>
                    <div className={styles.priceRow}>
                      <span className={styles.price}>{formatPrice(listing.price)}</span>
                      {listing.surfaceArea ? (
                        <span className={styles.surface}>{listing.surfaceArea} m²</span>
                      ) : null}
                    </div>
                    <h3 className={styles.cardTitle}>{listing.title}</h3>
                    <p className={styles.location}>{formatLocation(listing)}</p>
                    <div className={styles.metaRow}>
                      {listing.rooms ? (
                        <span className={styles.metaChip}>{listing.rooms} rooms</span>
                      ) : null}
                      {listing.bathrooms ? (
                        <span className={styles.metaChip}>{listing.bathrooms} baths</span>
                      ) : null}
                      {listing.pricePerSqm ? (
                        <span className={styles.metaChip}>
                          {formatPrice(listing.pricePerSqm)}/m²
                        </span>
                      ) : null}
                    </div>
                    {listing.features && listing.features.length > 0 ? (
                      <div className={styles.tags}>
                        {listing.features.slice(0, 4).map((feature) => (
                          <span key={feature} className={styles.tag}>
                            {feature}
                          </span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </TransitionLink>
              </motion.article>
            ))}
          </motion.section>
        )}
      </div>
    </div>
  );
}
