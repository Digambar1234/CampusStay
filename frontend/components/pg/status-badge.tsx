import type { ListingStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const styles: Record<ListingStatus, string> = {
  draft: "bg-stone-100 text-stone-700",
  pending_review: "bg-amber-100 text-amber-800",
  approved: "bg-emerald-100 text-emerald-800",
  rejected: "bg-red-100 text-red-800",
  suspended: "bg-red-950 text-white",
};

export function StatusBadge({ status }: { status: ListingStatus }) {
  return (
    <span className={cn("inline-flex rounded-md px-2.5 py-1 text-xs font-medium", styles[status])}>
      {status.replace("_", " ")}
    </span>
  );
}
