import styles from "./earningsHistorySummary.module.css";

export default function EarningsHistorySummary({
  summary,
}: {
  summary: string;
}) {
  if (!summary) return null;
  return (
    <section>
      <h2 className={styles.title}>Summary: </h2>
      <div>
        <p className={styles.text}>{summary}</p>
      </div>
    </section>
  );
}
