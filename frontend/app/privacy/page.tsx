export default function PrivacyPage() {
  return <Legal title="Privacy Policy" body={["CampusStay collects account, listing, payment, review, report, and contact unlock data needed to operate the platform.", "Owner contact details are protected and revealed only to logged-in students after a credit unlock.", "Students should physically inspect a PG before paying rent or deposit. For questions, contact support@campusstay.in."]} />;
}

function Legal({ title, body }: { title: string; body: string[] }) { return <main className="mx-auto max-w-3xl px-4 py-12"><h1 className="text-3xl font-semibold">{title}</h1><div className="mt-6 grid gap-4 text-stone-700">{body.map((p) => <p key={p}>{p}</p>)}</div></main>; }
