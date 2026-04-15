"use client";

import React, { useState } from "react";
import {
  formatCurrencyLarge,
  formatDate,
  formatPercentage,
} from "../utils/formatters";

interface EarningsTableProps {
  earningsHistory: any[];
}

export default function EarningsTable({ earningsHistory }: EarningsTableProps) {
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const toggleRow = (idx: number) => {
    setExpandedRow(expandedRow === idx ? null : idx);
  };

  if (!earningsHistory || earningsHistory.length === 0) return null;

  return (
    <section>
      <h2 className="text-lg font-semibold mb-4">
        Comprehensive Earnings History
      </h2>
      <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
        <table className="w-full text-left text-sm whitespace-normal">
          <thead className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950">
            <tr>
              <th className="p-4 font-medium w-8"></th>
              <th className="p-4 font-medium">Earnings Date</th>
              <th className="p-4 font-medium">EPS Est</th>
              <th className="p-4 font-medium">EPS Actual</th>
              <th className="p-4 font-medium">Surprise</th>
              <th className="p-4 font-medium">Total Revenue</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
            {earningsHistory.map((earning, idx) => (
              <React.Fragment key={idx}>
                <tr
                  onClick={() => toggleRow(idx)}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-950/50 transition-colors cursor-pointer"
                >
                  <td className="p-4 text-zinc-400">
                    {expandedRow === idx ? "▼" : "▶"}
                  </td>
                  <td className="p-4 font-medium">
                    {formatDate(earning.earnings_date)}
                  </td>
                  <td className="p-4">
                    {earning.eps_estimate !== null
                      ? earning.eps_estimate
                      : "N/A"}
                  </td>
                  <td className="p-4">
                    {earning.eps_actual !== null ? earning.eps_actual : "N/A"}
                  </td>
                  <td
                    className={`p-4 ${earning.surprise_pct && earning.surprise_pct > 0 ? "text-green-600 dark:text-green-400" : earning.surprise_pct && earning.surprise_pct < 0 ? "text-red-600 dark:text-red-400" : ""}`}
                  >
                    {formatPercentage(earning.surprise_pct)}
                  </td>
                  <td className="p-4">
                    {formatCurrencyLarge(earning.total_revenue)}
                  </td>
                </tr>
                {expandedRow === idx && (
                  <tr className="bg-zinc-50/50 dark:bg-zinc-950/30">
                    <td
                      colSpan={6}
                      className="p-6 border-b border-zinc-200 dark:border-zinc-800"
                    >
                      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                        <div>
                          <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                            Details & Timing
                          </h4>
                          <div className="space-y-2 mb-4 text-sm">
                            <p>
                              <span className="text-zinc-500 mr-2">Name:</span>{" "}
                              {earning.company_name || "N/A"}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Industry:
                              </span>{" "}
                              {earning.industry || "N/A"}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Sector:
                              </span>{" "}
                              {earning.sector || "N/A"}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Sector ETF:
                              </span>{" "}
                              {earning.sector_etf || "N/A"}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Timing:
                              </span>{" "}
                              {earning.earnings_timing || "N/A"}
                            </p>
                          </div>
                        </div>

                        <div>
                          <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                            Price Action
                          </h4>
                          <div className="space-y-2 text-sm">
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Ref Close Date:
                              </span>{" "}
                              {formatDate(earning.ref_close_date)}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Price Ref Close:
                              </span>{" "}
                              {earning.price_ref_close
                                ? `$${earning.price_ref_close.toFixed(2)}`
                                : "N/A"}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Sector Ref Close:
                              </span>{" "}
                              {earning.sector_ref_close
                                ? `$${earning.sector_ref_close.toFixed(2)}`
                                : "N/A"}
                            </p>
                            <div className="h-2"></div>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Ref Open Date:
                              </span>{" "}
                              {formatDate(earning.ref_open_date)}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Price Ref Open:
                              </span>{" "}
                              {earning.price_ref_open
                                ? `$${earning.price_ref_open.toFixed(2)}`
                                : "N/A"}
                              {earning.price_ref_open &&
                                earning.price_ref_close && (
                                  <span
                                    className={`ml-2 ${earning.price_ref_open >= earning.price_ref_close ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
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
                              <span className="text-zinc-500 mr-2">
                                Sector Ref Open:
                              </span>{" "}
                              {earning.sector_ref_open
                                ? `$${earning.sector_ref_open.toFixed(2)}`
                                : "N/A"}
                              {earning.sector_ref_open &&
                                earning.sector_ref_close && (
                                  <span
                                    className={`ml-2 ${earning.sector_ref_open >= earning.sector_ref_close ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
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
                          <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                            Extended Financials
                          </h4>
                          <div className="space-y-2 text-sm">
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Operating Income:
                              </span>{" "}
                              {formatCurrencyLarge(earning.operating_income)}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                Norm. EBITA:
                              </span>{" "}
                              {formatCurrencyLarge(earning.normalized_EBITA)}
                            </p>
                          </div>
                        </div>

                        <div>
                          <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                            Impact Analysis
                          </h4>
                          {earning.impact_factors ? (
                            <div className="space-y-2 text-sm">
                              <p>
                                <span className="text-zinc-500 mr-2">
                                  Primary Driver:
                                </span>{" "}
                                <span className="font-medium text-zinc-900 dark:text-zinc-100">
                                  {earning.impact_factors.primary_driver}
                                </span>
                              </p>
                              <p>
                                <span className="text-zinc-500 mr-2">
                                  Excess Return:
                                </span>{" "}
                                {earning.impact_factors.excess_return}%
                              </p>
                              <p>
                                <span className="text-zinc-500 mr-2">
                                  {/*  */}
                                  Attr. Score:
                                </span>{" "}
                                {
                                  earning.impact_factors
                                    .earnings_attribution_score
                                }
                              </p>
                              <p>
                                <span className="text-zinc-500 mr-2">
                                  Volatility Factor:
                                </span>{" "}
                                <span className="capitalize">
                                  {earning.impact_factors.volatility_factor}
                                </span>
                              </p>
                              <p>
                                <span className="text-zinc-500 mr-2">
                                  Sector Influence:
                                </span>{" "}
                                <span className="capitalize">
                                  {earning.impact_factors.sector_influence}
                                </span>
                              </p>
                            </div>
                          ) : (
                            <p className="text-sm text-zinc-500">
                              Not calculated
                            </p>
                          )}
                        </div>

                        <div>
                          <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                            Market & System
                          </h4>
                          <div className="space-y-2 mb-4 text-sm">
                            <p>
                              <span className="text-zinc-500 mr-2">
                                ETF Change:
                              </span>{" "}
                              {formatPercentage(earning.sector_etf_change)}
                            </p>
                            <p>
                              <span className="text-zinc-500 mr-2">
                                VIX Close:
                              </span>{" "}
                              {earning.vix_close
                                ? earning.vix_close.toFixed(2)
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
