"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { useAuth } from "@/components/auth/auth-provider";
import { ErrorState, LoadingState } from "@/components/pg/state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createCreditOrder, getCreditTransactions, getWallet, markCreditPaymentFailed, verifyCreditPayment } from "@/lib/api-client";
import { loadRazorpayScript, type RazorpayFailureResponse, type RazorpaySuccessResponse } from "@/lib/razorpay";
import type { CreditTransaction, CreditWallet } from "@/lib/types";

export default function StudentCreditsPage() {
  const { user } = useAuth();
  const [wallet, setWallet] = useState<CreditWallet | null>(null);
  const [transactions, setTransactions] = useState<CreditTransaction[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isBuying, setIsBuying] = useState(false);

  async function load() {
    const [walletData, txData] = await Promise.all([getWallet(), getCreditTransactions()]);
    setWallet(walletData);
    setTransactions(txData.items);
  }

  useEffect(() => { load().catch((err) => setError(err instanceof Error ? err.message : "Could not load credits.")); }, []);

  async function handlePaymentFailure(response: RazorpayFailureResponse) {
    const orderId = response.error?.metadata?.order_id;
    const paymentId = response.error?.metadata?.payment_id;
    const reason = response.error?.description ?? response.error?.reason ?? "Payment failed.";

    setIsBuying(false);
    setError(reason);

    if (!orderId) return;
    try {
      await markCreditPaymentFailed({
        razorpay_order_id: orderId,
        razorpay_payment_id: paymentId,
        reason,
      });
    } catch {
      // The UI should stay on the normal failure message even if status logging fails.
    }
  }

  async function buyCredits() {
    setError(null);
    setMessage(null);
    setIsBuying(true);
    try {
      const loaded = await loadRazorpayScript();
      if (!loaded || !window.Razorpay) throw new Error("Could not load Razorpay Checkout.");
      const order = await createCreditOrder();
      const checkout = new window.Razorpay({
        key: order.razorpay_key_id || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "",
        amount: order.amount_paise,
        currency: order.currency,
        name: "CampusStay",
        description: `${order.credits} credits`,
        order_id: order.order_id,
        prefill: { name: user?.full_name, email: user?.email, contact: user?.phone ?? undefined },
        theme: { color: "#047857" },
        modal: { ondismiss: () => { setIsBuying(false); setMessage("Payment cancelled."); } },
        handler: async (response: RazorpaySuccessResponse) => {
          try {
            const verified = await verifyCreditPayment(response);
            await load();
            setMessage(verified.already_verified ? "Payment was already verified." : `Payment verified. Added ${verified.credits_added} credits.`);
          } catch (err) {
            setError(err instanceof Error ? err.message : "Payment verification failed.");
          } finally {
            setIsBuying(false);
          }
        },
      });
      checkout.on("payment.failed", handlePaymentFailure);
      checkout.open();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start payment.");
      setIsBuying(false);
    }
  }

  return (
    <ProtectedRoute roles={["student"]}>
      <main className="mx-auto max-w-6xl px-4 py-12">
        <h1 className="text-3xl font-semibold">Credits</h1>
        <p className="mt-2 text-stone-600">1 credit = 1 PG owner contact unlock. Rs. 10 = 10 credits.</p>
        {error ? <div className="mt-4"><ErrorState message={error} /></div> : null}
        {message ? <p className="mt-4 rounded-md bg-emerald-50 p-3 text-sm text-emerald-800">{message}</p> : null}
        {!wallet ? <LoadingState /> : (
          <div className="mt-8 grid gap-6 lg:grid-cols-[360px_1fr]">
            <Card>
              <CardHeader><CardTitle>{wallet.balance} credits</CardTitle><CardDescription>Current balance</CardDescription></CardHeader>
              <CardContent className="grid gap-3 text-sm">
                <p>Signup bonus: {wallet.signup_bonus_credits}</p>
                <p>Purchased: {wallet.total_purchased_credits}</p>
                <p>Used: {wallet.total_used_credits}</p>
                <Button disabled={isBuying} onClick={buyCredits}>{isBuying ? "Opening payment..." : "Buy 10 Credits"}</Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Transaction history</CardTitle><CardDescription>Additions are positive. Unlocks are negative.</CardDescription></CardHeader>
              <CardContent className="grid gap-3">
                {transactions.length === 0 ? <p className="text-sm text-stone-600">No transactions yet.</p> : transactions.map((tx) => (
                  <div key={tx.id} className="flex justify-between rounded-md border p-3 text-sm">
                    <span>{tx.reason ?? tx.type}</span>
                    <span className={tx.amount >= 0 ? "text-emerald-700" : "text-red-700"}>{tx.amount > 0 ? `+${tx.amount}` : tx.amount}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </ProtectedRoute>
  );
}
