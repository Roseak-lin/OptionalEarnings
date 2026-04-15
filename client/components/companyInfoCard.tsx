import { formatCurrencyLarge } from "../utils/formatters";

interface CompanyInfoCardProps {
  companyInfo: any;
}

export default function CompanyInfoCard({ companyInfo }: CompanyInfoCardProps) {
  if (!companyInfo) return null;

  return (
    <section className="p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
      <h2 className="text-2xl font-bold mb-2">
        {companyInfo.company_name} ({companyInfo.ticker})
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
        <div>
          <span className="text-zinc-500 block">Sector</span>
          <span className="font-medium">{companyInfo.sector || "N/A"}</span>
        </div>
        <div>
          <span className="text-zinc-500 block">Industry</span>
          <span className="font-medium">{companyInfo.industry || "N/A"}</span>
        </div>
        <div>
          <span className="text-zinc-500 block">Location</span>
          <span className="font-medium">
            {companyInfo.city}, {companyInfo.country}
          </span>
        </div>
        <div>
          <span className="text-zinc-500 block">Market Cap</span>
          <span className="font-medium">
            {formatCurrencyLarge(companyInfo.marketCap)}
          </span>
        </div>
      </div>
      <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-4 leading-relaxed">
        {companyInfo.longBusinessSummary}
      </p>
    </section>
  );
}