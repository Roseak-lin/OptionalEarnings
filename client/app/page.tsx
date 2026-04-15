"use client";

import React, { useEffect, useState } from "react";
import SearchBar from "@/components/searchBar";
import CompanyInfoCard from "@/components/companyInfoCard";
import EarningsTable from "@/components/earningsTable";
import EarningsHistorySummary from "@/components/earningsHistorySummary";

import type {CompanyInfo} from "@/types/index";
import UpcomingEarnings from "@/components/upcomingEarnings";

export default function Home() {
  const [searchInput, setSearchInput] = useState<string | null>("");
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [earningsHistory, setEarningsHistory] = useState<any[]>([]);
  const [earningsAnalysis, setEarningsAnalysis] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sP500Companies, setSP500Companies] = useState<CompanyInfo[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<CompanyInfo | null>(null);
  const [upcomingEarnings, setUpcomingEarnings] = useState<any[]>([]);

  const url = process.env.BACKEND_URL_LOCAL || "http://localhost:8000";
  
  useEffect(() => {
    // fetch SP500 companies for search dropdown
    fetch(`${url}/api/sp500-companies`)
      .then((res) => res.json())
      .then((data) => {
        setSP500Companies(data);
      })
      .catch((err) => console.error("Error fetching SP500 companies:", err));
  
    // fetch upcoming earnings for SP500 companies
    fetch(`${url}/api/get-upcoming-earnings`)
      .then((res) => res.json())
      .then((data) => {
        setUpcomingEarnings(data || []);
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
        fetch(
          `${url}/api/company-info?ticker=${searchInput.toUpperCase()}`,
        ),
        fetch(
          `${url}/api/earnings-history?ticker=${searchInput.toUpperCase()}`,
        ),
      ]);

      if (!infoRes.ok || !earningsRes.ok) {
        throw new Error(
          "Failed to fetch data. Please check the ticker and try again.",
        );
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
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-zinc-900 dark:text-zinc-50">
      <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 px-6 py-4">
        <h1 className="text-xl font-bold tracking-tight">Optional Earnings</h1>
      </header>

      <main className="p-6 max-w-7xl mx-auto space-y-8">
        <SearchBar
          setSearchInput={setSearchInput}
          handleSearch={handleSearch}
          selectedCompany={selectedCompany}
          setSelectedCompany={setSelectedCompany}
          loading={loading}
          sp500Companies={sP500Companies}
        />

        {error && <div className="text-red-500 font-medium">{error}</div>}

        <CompanyInfoCard companyInfo={companyInfo} />

        <EarningsTable earningsHistory={earningsHistory} />

        <EarningsHistorySummary summary={earningsAnalysis} />
        
        <UpcomingEarnings earnings={upcomingEarnings} />
      </main>
    </div>
  );
}