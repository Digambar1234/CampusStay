import type {
  AuthResponse,
  CreditOrder,
  CreditTransaction,
  CreditWallet,
  ImageType,
  PGListing,
  PGListingSummary,
  PGPhoto,
  PGRoom,
  Paginated,
  UnlockContactResponse,
  UnlockStatus,
  UnlockedContact,
  VerifyPaymentResponse,
  AdminAnalyticsSummary,
  AdminRevenue,
  FeaturedListing,
  OwnerAnalyticsSummary,
  OwnerListingAnalytics,
  Report,
  ReportPriority,
  ReportStatus,
  ReportType,
  Review,
  ReviewList,
  TopPG,
  AuditLog,
  ReadyResponse,
  LoginOtpStartResponse,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "campusstay_access_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

type RequestOptions = RequestInit & {
  auth?: boolean;
};

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  if (options.auth !== false) {
    const token = getStoredToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401) {
      clearStoredToken();
      if (typeof window !== "undefined" && !window.location.pathname.includes("/login")) {
        window.dispatchEvent(new CustomEvent("campusstay:session-expired"));
      }
    }
    const message = payload?.error?.message ?? payload?.detail ?? "Something went wrong. Please try again.";
    if (Array.isArray(message)) throw new Error(message[0]?.msg ?? "Request failed.");
    if (typeof message === "object" && message?.message) throw new Error(message.message);
    if (typeof message === "object" && message?.code) throw new Error(message.code);
    throw new Error(message);
  }
  return payload as T;
}

export function login(email: string, password: string) {
  return apiRequest<AuthResponse>("/api/v1/auth/login", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password }),
  });
}

export function startLoginOtp(email: string, password: string) {
  return apiRequest<LoginOtpStartResponse>("/api/v1/auth/login/start", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password }),
  });
}

export function verifyLoginOtp(challenge_id: string, otp: string) {
  return apiRequest<AuthResponse>("/api/v1/auth/login/verify-otp", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ challenge_id, otp }),
  });
}

export function register(input: {
  full_name: string;
  email: string;
  phone?: string;
  password: string;
  role: "student" | "pg_owner";
}) {
  return apiRequest<AuthResponse>("/api/v1/auth/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify(input),
  });
}

export type ListingPayload = {
  pg_name: string;
  description?: string | null;
  address: string;
  landmark?: string | null;
  distance_from_lpu_km?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  gender_allowed: "boys" | "girls" | "co_living";
  food_available: boolean;
  wifi_available: boolean;
  ac_available: boolean;
  laundry_available: boolean;
  parking_available: boolean;
  security_available: boolean;
  monthly_rent_min?: number | null;
  monthly_rent_max?: number | null;
  deposit_amount?: number | null;
  owner_phone: string;
  whatsapp_number?: string | null;
};

export type RoomPayload = {
  room_type: "single" | "double_sharing" | "triple_sharing" | "four_sharing" | "dormitory";
  price_per_month: number;
  available_beds: number;
  ac_available: boolean;
  attached_washroom: boolean;
};

export function getOwnerListings() {
  return apiRequest<Paginated<PGListingSummary>>("/api/v1/owner/listings");
}

