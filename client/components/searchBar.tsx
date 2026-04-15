import React, { useState } from "react";
import type { CompanyInfo } from "@/types";

import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";

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
    <div className="flex items-center gap-2 w-full">
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
          className="w-full rounded-lg border-none bg-white/15 py-1.5 pr-8 pl-3 text-sm/6 text-white"
        />

        <ComboboxOptions
          anchor="bottom"
          className="w-(--input-width) rounded-xl border border-white/30 bg-black/90 p-1 [--anchor-gap:--spacing(1)] [--anchor-max-height:280px]"
        >
          {({ option }) => (
            <ComboboxOption
              value={option}
              className="w-full group flex cursor-default items-center gap-2 rounded-lg px-3 py-1.5 select-none data-focus:bg-white/10"
            >
              {option.name} ({option.ticker})
            </ComboboxOption>
          )}
        </ComboboxOptions>
      </Combobox>

      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-zinc-900 dark:bg-white px-4 py-2 text-sm font-medium text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-zinc-200 disabled:opacity-50 shrink-0"
        onClick={handleSearch}
      >
        {loading ? "Searching..." : "Search"}
      </button>
    </div>
  );
}
