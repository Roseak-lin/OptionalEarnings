"use client";

import React, { useState } from "react";
import {
  formatCurrencyLarge,
  formatDate,
  formatPercentage,
} from "../../utils/formatters";
import styles from "./earningsTable.module.css";

interface EarningsTableProps {
  earningsHistory: any[];
}

export default function EarningsTable({ earningsHistory }: EarningsTableProps) {
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const toggleRow = (idx: number) => {
    setExpandedRow(expandedRow === idx ? null : idx);
  };

  const computeSurpriseCategory = (percentage: number | null) => {
    if (percentage === null) return "";
    if (percentage >= 3.5) return styles.textVeryPositive;
    else if (percentage > 0) return styles.textPositive;
    else if (percentage <= -3.5) return styles.textVeryNegative;
    else return styles.textNegative;
  }

  if (!earningsHistory || earningsHistory.length === 0) return null;
  return (
    <section>
      <h2 className={styles.title}>
        Comprehensive Earnings History
      </h2>
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead className={styles.thead}>
            <tr>
              <th className={styles.thIcon}></th>
              <th className={styles.th}>Earnings Date</th>
              <th className={styles.th}>EPS Est</th>
              <th className={styles.th}>EPS Actual</th>
              <th className={styles.th}>Surprise</th>
              <th className={styles.th}>Total Revenue</th>
            </tr>
          </thead>
          <tbody className={styles.tbody}>
            {earningsHistory.map((earning, idx) => (
              <React.Fragment key={idx}>
                <tr
                  onClick={() => toggleRow(idx)}
                  className={styles.trMain}
                >
                  <td className={styles.tdIcon}>
                    {expandedRow === idx ? "▼" : "▶"}
                  </td>
                  <td className={styles.tdDate}>
                    {formatDate(earning.earnings_date)}
                  </td>
                  <td className={styles.td}>
                    {earning.eps_estimate !== null
                      ? earning.eps_estimate.toFixed(2)
                      : "N/A"}
                  </td>
                  <td className={styles.td}>
                    {earning.eps_actual !== null ? earning.eps_actual.toFixed(2) : "N/A"}
                  </td>
                  <td
                    className={`${styles.td} ${
                      earning.surprise_pct && earning.surprise_pct > 0
                        ? styles.textPositive
                        : earning.surprise_pct && earning.surprise_pct < 0
                        ? styles.textNegative
                        : ""
                    }`}
                  >
                    {formatPercentage(earning.surprise_pct)}
                  </td>
                  <td className={styles.td}>
                    {formatCurrencyLarge(earning.total_revenue)}
                  </td>
                </tr>
                {expandedRow === idx && (
                  <tr className={styles.trExpanded}>
                    <td colSpan={6} className={styles.tdExpanded}>
                      <div className={styles.grid}>
                        <div>
                          <h4 className={styles.sectionTitle}>
                            Details & Timing
                          </h4>
                          <div className={styles.detailsGroup}>
                            <p>
                              <span className={styles.label}>Name:</span>{" "}
                              {earning.company_name || "N/A"}
                            </p>
                            <p>
                              <span className={styles.label}>Industry:</span>{" "}
                              {earning.industry || "N/A"}
                            </p>
                            <p>
                              <span className={styles.label}>Sector:</span>{" "}
                              {earning.sector || "N/A"}
                            </p>
                            <p>
                              <span className={styles.label}>Sector ETF:</span>{" "}
                              {earning.sector_etf || "N/A"}
                            </p>
                            <p>
                              <span className={styles.label}>Timing:</span>{" "}
                              {earning.earnings_timing || "N/A"}
                            </p>
                          </div>
                        </div>

                        <div>
                          <h4 className={styles.sectionTitle}>
                            Price Action
                          </h4>
                          <div className={styles.detailsGroupNoMargin}>
                            <p>
                              <span className={styles.label}>
                                Ref Close Date:
                              </span>{" "}
                              {formatDate(earning.ref_close_date)}
                            </p>
                            <p>
                              <span className={styles.label}>
                                Price Ref Close:
                              </span>{" "}
                              {earning.price_ref_close
                                ? `$${earning.price_ref_close.toFixed(2)}`
                                : "N/A"}
                            </p>
                            <p>
                              <span className={styles.label}>
                                Sector Ref Close:
                              </span>{" "}
                              {earning.sector_ref_close
                                ? `$${earning.sector_ref_close.toFixed(2)}`
                                : "N/A"}
                            </p>
                            <div className={styles.spacer}></div>
                            <p>
                              <span className={styles.label}>
                                Ref Open Date:
                              </span>{" "}
                              {formatDate(earning.ref_open_date)}
                            </p>
                            <p>
                              <span className={styles.label}>
                                Price Ref Open:
                              </span>{" "}
                              {earning.price_ref_open
                                ? `$${earning.price_ref_open.toFixed(2)}`
                                : "N/A"}
                              {earning.price_ref_open &&
                                earning.price_ref_close && (
                                  <span
                                    className={`ml-2 ${
                                      computeSurpriseCategory((earning.price_ref_open - earning.price_ref_close) / earning.price_ref_close * 100)
                                    }`}
                                  >
                                    (
                                    {earning.price_ref_open >=
                                    earning.price_ref_close
                                      ? "+"
                                      : ""}
                                    {(
                                      ((earning.price_ref_open -
                                        earning.price_ref_close) /
                                        earning.price_ref_close) *
                                      100
                                    ).toFixed(2)}
                                    %)
                                  </span>
                                )}
                            </p>
                            <p>
                              <span className={styles.label}>
                                Sector Ref Open:
                              </span>{" "}
                              {earning.sector_ref_open
                                ? `$${earning.sector_ref_open.toFixed(2)}`
                                : "N/A"}
                              {earning.sector_ref_open &&
                                earning.sector_ref_close && (
                                  <span
                                    className={`ml-2 ${
                                      computeSurpriseCategory((earning.sector_ref_open - earning.sector_ref_close) / earning.sector_ref_close * 100)
                                    }`}
                                  >
                                    (
                                    {earning.sector_ref_open >=
                                    earning.sector_ref_close
                                      ? "+"
                                      : ""}
                                    {(
                                      ((earning.sector_ref_open -
                                        earning.sector_ref_close) /
                                        earning.sector_ref_close) *
                                      100
                                    ).toFixed(2)}
                                    %)
                                  </span>
                                )}
                            </p>
                          </div>
                        </div>

                        <div>
                          <h4 className={styles.sectionTitle}>
                            Extended Financials
                          </h4>
                          <div className={styles.detailsGroupNoMargin}>
                            <p>
                              <span className={styles.label}>
                                Operating Income:
                              </span>{" "}
                              {formatCurrencyLarge(earning.operating_income)}
                            </p>
                            <p>
                              <span className={styles.label}>
                                Norm. EBITA:
                              </span>{" "}
                              {formatCurrencyLarge(earning.normalized_EBITA)}
                            </p>
                          </div>
                        </div>

                        <div>
                          <h4 className={styles.sectionTitle}>
                            Impact Analysis
                          </h4>
                          {earning.impact_factors ? (
                            <div className={styles.detailsGroupNoMargin}>
                              <p>
                                <span className={styles.label}>
                                  Primary Driver:
                                </span>{" "}
                                <span className={styles.highlightValue}>
                                  {earning.impact_factors.primary_driver}
                                </span>
                              </p>
                              <p>
                                <span className={styles.label}>
                                  Excess Return:
                                </span>{" "}
                                {earning.impact_factors.excess_return}%
                              </p>
                              <p>
                                <span className={styles.label}>
                                  Attr. Score:
                                </span>{" "}
                                {
                                  earning.impact_factors
                                    .earnings_attribution_score
                                }
                              </p>
                              <p>
                                <span className={styles.label}>
                                  Volatility Factor:
                                </span>{" "}
                                <span className={styles.capitalize}>
                                  {earning.impact_factors.volatility_factor}
                                </span>
                              </p>
                              <p>
                                <span className={styles.label}>
                                  Sector Influence:
                                </span>{" "}
                                <span className={styles.capitalize}>
                                  {earning.impact_factors.sector_influence}
                                </span>
                              </p>
                            </div>
                          ) : (
                            <p className={styles.notCalculated}>
                              Not calculated
                            </p>
                          )}
                        </div>

                        <div>
                          <h4 className={styles.sectionTitle}>
                            Market & System
                          </h4>
                          <div className={styles.detailsGroup}>
                            <p>
                              <span className={styles.label}>
                                ETF Change:
                              </span>{" "}
                              {formatPercentage(earning.sector_etf_change)}
                            </p>
                            <p>
                              <span className={styles.label}>
                                VIX {earning.earnings_timing === "Before market open" ? "Open" : "Close"}:
                              </span>{" "}
                              {earning.vix_val
                                ? earning.vix_val.toFixed(2)
                                : "N/A"}
                            </p>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}