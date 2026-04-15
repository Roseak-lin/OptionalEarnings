import type { UpcomingEarnings } from "@/types";
import UpcomingEarningsCard from "./upcomingEarningsCard";

type UpcomingEarningsProps = {
  earnings: UpcomingEarnings[];
};

export default function UpcomingEarnings({ earnings }: UpcomingEarningsProps) {
  return (
    <div className="columns-lg gap-4">
      {earnings.length === 0 ? (
        <></>
      ) : (
        earnings.map((earning, index) => (
          <UpcomingEarningsCard key={index} earningsDetails={earning} />
        ))
      )}
    </div>
  );
}
