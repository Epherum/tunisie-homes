import TransitionLink from "@/components/TransitionLink";
import styles from "./not-found.module.css";

export default function NotFound() {
  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.alert}>
          Listing not found. It may have been removed or is still being scraped.
        </div>
        <TransitionLink href="/" className={styles.backLink}>
          ← Back to all listings
        </TransitionLink>
      </div>
    </div>
  );
}
