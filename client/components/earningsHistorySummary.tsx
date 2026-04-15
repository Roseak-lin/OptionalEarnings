export default function EarningsHistorySummary({
  summary,
}: {
  summary: string;
}) {
  if (!summary) return null;
  return (
    <section>
      <h2 className="text-lg font-semibold p-2">Summary: </h2>
      <div>
        <p className="p-2">{summary}</p>
      </div>
    </section>
  );
}
