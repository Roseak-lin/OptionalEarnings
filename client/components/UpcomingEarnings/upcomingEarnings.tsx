import React, { useState } from "react";

import styles from "./upcomingEarnings.module.css";

import type { UpcomingEarnings } from "@/types";
import UpcomingEarningsCard from "./UpcomingEarningsCard/upcomingEarningsCard";

type UpcomingEarningsProps = {
  earnings: UpcomingEarnings[];
  loading: boolean;
};

export default React.memo(function UpcomingEarningsList({
  earnings,
  loading,
}: UpcomingEarningsProps) {
  const [visibleCount, setVisibleCount] = useState(5);

  const visibleEarnings = earnings.slice(0, visibleCount);
  return (
    <section className="mt-2">
      <h2 className={styles.title}>Upcoming Earnings</h2>
      <div className={styles.grid}>
        {loading ? (
          <p>Loading...</p>
        ) : earnings.length === 0 ? (
          <p>No upcoming earnings found.</p>
        ) : (
          visibleEarnings.map((earning, index) => (
            <UpcomingEarningsCard key={index} earningsDetails={earning} />
          ))
        )}
      </div>
      {visibleCount < earnings.length && (
        <button onClick={() => setVisibleCount(Math.min(visibleCount + 4, earnings.length))} className={styles.showMoreButton}>
          Show more
        </button>
      )}
    </section>
  );
});