export function createOwnerListing(input: ListingPayload, submit = false) {
  return apiRequest<PGListing>(`/api/v1/owner/listings?submit=${submit}`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getOwnerListing(id: string) {
  return apiRequest<PGListing>(`/api/v1/owner/listings/${id}`);
}

export function updateOwnerListing(id: string, input: Partial<ListingPayload>) {
  return apiRequest<PGListing>(`/api/v1/owner/listings/${id}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function submitOwnerListing(id: string) {
  return apiRequest<PGListing>(`/api/v1/owner/listings/${id}/submit`, { method: "POST" });
}

export function deleteOwnerListing(id: string) {
  return apiRequest<{ message: string }>(`/api/v1/owner/listings/${id}`, { method: "DELETE" });
}

export function addRoom(pgId: string, input: RoomPayload) {
  return apiRequest<PGRoom>(`/api/v1/owner/listings/${pgId}/rooms`, { method: "POST", body: JSON.stringify(input) });
}

export function updateRoom(pgId: string, roomId: string, input: Partial<RoomPayload>) {
  return apiRequest<PGRoom>(`/api/v1/owner/listings/${pgId}/rooms/${roomId}`, { method: "PATCH", body: JSON.stringify(input) });
}

export function deleteRoom(pgId: string, roomId: string) {
  return apiRequest<{ message: string }>(`/api/v1/owner/listings/${pgId}/rooms/${roomId}`, { method: "DELETE" });
}

export async function uploadPhoto(pgId: string, input: { file: File; image_type: ImageType; is_primary: boolean }) {
  const token = getStoredToken();
  const formData = new FormData();
  formData.set("file", input.file);
  formData.set("image_type", input.image_type);
  formData.set("is_primary", String(input.is_primary));
  const response = await fetch(`${API_BASE_URL}/api/v1/owner/listings/${pgId}/photos`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok) throw new Error(payload?.error?.message ?? payload?.detail ?? "Photo upload failed.");
  return payload as PGPhoto;
}

export function deletePhoto(pgId: string, photoId: string) {
  return apiRequest<{ message: string }>(`/api/v1/owner/listings/${pgId}/photos/${photoId}`, { method: "DELETE" });
}

export function markPrimaryPhoto(pgId: string, photoId: string) {
  return apiRequest<PGPhoto>(`/api/v1/owner/listings/${pgId}/photos/${photoId}/primary`, { method: "PATCH" });
}

export function getAdminPGs(status: "pending" | "approved" | "rejected") {
  return apiRequest<Paginated<PGListing>>(`/api/v1/admin/pgs/${status}`);
}

export function getAdminPG(id: string) {
  return apiRequest<PGListing>(`/api/v1/admin/pgs/${id}`);
}

export function approvePG(id: string) {
  return apiRequest<PGListing>(`/api/v1/admin/pgs/${id}/approve`, { method: "POST" });
}

export function rejectPG(id: string, reason: string) {
  return apiRequest<PGListing>(`/api/v1/admin/pgs/${id}/reject`, { method: "POST", body: JSON.stringify({ reason }) });
}

export function suspendPG(id: string, reason: string) {
  return apiRequest<PGListing>(`/api/v1/admin/pgs/${id}/suspend`, { method: "POST", body: JSON.stringify({ reason }) });
}

export function requestPGChanges(id: string, message: string) {
  return apiRequest<PGListing>(`/api/v1/admin/pgs/${id}/request-changes`, { method: "POST", body: JSON.stringify({ message }) });
}

export function getPublicPGs(query = "") {
  return apiRequest<Paginated<PGListing>>(`/api/v1/pgs${query}`, { auth: false });
}

export function getPublicPG(id: string) {
  return apiRequest<PGListing>(`/api/v1/pgs/${id}`, { auth: false });
}

export function getWallet() {
  return apiRequest<CreditWallet>("/api/v1/credits/wallet");
}

export function getCreditTransactions() {
  return apiRequest<Paginated<CreditTransaction>>("/api/v1/credits/transactions");
}

export function createCreditOrder() {
  return apiRequest<CreditOrder>("/api/v1/credits/create-order", {
    method: "POST",
    body: JSON.stringify({ pack: "credits_10" }),
  });
}

export function verifyCreditPayment(input: {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}) {
  return apiRequest<VerifyPaymentResponse>("/api/v1/credits/verify-payment", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function markCreditPaymentFailed(input: {
  razorpay_order_id: string;
  razorpay_payment_id?: string;
  reason?: string;
}) {
  return apiRequest<{ payment_status: "created" | "paid" | "failed" | "refunded" }>("/api/v1/credits/mark-payment-failed", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function createTestCreditPurchase() {
  return apiRequest<{ payment_status: "paid"; wallet_balance: number; credits_added: number }>("/api/v1/credits/test-purchase", {
    method: "POST",
  });
}

export function unlockContact(pgId: string) {
  return apiRequest<UnlockContactResponse>(`/api/v1/credits/unlock-contact/${pgId}`, { method: "POST" });
}

export function getUnlockStatus(pgId: string) {
  return apiRequest<UnlockStatus>(`/api/v1/credits/unlock-status/${pgId}`);
}

export function getUnlockedContacts() {
  return apiRequest<UnlockedContact[]>("/api/v1/credits/unlocked-contacts");
}

export function getPGReviews(pgId: string) {
  return apiRequest<ReviewList>(`/api/v1/reviews/pg/${pgId}`, { auth: false });
}

export function createReview(pgId: string, data: { rating: number; title?: string | null; comment: string }) {
  return apiRequest<Review>(`/api/v1/reviews/pg/${pgId}`, { method: "POST", body: JSON.stringify(data) });
}

export function updateReview(reviewId: string, data: { rating?: number; title?: string | null; comment?: string }) {
  return apiRequest<Review>(`/api/v1/reviews/${reviewId}`, { method: "PATCH", body: JSON.stringify(data) });
}

export function deleteReview(reviewId: string) {
  return apiRequest<{ message: string }>(`/api/v1/reviews/${reviewId}`, { method: "DELETE" });
}

export function getMyReviews() {
  return apiRequest<Review[]>("/api/v1/student/reviews");
}

export function createReport(pgId: string, data: { report_type: ReportType; reason: string; description?: string | null; reporter_email?: string | null; reporter_phone?: string | null }) {
  return apiRequest<Report>(`/api/v1/reports/pg/${pgId}`, { method: "POST", body: JSON.stringify(data), auth: Boolean(getStoredToken()) });
}

export function getMyReports() {
  return apiRequest<Report[]>("/api/v1/student/reports");
}

export function adminGetReports() {
  return apiRequest<Report[]>("/api/v1/admin/reports");
}

export function adminUpdateReport(id: string, data: { status?: ReportStatus; priority?: ReportPriority; admin_note?: string | null }) {
  return apiRequest<Report>(`/api/v1/admin/reports/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export function adminResolveReport(id: string) {
  return apiRequest<Report>(`/api/v1/admin/reports/${id}/resolve`, { method: "POST" });
}

export function getOwnerAnalyticsSummary() {
  return apiRequest<OwnerAnalyticsSummary>("/api/v1/owner/analytics/summary");
}

export function getOwnerListingAnalytics() {
  return apiRequest<OwnerListingAnalytics[]>("/api/v1/owner/analytics/listings");
}

export function getAdminAnalyticsSummary() {
  return apiRequest<AdminAnalyticsSummary>("/api/v1/admin/analytics/summary");
}

export function getAdminRevenueAnalytics() {
  return apiRequest<AdminRevenue>("/api/v1/admin/analytics/revenue");
}

export function getAdminTopPGs() {
  return apiRequest<TopPG[]>("/api/v1/admin/analytics/top-pgs");
}

export function adminGetReviews() {
  return apiRequest<Review[]>("/api/v1/admin/reviews");
}

export function adminApproveReview(id: string) {
  return apiRequest<{ message: string }>(`/api/v1/admin/reviews/${id}/approve`, { method: "POST" });
}

export function adminHideReview(id: string) {
  return apiRequest<{ message: string }>(`/api/v1/admin/reviews/${id}/hide`, { method: "POST" });
}

export function adminRejectReview(id: string) {
  return apiRequest<{ message: string }>(`/api/v1/admin/reviews/${id}/reject`, { method: "POST" });
}

export function adminCreateFeaturedListing(data: { pg_id: string; days: number; amount_rupees?: number; source?: "admin_grant" | "paid" }) {
  return apiRequest<FeaturedListing>("/api/v1/admin/featured-listings", { method: "POST", body: JSON.stringify(data) });
}

export function adminGetFeaturedListings() {
  return apiRequest<FeaturedListing[]>("/api/v1/admin/featured-listings");
}

export function adminCancelFeaturedListing(id: string) {
  return apiRequest<FeaturedListing>(`/api/v1/admin/featured-listings/${id}/cancel`, { method: "POST" });
}

export function getAuditLogs(query = "") {
  return apiRequest<Paginated<AuditLog>>(`/api/v1/admin/audit-logs${query}`);
}

export function getReadyStatus() {
  return apiRequest<ReadyResponse>("/ready", { auth: false });
}
