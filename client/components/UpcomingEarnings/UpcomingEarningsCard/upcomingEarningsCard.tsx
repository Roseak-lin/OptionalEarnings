import type { UpcomingEarnings } from "@/types";
import styles from "./upcomingEarningsCard.module.css";

import { formatDate, formatCurrencyLarge } from "@/utils/formatters";

export default function UpcomingEarningsCard({
  earningsDetails,
}: {
  earningsDetails: UpcomingEarnings;
}) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.ticker}>
          {earningsDetails.name} ({earningsDetails.ticker})
        </h3>
        <span className={styles.dateBadge}>
          {formatDate(earningsDetails.earnings_date)}
        </span>
      </div>

      <div className={styles.grid}>
        <div className={styles.column}>
          <span className={styles.label}>EPS Estimate</span>
          <span className={styles.value}>${earningsDetails.eps_estimate !== null &&
            earningsDetails.eps_estimate !== undefined
              ? earningsDetails.eps_estimate
              : "N/A"}
          </span>
        </div>

        <div className={styles.column}>
          <span className={styles.label}>Timing</span>
          <span className={styles.value}>
            {earningsDetails.timing || "Unspecified"}
          </span>
        </div>

        <div className={styles.column}>
          <span className={styles.label}>Market Cap</span>
          <span className={styles.value}>
            {formatCurrencyLarge(earningsDetails.market_cap)}
          </span>
        </div>
      </div>
    </div>
  );
}
