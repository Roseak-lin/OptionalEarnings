"use client";

import React, { useEffect, useMemo, useState } from "react";
import SearchBar from "@/components/SearchBar/searchBar";
import CompanyInfoCard from "@/components/CompanyInfoCard/companyInfoCard";
import EarningsTable from "@/components/EarningTable/earningsTable";
import EarningsHistorySummary from "@/components/EarningsHistorySummary/earningsHistorySummary";
import type { CompanyInfo, UpcomingEarnings } from "@/types/index";
import UpcomingEarningsList from "@/components/UpcomingEarnings/upcomingEarnings";
import styles from "./page.module.css";

export default function Home() {
  const [searchInput, setSearchInput] = useState<string | null>("");
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [earningsHistory, setEarningsHistory] = useState<any[]>([]);
  const [earningsAnalysis, setEarningsAnalysis] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [loadingUpcoming, setLoadingUpcoming] = useState(true);
  const [error, setError] = useState("");
  const [sP500Companies, setSP500Companies] = useState<CompanyInfo[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<CompanyInfo | null>(null);
  const [upcomingEarnings, setUpcomingEarnings] = useState<UpcomingEarnings[]>([]);

  const url = process.env.BACKEND_URL_LOCAL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${url}/api/sp500-companies`)
      .then((res) => res.json())
      .then((data) => {
        setSP500Companies(data);
      })
      .catch((err) => console.error("Error fetching SP500 companies:", err));
  
    fetch(`${url}/api/get-upcoming-earnings`)
      .then((res) => res.json())
      .then((data) => {
        setUpcomingEarnings(data || []);
        setLoadingUpcoming(false);
      })
      .catch((err) => console.error("Error fetching upcoming earnings:", err));
    }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchInput?.trim()) return;

    setLoading(true);
    setError("");
    setCompanyInfo(null);
    setEarningsHistory([]);
    setEarningsAnalysis("");

    try {
      const [infoRes, earningsRes] = await Promise.all([
        fetch(`${url}/api/company-info?ticker=${searchInput.toUpperCase()}`),
        fetch(`${url}/api/earnings-history?ticker=${searchInput.toUpperCase()}`),
      ]);

      if (!infoRes.ok || !earningsRes.ok) {
        throw new Error("Failed to fetch data. Please check the ticker and try again.");
      }

      const infoData = await infoRes.json();
      const earningsData = await earningsRes.json();
      setCompanyInfo(infoData);
      setEarningsHistory(earningsData.earnings || []);
      setEarningsAnalysis(earningsData.earnings_summary);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Optional Earnings</h1>
      </header>

      <main className={styles.main}>
        <SearchBar
          setSearchInput={setSearchInput}
          handleSearch={handleSearch}
          selectedCompany={selectedCompany}
          setSelectedCompany={setSelectedCompany}
          loading={loading}
          sp500Companies={sP500Companies}
        />

        {error && <div className={styles.error}>{error}</div>}

        <CompanyInfoCard companyInfo={companyInfo} />
        
        <EarningsTable earningsHistory={earningsHistory} />

        <EarningsHistorySummary summary={earningsAnalysis} />

        <UpcomingEarningsList loading={loadingUpcoming} earnings={upcomingEarnings} />
      </main>
    </div>
  );
}