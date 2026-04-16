import { formatCurrencyLarge } from "../../utils/formatters";
import styles from "./companyInfoCard.module.css";

interface CompanyInfoCardProps {
  companyInfo: any;
}

export default function CompanyInfoCard({ companyInfo }: CompanyInfoCardProps) {
  if (!companyInfo) return null;

  return (
    <section className={styles.card}>
      <h2 className={styles.title}>
        {companyInfo.company_name} ({companyInfo.ticker})
      </h2>
      <div className={styles.grid}>
        <div>
          <span className={styles.label}>Sector</span>
          <span className={styles.value}>{companyInfo.sector || "N/A"}</span>
        </div>
        <div>
          <span className={styles.label}>Industry</span>
          <span className={styles.value}>{companyInfo.industry || "N/A"}</span>
        </div>
        <div>
          <span className={styles.label}>Location</span>
          <span className={styles.value}>
            {companyInfo.city}, {companyInfo.country}
          </span>
        </div>
        <div>
          <span className={styles.label}>Market Cap</span>
          <span className={styles.value}>
            {formatCurrencyLarge(companyInfo.marketCap)}
          </span>
        </div>
      </div>
      <p className={styles.description}>
        {companyInfo.longBusinessSummary}
      </p>
    </section>
  );
}