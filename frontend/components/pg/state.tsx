import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <Card><CardHeader><CardTitle>{title}</CardTitle><CardDescription>{description}</CardDescription></CardHeader></Card>;
}

export function LoadingState() {
  return <div className="py-10 text-sm text-stone-600">Loading...</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{message}</div>;
}

export function rentRange(min?: number | null, max?: number | null) {
  if (!min && !max) return "Rent on request";
  if (min && max) return `Rs. ${min} - Rs. ${max}`;
  return `Rs. ${min ?? max}`;
}
