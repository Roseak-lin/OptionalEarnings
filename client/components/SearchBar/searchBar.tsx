import React, { useState } from "react";
import type { CompanyInfo } from "@/types";
import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import styles from "./searchBar.module.css";

interface SearchBarProps {
  setSearchInput: (value: string | null) => void;
  selectedCompany: CompanyInfo | null;
  setSelectedCompany: (value: CompanyInfo | null) => void;
  handleSearch: (e: React.FormEvent) => void;
  loading: boolean;
  sp500Companies?: CompanyInfo[];
}

export default function SearchBar({
  setSearchInput,
  selectedCompany,
  setSelectedCompany,
  handleSearch,
  loading,
  sp500Companies,
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const filteredCompanies: CompanyInfo[] | undefined =
    query === ""
      ? []
      : sp500Companies?.filter(
          (company) =>
            company.name.toLowerCase().startsWith(query.toLowerCase()) ||
            company.ticker.toLowerCase().startsWith(query.toLowerCase()),
        );

  return (
    <div className={styles.container}>
      <Combobox
        value={selectedCompany}
        onChange={(company: CompanyInfo | null) => {
          setSelectedCompany(company);
          setSearchInput(company ? company.ticker : null);
        }}
        virtual={{ options: filteredCompanies as CompanyInfo[] | null[] }}
      >
        <ComboboxInput
          displayValue={(company: CompanyInfo) =>
            company ? `${company.name} (${company.ticker})` : ""
          }
          onChange={(e) => setQuery(e.target.value)}
          className={styles.input}
          autoComplete="off"
        />

        <ComboboxOptions anchor="bottom" className={styles.options}>
          {({ option }) => (
            <ComboboxOption value={option} className={styles.option}>
              {option.name} ({option.ticker})
            </ComboboxOption>
          )}
        </ComboboxOptions>
      </Combobox>

      <button
        type="submit"
        disabled={loading}
        className={styles.button}
        onClick={handleSearch}
      >
        {loading ? "Searching..." : "Search"}
      </button>
    </div>
  );
}