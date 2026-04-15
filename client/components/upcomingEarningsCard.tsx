import type { UpcomingEarnings } from "@/types";

export default function UpcomingEarningsCard({
  earningsDetails,
}: {
  earningsDetails: UpcomingEarnings;
}) {
  return (
    <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 transition-all hover:shadow-md mb-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-zinc-900 dark:text-zinc-50">
          {earningsDetails.ticker}
        </h3>
        <span className="px-2.5 py-1 text-xs font-medium rounded-md bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300">
          {earningsDetails.earnings_date}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="flex flex-col">
          <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-1">
            EPS Estimate
          </span>
          <span className="font-medium text-zinc-900 dark:text-zinc-100">
            {earningsDetails.eps_estimate !== null &&
            earningsDetails.eps_estimate !== undefined
              ? earningsDetails.eps_estimate
              : "N/A"}
          </span>
        </div>

        <div className="flex flex-col">
          <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-1">
            Timing
          </span>
          <span className="font-medium text-zinc-900 dark:text-zinc-100 capitalize">
            {earningsDetails.timing || "Unspecified"}
          </span>
        </div>
      </div>
    </div>
  );
}
