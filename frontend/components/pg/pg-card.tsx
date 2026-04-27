import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { PGListing } from "@/lib/types";
import { rentRange } from "@/components/pg/state";

export function PublicPGCard({ pg }: { pg: PGListing }) {
  const primary = pg.photos.find((photo) => photo.is_primary) ?? pg.photos[0];
  const facilities = [
    pg.food_available && "Food",
    pg.wifi_available && "Wi-Fi",
    pg.ac_available && "AC",
    pg.laundry_available && "Laundry",
    pg.security_available && "Security",
  ].filter(Boolean);

  return (
    <Card className="overflow-hidden">
      {primary ? (
        <img src={primary.image_url} alt={pg.pg_name} className="h-48 w-full object-cover" />
      ) : (
        <div className="flex h-48 items-center justify-center bg-stone-100 text-sm text-stone-500">No photo yet</div>
      )}
      <CardHeader>
        <CardTitle>{pg.pg_name}</CardTitle>
        <CardDescription>{pg.is_featured ? "Featured - " : ""}{pg.distance_from_lpu_km ? `${pg.distance_from_lpu_km} km from LPU` : "Distance not listed"}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="font-medium text-stone-950">{rentRange(pg.monthly_rent_min, pg.monthly_rent_max)}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="rounded-md bg-stone-100 px-2 py-1 text-xs">{pg.gender_allowed.replace("_", " ")}</span>
          <span className="rounded-md bg-emerald-50 px-2 py-1 text-xs text-emerald-800">Verified</span>
          {pg.is_featured ? <span className="rounded-md bg-amber-100 px-2 py-1 text-xs text-amber-800">Featured</span> : null}
          {pg.review_count ? <span className="rounded-md bg-stone-100 px-2 py-1 text-xs">{pg.average_rating}/5 ({pg.review_count})</span> : null}
          {facilities.map((facility) => <span key={String(facility)} className="rounded-md bg-emerald-50 px-2 py-1 text-xs text-emerald-800">{facility}</span>)}
        </div>
        <Button asChild className="mt-4 w-full">
          <Link href={`/pgs/${pg.id}`}>View Details</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
