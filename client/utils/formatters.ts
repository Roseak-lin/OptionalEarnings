export const formatCurrencyLarge = (num: number | null | undefined) => {
  if (num === null || num === undefined) return "N/A";
  if (Math.abs(num) >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
  if (Math.abs(num) >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
  return `$${num.toLocaleString()}`;
};

export const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("en-US", {
    timeZone: "UTC",
  });
};

export const formatDateTime = (dateString: string | null | undefined) => {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleString("en-US", { timeZone: "UTC" });
};

export const formatPercentage = (num: number | null | undefined) => {
  if (num === null || num === undefined) return "N/A";
  return `${num.toFixed(2)}%`;
};