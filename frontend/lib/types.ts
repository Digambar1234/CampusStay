export type UserRole = "student" | "pg_owner" | "admin" | "super_admin";

export type AuthUser = {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string | null;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
};

export type ListingStatus = "draft" | "pending_review" | "approved" | "rejected" | "suspended";
export type GenderAllowed = "boys" | "girls" | "co_living";
export type RoomType = "single" | "double_sharing" | "triple_sharing" | "four_sharing" | "dormitory";
export type ImageType = "room" | "washroom" | "building" | "mess" | "common_area" | "other";

export type PGRoom = {
  id: string;
  pg_id: string;
  room_type: RoomType;
  price_per_month: number;
  available_beds: number;
  ac_available: boolean;
  attached_washroom: boolean;
  created_at: string;
  updated_at: string;
};

export type PGPhoto = {
  id: string;
  pg_id: string;
  image_url: string;
  public_id: string | null;
  image_type: ImageType;
  is_primary: boolean;
  created_at: string;
};

export type PGListing = {
  id: string;
  owner_id: string;
  pg_name: string;
  description: string | null;
  address: string;
  landmark: string | null;
  distance_from_lpu_km: string | null;
  latitude: string | null;
  longitude: string | null;
  gender_allowed: GenderAllowed;
  food_available: boolean;
  wifi_available: boolean;
  ac_available: boolean;
  laundry_available: boolean;
  parking_available: boolean;
  security_available: boolean;
  monthly_rent_min: number | null;
  monthly_rent_max: number | null;
  deposit_amount: number | null;
  status: ListingStatus;
  admin_verified: boolean;
  created_at: string;
  updated_at: string;
  rooms: PGRoom[];
  photos: PGPhoto[];
  owner_phone?: string;
  whatsapp_number?: string | null;
  owner?: {
    id: string;
    full_name: string;
    email: string;
    phone: string | null;
  };
  average_rating?: number | null;
  review_count?: number;
  is_featured?: boolean;
};

export type PGListingSummary = {
  id: string;
  pg_name: string;
  address: string;
  distance_from_lpu_km: string | null;
  gender_allowed: GenderAllowed;
  monthly_rent_min: number | null;
  monthly_rent_max: number | null;
  status: ListingStatus;
  admin_verified: boolean;
  rooms_count: number;
  photos_count: number;
  primary_photo_url: string | null;
  created_at: string;
};

export type Paginated<T> = {
  items: T[];
  total: number;
  page?: number;
  page_size?: number;
};

export type CreditWallet = {
  student_id: string;
  balance: number;
  total_purchased_credits: number;
  total_used_credits: number;
  signup_bonus_credits: number;
  created_at: string;
  updated_at: string;
};

export type CreditTransaction = {
  id: string;
  type: "free_signup_bonus" | "purchase" | "contact_unlock" | "refund" | "admin_adjustment";
  amount: number;
  reason: string | null;
  created_at: string;
};

export type UnlockContactResponse = {
  pg_id: string;
  pg_name: string;
  owner_phone: string;
  whatsapp_number: string | null;
  already_unlocked: boolean;
  credits_used: number;
  remaining_balance: number;
};

export type UnlockStatus = {
  pg_id: string;
  is_unlocked: boolean;
  wallet_balance: number;
  can_unlock: boolean;
  reason: string | null;
};

export type UnlockedContact = {
  pg_id: string;
  pg_name: string;
  address: string;
  distance_from_lpu_km: string | null;
  monthly_rent_min: number | null;
  monthly_rent_max: number | null;
  owner_phone: string;
  whatsapp_number: string | null;
  primary_photo_url: string | null;
  unlocked_at: string;
};

export type CreditOrder = {
  order_id: string;
  amount_rupees: number;
  amount_paise: number;
  credits: number;
  currency: "INR";
  razorpay_key_id: string;
};

export type VerifyPaymentResponse = {
  payment_status: "created" | "paid" | "failed" | "refunded";
  wallet_balance: number;
  credits_added: number;
  already_verified: boolean;
};

export type ReviewStatus = "pending" | "approved" | "hidden" | "rejected";
export type Review = {
  id: string;
  pg_id: string;
  pg_name?: string;
  rating: number;
  title: string | null;
  comment: string;
  status: ReviewStatus;
  is_edited: boolean;
  reviewer_name?: string;
  student_name?: string;
  student_email?: string;
  created_at: string;
  updated_at: string;
};

export type ReviewList = { items: Review[]; total: number; average_rating: number | null };
export type ReportType = "fake_listing" | "wrong_price" | "wrong_phone" | "room_not_available" | "misleading_photos" | "abusive_owner" | "other";
export type ReportStatus = "open" | "reviewed" | "resolved" | "rejected";
export type ReportPriority = "low" | "medium" | "high";
export type Report = {
  id: string;
  pg_id: string;
  pg_name: string;
  student_id: string | null;
  reporter_email: string | null;
  reporter_phone: string | null;
  report_type: ReportType;
  priority: ReportPriority;
  reason: string;
  description: string | null;
  status: ReportStatus;
  admin_note: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
};

export type FeaturedListing = {
  id: string;
  pg_id: string;
  pg_name: string;
  owner_id: string;
  status: "active" | "expired" | "cancelled" | "pending";
  starts_at: string;
  ends_at: string;
  amount_rupees: number;
  source: "admin_grant" | "paid";
  created_at: string;
  updated_at: string;
};

export type OwnerAnalyticsSummary = {
  total_listings: number;
  approved_listings: number;
  pending_listings: number;
  rejected_listings: number;
  total_views: number;
  total_contact_unlocks: number;
  total_reviews: number;
  average_rating_across_listings: number | null;
  active_featured_listings: number;
};

export type OwnerListingAnalytics = {
  pg_id: string;
  pg_name: string;
  status: ListingStatus;
  views_count: number;
  contact_unlock_count: number;
  review_count: number;
  average_rating: number | null;
  is_featured: boolean;
  created_at: string;
};

export type AdminAnalyticsSummary = {
  total_users: number;
  total_students: number;
  total_pg_owners: number;
  total_pg_listings: number;
  approved_pg_listings: number;
  pending_pg_listings: number;
  rejected_pg_listings: number;
  suspended_pg_listings: number;
  total_contact_unlocks: number;
  total_credit_revenue_rupees: number;
  total_credits_purchased: number;
  total_reviews: number;
  total_reports: number;
  open_reports: number;
  active_featured_listings: number;
};

export type AdminRevenue = { total_revenue_rupees: number; credits_sold: number; payments: Array<Record<string, string | number>> };
export type TopPG = { pg_id: string; pg_name: string; views: number; unlocks: number; average_rating: number | null; review_count: number };
export type AuditLog = { id: string; admin_id: string; admin_name: string; admin_email: string; action: string; target_type: string; target_id: string | null; metadata: Record<string, unknown> | null; created_at: string };
export type ReadyResponse = { status: "ready" | "degraded" | "not_ready"; checks: Record<string, { ok: boolean; [key: string]: boolean | string }> };
