import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-stone-200 bg-stone-950 text-stone-300">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-3 lg:px-8">
        <div>
          <p className="text-lg font-semibold text-white">CampusStay</p>
          <p className="mt-3 max-w-sm text-sm leading-6">
            Verified PG discovery near LPU with accountable listings, contact unlocks, and admin review workflows.
          </p>
        </div>
        <div className="text-sm">
          <p className="font-semibold text-white">Platform</p>
          <div className="mt-3 grid gap-2">
            <Link href="/pgs">Browse PGs</Link>
            <Link href="/owner/listings/new">Owner registration</Link>
            <Link href="/student/credits">Credits</Link>
          </div>
        </div>
        <div className="text-sm">
          <p className="font-semibold text-white">Operations</p>
          <div className="mt-3 grid gap-2">
            <Link href="/admin/dashboard">Admin dashboard</Link>
            <Link href="/admin/pgs/pending">Pending PGs</Link>
            <Link href="/admin/users">Users</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
