# CSS / UI Audit Report — DE_GECR_WEBSITE

**Date:** Auto-generated  
**Scope:** All 27 template files across Student Portal (7), Faculty Portal (12), Auth Pages (7), and Landing Page (1)  
**Purpose:** Read-only analysis of CSS/UI inconsistencies across the entire template codebase

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [File Inventory & Line Counts](#2-file-inventory--line-counts)
3. [Shared Infrastructure](#3-shared-infrastructure)
4. [Student Portal — Per-File Analysis](#4-student-portal--per-file-analysis)
5. [Faculty Portal — Per-File Analysis](#5-faculty-portal--per-file-analysis)
6. [Auth Pages — Per-File Analysis](#6-auth-pages--per-file-analysis)
7. [Landing Page (index.html)](#7-landing-page-indexhtml)
8. [Cross-Portal Comparison Tables](#8-cross-portal-comparison-tables)
9. [Critical Inconsistencies](#9-critical-inconsistencies)
10. [Recommendations Summary](#10-recommendations-summary)

---

## 1. Executive Summary

The codebase consists of 27 HTML template files with **all CSS written inline in `<style>` blocks** — there is no shared CSS component system. Each file independently re-declares its own sidebar, card, button, and layout styles. This has resulted in significant drift between files, even within the same portal.

**Key findings:**
- **2 structural outliers** completely break from the sidebar layout pattern: `student/attendance.html` (plain Tailwind, no sidebar) and `faculty/students_subject_view.html` (no sidebar, loads Font Awesome, unique animation system)
- Faculty portal files split into **two distinct CSS "generations"**: a "full" style (6 files) and a "compact/minimal" style (6 files)
- Glass-card background opacity varies between `0.9` and `0.95` with no clear logic
- Card hover effects range from none, to simple translateY, to full 3D rotateX/rotateY — across the same portal
- Sidebar navigation links are inconsistent: some faculty pages are missing the "Announcements" link
- Logout button styling varies (color, icon) even within the same portal
- Auth pages are the **most consistent** group, sharing a common design system with minimal drift
- The landing page (`index.html`) has a completely unique, elaborate CSS architecture

---

## 2. File Inventory & Line Counts

### Student Portal (7 files)
| File | Lines | Has Sidebar |
|------|-------|-------------|
| `student/dashboard.html` | 882 | ✅ |
| `student/attendance.html` | ~290 | ❌ |
| `student/enroll-subjects.html` | 819 | ✅ |
| `student/events.html` | 1240 | ✅ |
| `student/profile.html` | 675 | ✅ |
| `student/schedule.html` | 860 | ✅ |
| `student/settings.html` | 806 | ✅ |

### Faculty Portal (12 files)
| File | Lines | Has Sidebar |
|------|-------|-------------|
| `faculty/dashboard.html` | 923 | ✅ |
| `faculty/attendance.html` | ~500 | ✅ |
| `faculty/assignments.html` | ~500 | ✅ |
| `faculty/enrollments.html` | ~400 | ✅ |
| `faculty/events.html` | 622 | ✅ |
| `faculty/manage-announcements.html` | ~440 | ✅ |
| `faculty/manage-subjects.html` | 329 | ✅ |
| `faculty/profile.html` | 674 | ✅ |
| `faculty/schedule.html` | 994 | ✅ |
| `faculty/settings.html` | 771 | ✅ |
| `faculty/subjects.html` | 918 | ✅ |
| `faculty/students_subject_view.html` | 760 | ❌ |

### Auth Pages (7 files)
| File | Lines |
|------|-------|
| `auth/login/student.html` | 242 |
| `auth/login/faculty.html` | 245 |
| `auth/login/student-register.html` | 318 |
| `auth/login/faculty-register.html` | 349 |
| `auth/login/student-forgot.html` | 350 |
| `auth/login/faculty-forgot.html` | 358 |
| `auth/verify-otp.html` | 323 |

### Landing Page (1 file)
| File | Lines |
|------|-------|
| `index.html` | 1288 |

**Total: ~14,387 lines of template code**

---

## 3. Shared Infrastructure

### CDN Dependencies (expected across all files)
| Resource | URL | Notes |
|----------|-----|-------|
| Tailwind CSS | `https://cdn.tailwindcss.com` | Missing from `student/attendance.html` |
| Inter Font | Google Fonts `Inter:wght@400;500;600;700` | Missing from `student/attendance.html` |
| Playfair Display | Google Fonts | Auth pages + index.html only |
| Font Awesome 6.5.1 | `cdnjs.cloudflare.com` | Auth pages + index.html + `faculty/students_subject_view.html` only |
| Font Awesome 6.0.0 | `cdnjs.cloudflare.com` | `faculty/students_subject_view.html` only (different version!) |
| Swiper.js | `cdn.jsdelivr.net` | `index.html` only |
| Chart.js | CDN | `student/attendance.html` only |
| Three.js | CDN | `student/dashboard.html` only |

### Common CSS Variables (`:root` block)
Most portal pages declare some subset of:
```css
:root {
    --primary: #4F46E5;
    --accent: #3B82F6;
    --bg: #f0f2f5;        /* Only in "full" CSS files */
    --text: #1f2937;       /* Only in "full" CSS files */
    --card-bg: #ffffff;    /* Only in "full" CSS files */
    --hover-bg: rgba(79, 70, 229, 0.08);
    --sidebar-width: 280px;
}
```

---

## 4. Student Portal — Per-File Analysis

### 4.1 `student/dashboard.html` (882 lines)
- **CSS approach:** Full inline `<style>` block with complete CSS variable set (`--bg`, `--text`, `--card-bg`)
- **Color scheme:** Indigo primary (`#4F46E5`), blue accent (`#3B82F6`)
- **Sidebar:** 280px fixed, glass-morphism (`backdrop-filter: blur(10px)`), gradient-text header "GEC Rajkot", `::before` pseudo-element hover effect, scrollbar styling, `.menu-divider` CSS class
- **Top bar:** Transparent bar with search, notification bell dropdown, profile avatar with gradient border
- **Main content:** `margin-left: 300px`, gradient mesh background
- **Card styles:** `.glass-card` bg `rgba(255,255,255,0.9)`, 3D hover (`translateY(-5px) rotateX(2deg) rotateY(2deg)`) with `transform-style: preserve-3d; perspective: 1000px`
- **Fonts:** Inter (Google Fonts CDN)
- **Button styles:** Gradient primary buttons
- **Logout:** `text-gray-600`, circle arrow SVG (`M11 15l-3-3...`)
- **Unique:** Three.js canvas background, progress-bar styles, notification dropdown system, events notification badge

### 4.2 `student/attendance.html` (~290 lines) ⚠️ OUTLIER
- **CSS approach:** ⚠️ **NO `<style>` block at all** — pure Tailwind utility classes
- **Color scheme:** Tailwind defaults (`bg-gray-100`, `bg-blue-600`)
- **Sidebar:** ❌ **NONE** — standalone page with "Back to Dashboard" button
- **Top bar:** None
- **Main content:** `max-w-7xl mx-auto p-6` container
- **Card styles:** `bg-white rounded-lg shadow p-6` (plain Tailwind)
- **Fonts:** ⚠️ No Inter font loaded, no Google Fonts link
- **Button styles:** `bg-blue-600 text-white px-4 py-2 rounded` (inline Tailwind)
- **Logout:** N/A
- **Unique:** Loads Chart.js for attendance visualization. **Completely different design language** from all other portal pages.

### 4.3 `student/enroll-subjects.html` (819 lines)
- **CSS approach:** Full `<style>` block with CSS variables
- **Color scheme:** Same indigo/blue
- **Sidebar:** Same structure, `::before` hover, scrollbar styles
- **Top bar:** Similar to dashboard
- **Main content:** ⚠️ `margin-left: 310px` (inconsistent — should be 300px)
- **Card styles:** `.glass-card` bg `rgba(255,255,255,0.95)` (differs from dashboard's 0.9), hover `translateY(-2px)` (simpler than dashboard's 3D)
- **Fonts:** Inter
- **Button styles:** Gradient buttons
- **Logout:** ⚠️ `text-red-500` (differs from dashboard's gray-600), door arrow SVG (different icon)
- **Unique:** Menu divider uses inline style (not CSS class). No notification badge on Events. Has duplicate `noEnrollments` div (bug).

### 4.4 `student/events.html` (1240 lines)
- **CSS approach:** Full `<style>` block with CSS variables
- **Main content:** `margin-left: 300px`, glass-card bg `0.9`, hover `translateY(-3px)` (yet another transform value)
- **Sidebar:** ⚠️ Hover uses direct `background: var(--hover-bg)` instead of `::before` pseudo-element (inconsistent with dashboard)
- **Scrollbar:** ⚠️ Missing scrollbar styles on sidebar-nav
- **Logout:** gray-600, door arrow SVG
- **Unique:** Full modal system, event-date gradient badge, event-tag color pills. Largest student file at 1240 lines.

### 4.5 `student/profile.html` (675 lines)
- **CSS approach:** Full `<style>` block with CSS variables
- **Main content:** `margin-left: 300px`, glass-card bg `0.95`, hover `translateY(-2px)`
- **Sidebar:** `::before` hover, scrollbar styles, Events badge "2"
- **Logout:** gray-600, circle arrow SVG
- **Unique:** Profile hero gradient (`#667eea → #764ba2 → #f093fb`), 130px avatar, stat-card, info-card

### 4.6 `student/schedule.html` (860 lines)
- **CSS approach:** Full `<style>` block with CSS variables
- **Main content:** ⚠️ `margin-left: 310px` (inconsistent), glass-card bg `0.95`, ⚠️ **NO hover transform** on glass-card
- **Sidebar:** `::before` hover, scrollbar styles
- **Logout:** ⚠️ `text-red-500`, door arrow SVG
- **Menu divider:** inline style (not CSS class)
- **Events badge:** None
- **Unique:** day-tab with gradient active state, time-badge pulse animation, status-dot blink animation

### 4.7 `student/settings.html` (806 lines)
- **CSS approach:** Full `<style>` block with CSS variables
- **Main content:** `margin-left: 300px`, glass-card bg `0.95`, **NO hover transform** on glass-card
- **Sidebar:** `::before` hover, scrollbar styles, `.menu-divider` CSS class, Events badge "2"
- **Logout:** gray-600, circle arrow SVG
- **Unique:** settings-card, photo-upload-container, toggle-switch, alert slideIn animation

---

## 5. Faculty Portal — Per-File Analysis

Faculty files split into two CSS "generations":

### Generation A — "Full CSS" (6 files)
Files: `dashboard`, `assignments`, `events`, `profile`, `schedule`, `settings`  
Characteristics: Full CSS variable set, `::before` pseudo-element sidebar hover, full scrollbar styling, submenu-item styles

### Generation B — "Compact CSS" (6 files)
Files: `attendance`, `enrollments`, `manage-announcements`, `manage-subjects`, `subjects`, `students_subject_view`  
Characteristics: Minimal CSS vars (no `--bg`, `--text`, `--card-bg`), direct sidebar hover (no `::before`), thumb-only scrollbar, no submenu styles

---

### 5.1 `faculty/dashboard.html` (923 lines) — Gen A
- **CSS vars:** Full set (`--bg`, `--text`, `--card-bg`)
- **Glass-card:** bg `0.95`, hover `translateY(-2px)`
- **Sidebar hover:** `::before` pseudo-element
- **Sidebar header:** ⚠️ "GEC Rajkot" (differs from all other faculty pages which say "Faculty Portal")
- **Logout:** gray-600, `hover:text-red-600`, door arrow SVG (`M17 16l4-4...`)
- **Unique:** ⚠️ Has DUPLICATE `progress-bar` and `@media` blocks (copy-paste artifact). Notification bell dropdown with profile avatar.

### 5.2 `faculty/attendance.html` (~500 lines) — Gen B
- **CSS vars:** Minimal (no `--bg`, `--text`, `--card-bg`)
- **Glass-card:** bg `0.9`, ⚠️ **NO hover effect**
- **Sidebar hover:** Direct `background: var(--hover-bg)` (no `::before`)
- **Scrollbar:** Thumb only, no track
- **Sidebar header:** "Faculty Portal"
- **Logout:** gray-600, `hover:text-red-600`, door arrow SVG

### 5.3 `faculty/assignments.html` (~500 lines) — Gen A
- **CSS vars:** Full set
- **Glass-card:** bg `0.9`, ⚠️ **3D hover** (`translateY(-5px) rotateX(2deg) rotateY(2deg)`) with `transform-style: preserve-3d; perspective: 1000px`
- **Sidebar hover:** `::before` pseudo-element
- **Sidebar header:** "Faculty Portal"
- **Logout:** gray-600, `hover:text-red-600`, door arrow SVG
- **Unique:** Only faculty page (with schedule) that uses 3D card transforms

### 5.4 `faculty/enrollments.html` (~400 lines) — Gen B
- **CSS vars:** Minimal
- **Glass-card:** bg `0.9`, ⚠️ **NO hover effect**
- **Sidebar hover:** Direct background (no `::before`)
- **Scrollbar:** Thumb only
- **Sidebar nav:** ⚠️ **MISSING "Announcements" link** in navigation
- **Unique:** Tab-button styles with underline indicator

### 5.5 `faculty/events.html` (622 lines) — Gen A
- **CSS vars:** Partial (no `--bg`, `--text`)
- **Glass-card:** bg `0.9`, NO `.glass-card` hover defined (but separate `.event-card` has `translateY(-2px)`)
- **Sidebar hover:** `::before` pseudo-element + submenu styles
- **Logout:** gray-600, `hover:text-red-600`, door arrow SVG

### 5.6 `faculty/manage-announcements.html` (~440 lines) — Gen B
- **CSS vars:** Minimal
- **Glass-card:** bg `0.9`, NO hover
- **Sidebar hover:** Direct background (no `::before`)
- **Scrollbar:** Thumb only
- **Unique:** `.stat-card` with `::before` decorative gradient, `.announcement-card` with left border + `translateX(5px)` hover

### 5.7 `faculty/manage-subjects.html` (329 lines) — Gen B
- **CSS vars:** Minimal
- **Glass-card:** bg `0.9`, NO hover
- **Sidebar hover:** Direct background (no `::before`)
- **Sidebar nav:** ⚠️ **MISSING "Announcements" link**
- **Unique:** `.subject-card` with translateY(-2px) hover

### 5.8 `faculty/profile.html` (674 lines) — Gen A
- **CSS vars:** Full set
- **Glass-card:** bg `0.95`, hover `translateY(-2px)`
- **Sidebar hover:** `::before` pseudo-element
- **Unique:** Profile hero gradient matches student/profile.html exactly (`#667eea → #764ba2 → #f093fb`), 130px avatar. Has `background-clip: text` (standard) alongside `-webkit-background-clip`.

### 5.9 `faculty/schedule.html` (994 lines) — Gen A
- **CSS vars:** Full set
- **Glass-card:** bg `0.9`, ⚠️ **3D hover** (`translateY(-5px) rotateX(2deg) rotateY(2deg)`)
- **Sidebar hover:** `::before` pseudo-element + submenu styles
- **Unique:** Longest faculty file. Same 3D card hover as assignments.html.

### 5.10 `faculty/settings.html` (771 lines) — Gen A
- **CSS vars:** Full set
- **Glass-card:** bg `0.95`, ⚠️ **NO hover transform** defined
- **Sidebar hover:** `::before` pseudo-element
- **Unique:** settings-card, photo-upload-container matching student/settings.html. Has `background-clip: text` alongside `-webkit-background-clip`.

### 5.11 `faculty/subjects.html` (918 lines) — Gen B
- **CSS vars:** Minimal
- **Glass-card:** bg `0.9`, NO hover
- **Sidebar hover:** Direct background (no `::before`)
- **Unique:** `.subject-card` hover, `.modal-overlay`/`.modal-content`, `.btn-primary` gradient button, "Enrollment Requests" button with `animate-pulse` badge

### 5.12 `faculty/students_subject_view.html` (760 lines) — Gen B ⚠️ OUTLIER
- **CSS vars:** Minimal + unique additions (`--success`, `--warning`, `--danger`)
- **Glass-card:** bg `0.95`, hover `translateY(-4px)` (strongest simple translateY in codebase)
- **Sidebar:** ❌ **NO SIDEBAR** — full-page standalone layout
- **Font Awesome:** ⚠️ Loads Font Awesome (only portal page to do so, and uses version 6.0.0, not 6.5.1)
- **Unique:** Most animation-heavy file in the project:
  - Enhanced body-level scrollbar styles
  - `.tab-button` with 3px bottom border + gradient `::after` pseudo-element
  - `.student-row` with `translateX(4px)` hover
  - `.subject-card-header` with radial gradient pulse animation
  - `.stat-card` with shimmer animation
  - `.badge-count` with pop animation
  - `.skeleton` loading pattern
  - `.btn-primary`/`.btn-success` with shadow hover
  - `fadeIn` animation
  - `icon-bounce` animation

---

## 6. Auth Pages — Per-File Analysis

Auth pages are the **most consistent group** in the codebase. They share a common design system:

### Shared Auth Design System
- **Layout:** `.auth-wrapper` flex container → `.auth-image-panel` (50%, hidden on mobile) + `.auth-form-panel` (50%)
- **Fonts:** Inter + Playfair Display (Google Fonts)
- **Icons:** Font Awesome 6.5.1
- **CSS vars:** `--primary: #4F46E5`, `--accent: #3B82F6`
- **Decorative:** `.blob-1` and `.blob-2` blurred background circles
- **Animation:** `slideUp` keyframe on `.form-container`
- **Mobile:** `.mobile-brand` bar shown below 1024px, image panel hidden
- **Responsive breakpoint:** `@media (min-width: 1024px)`
- **Form inputs:** 2px border, 12px border-radius, icon left-positioned, focus ring with `box-shadow: 0 0 0 4px rgba(79,70,229,0.1)`
- **Primary button:** Gradient `135deg, --primary → --accent`, `translateY(-1px)` hover, `box-shadow: 0 8px 25px rgba(79,70,229,0.35)`
- **Flash alerts:** Same Tailwind classes for error/success/info

### Student vs Faculty Auth Color Differences
| Dimension | Student Auth | Faculty Auth |
|-----------|-------------|--------------|
| Image panel gradient overlay | `rgba(79,70,229,0.88) → rgba(59,130,246,0.82) → rgba(79,70,229,0.92)` (indigo) | `rgba(30,58,138,0.9) → rgba(55,48,163,0.85) → rgba(79,70,229,0.92)` (navy→indigo) |
| Mobile brand gradient | `var(--primary), var(--accent)` | `#1e3a8a, var(--primary)` |
| Background image | IMG-20230130-WA0007.jpg | WhatsApp-Image-2023-02-02-at-13.06.36.jpg |

### 6.1 `auth/login/student.html` (242 lines)
- Form container max-width: **420px**
- Heading: "Welcome Back"
- Extra: toggle-password, remember-me, register link, back-home link

### 6.2 `auth/login/faculty.html` (245 lines)
- Form container max-width: **420px**
- Heading: "Faculty Portal"
- Extra: Department `<select>` dropdown with custom SVG arrow, `appearance: none`

### 6.3 `auth/login/student-register.html` (318 lines)
- Form container max-width: **480px** (wider for grid layout)
- Responsive grid: `1fr` → `1fr 1fr` at 768px
- Extra: `.form-grid`, `.btn-secondary`, `.checkbox-group`, `.form-footer`
- Mobile brand img: 28px (vs 32px on login pages)

### 6.4 `auth/login/faculty-register.html` (349 lines)
- Form container max-width: **480px**
- Extra: `.section-title` (styled form section dividers with icon), same grid system, same navy gradient on mobile-brand

### 6.5 `auth/login/student-forgot.html` (350 lines)
- Form container max-width: **460px**
- CSS vars add: `--success: #10b981`
- Extra: Step wizard (`.steps-bar`, `.step-dot`, `.step-line`, `.step-label`), OTP inputs (48×56px, 1.3rem font), `.btn-success`, `.btn-outline`, `.reset-step` visibility toggle, `fadeIn` animation
- Form header img: 48px (vs 56px on login/register)
- Form header h1: 1.6rem (vs 1.75rem on login/register)

### 6.6 `auth/login/faculty-forgot.html` (358 lines)
- Nearly identical to student-forgot.html
- Uses navy gradient overlay and mobile-brand gradient (faculty color scheme)
- Step 1 has additional Department `<select>` field
- ⚠️ Department options list is **shorter** than other pages (missing Robotics & Automation, Instrumentation & Control)

### 6.7 `auth/verify-otp.html` (323 lines)
- Form container max-width: **440px**
- Unique elements:
  - `.email-icon-circle` with spinning dashed border animation (`@keyframes spin { to { transform: rotate(360deg); } }`)
  - OTP inputs are **larger**: 52×62px, 1.5rem font (vs 48×56px on forgot pages)
  - `.otp-input.filled` class for visual feedback
  - `.timer-display` with urgent red color state
  - `.msg-box` message system (success/error)
  - `.btn-secondary` outline button (different from register page's `.btn-secondary`)
  - `.btn-primary:disabled` state
- ⚠️ Logo uses hardcoded path `/static/images/logo.png` instead of `{{ url_for('serve_logo') }}` (inconsistent with all other auth pages)

---

## 7. Landing Page (index.html)

**1288 lines** — the largest and most elaborately styled file.

- **CSS approach:** Full `<style>` block (~550 lines of CSS alone), CSS variables, extensive custom classes
- **Fonts:** Inter + Playfair Display + system font stack fallback
- **Icons:** Font Awesome 6.5.1
- **External libs:** Swiper.js (placement section carousel)
- **CSS vars:** `--primary`, `--accent`, `--bg: #ffffff`, `--text: #1f2937`, `--card-bg: #f9fafb`
- **Layout:** Full-page sections, no sidebar
- **Key components:**
  - `.nav-glass` — Sticky glass navbar, transparent on hero → white on scroll
  - `.hero-section` — Full viewport hero with background image, gradient overlay, Playfair Display headings
  - `.hero-portal-card` — Glass-morphism cards on dark hero background
  - `.portal-card` — White cards in portal access section
  - `.feature-card` — Feature highlight cards with hover animations
  - `.dept-card` — Department info cards
  - `.stats-bar` — Full-width gradient stats section
  - `.swiper` — Company logo carousel (placements)
  - `.contact-card` — Contact info cards
  - `.campus-img-card` — Image gallery with scale hover
  - `.site-footer` — Dark footer (`#0f172a`)
  - `.mobile-menu` — Slide-in mobile navigation
- **Unique design patterns:** This page has its own complete design language not shared with any portal page

---

## 8. Cross-Portal Comparison Tables

### 8.1 Student Portal Sidebar & Layout Consistency

| Dimension | dashboard | attendance | enroll | events | profile | schedule | settings |
|-----------|-----------|-----------|--------|--------|---------|----------|----------|
| Has sidebar | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| margin-left | 300px | N/A | ⚠️ **310px** | 300px | 300px | ⚠️ **310px** | 300px |
| glass-card bg alpha | 0.9 | N/A | 0.95 | 0.9 | 0.95 | 0.95 | 0.95 |
| glass-card hover | 3D rotate | N/A | translateY(-2px) | translateY(-3px) | translateY(-2px) | **NONE** | **NONE** |
| Sidebar `::before` hover | ✅ | N/A | ✅ | ❌ | ✅ | ✅ | ✅ |
| Scrollbar styles | ✅ | N/A | ✅ | ❌ | ✅ | ✅ | ✅ |
| Menu divider method | CSS class | N/A | inline style | CSS class | CSS class | inline style | CSS class |
| Logout text color | gray-600 | N/A | ⚠️ red-500 | gray-600 | gray-600 | ⚠️ red-500 | gray-600 |
| Logout icon SVG path | circle arrow | N/A | door arrow | door arrow | circle arrow | door arrow | circle arrow |
| Events badge | ✅ | N/A | ❌ | ✅ | ✅ ("2") | ❌ | ✅ ("2") |
| Tailwind CDN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Inter font | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CSS variables | Full | ❌ | Full | Full | Full | Full | Full |

### 8.2 Faculty Portal Sidebar & Layout Consistency

| Dimension | dashboard | attendance | assignments | enrollments | events | announce | manage-subj | profile | schedule | settings | subjects | students_view |
|-----------|-----------|-----------|------------|------------|--------|----------|-------------|---------|----------|----------|----------|--------------|
| CSS Gen | A | B | A | B | A | B | B | A | A | A | B | B |
| Has sidebar | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| glass-card bg | 0.95 | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 | 0.95 | 0.9 | 0.95 | 0.9 | 0.95 |
| glass-card hover | -2px | **NONE** | **3D** | **NONE** | **NONE** | **NONE** | **NONE** | -2px | **3D** | **NONE** | **NONE** | -4px |
| `::before` hover | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | N/A |
| Full CSS vars | ✅ | ❌ | ✅ | ❌ | Partial | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Scrollbar (full) | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | N/A |
| Sidebar header | ⚠️ GEC Rajkot | Faculty Portal | Faculty Portal | Faculty Portal | Faculty Portal | Faculty Portal | Faculty Portal | Faculty Portal | Faculty Portal | Faculty Portal | Faculty Portal | N/A |
| Announcements nav | ✅ | ✅ | ✅ | ⚠️ **MISSING** | ✅ | ✅ | ⚠️ **MISSING** | ✅ | ✅ | ✅ | ✅ | N/A |
| Font Awesome | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ **YES** |

### 8.3 Card Hover Effect Inventory (All Portal Pages)

| Hover Effect | Files Using It |
|-------------|----------------|
| `translateY(-2px)` | student/enroll, student/profile, faculty/dashboard, faculty/profile |
| `translateY(-3px)` | student/events |
| `translateY(-4px)` | faculty/students_subject_view |
| `translateY(-5px) rotateX(2deg) rotateY(2deg)` (3D) | student/dashboard, faculty/assignments, faculty/schedule |
| **No hover** | student/schedule, student/settings, faculty/attendance, faculty/enrollments, faculty/events*, faculty/manage-announcements, faculty/manage-subjects, faculty/settings, faculty/subjects |

*faculty/events has no `.glass-card` hover but has a separate `.event-card:hover`

### 8.4 Logout Button Variants

| Variant | Color | Icon | Pages |
|---------|-------|------|-------|
| A | gray-600 | circle arrow (`M11 15l-3-3m0 0l3-3...`) | student/dashboard, student/profile, student/settings |
| B | red-500 | door arrow (`M17 16l4-4m0 0l-4-4...`) | student/enroll, student/schedule |
| C | gray-600 | door arrow | student/events, all faculty pages (with `hover:text-red-600`) |

---

## 9. Critical Inconsistencies

### 🔴 Severity: High

1. **`student/attendance.html` is a completely different app**
   - No sidebar, no CSS variables, no Inter font, no glass-morphism, no `<style>` block
   - Uses plain Tailwind utility classes only
   - Looks like a prototype or early-stage page that was never updated to match the design system

2. **`faculty/students_subject_view.html` is a completely different app**
   - No sidebar, loads Font Awesome (unique), has its own animation system
   - Uses Font Awesome 6.0.0 while auth pages use 6.5.1 (version mismatch)
   - Has unique CSS variables (`--success`, `--warning`, `--danger`) not used elsewhere

3. **Faculty sidebar nav is inconsistent**
   - `faculty/enrollments.html` and `faculty/manage-subjects.html` are **missing the "Announcements" link**
   - `faculty/dashboard.html` sidebar says "GEC Rajkot" while all other faculty pages say "Faculty Portal"

4. **`margin-left` inconsistency** 
   - `student/enroll-subjects.html` and `student/schedule.html` use `310px` instead of `300px`
   - This creates a 10px content offset visible when navigating between pages

### 🟡 Severity: Medium

5. **Two CSS "generations" in faculty portal**
   - 6 files use full CSS (Gen A: dashboard, assignments, events, profile, schedule, settings)
   - 6 files use minimal CSS (Gen B: attendance, enrollments, manage-announcements, manage-subjects, subjects, students_subject_view)
   - Sidebar hover behavior, scrollbar styling, and CSS variable completeness differ between generations

6. **Glass-card opacity inconsistency**
   - `0.9` used by: student/dashboard, student/events, faculty/attendance, faculty/assignments, faculty/enrollments, faculty/events, faculty/manage-announcements, faculty/manage-subjects, faculty/schedule, faculty/subjects
   - `0.95` used by: student/enroll, student/profile, student/schedule, student/settings, faculty/dashboard, faculty/profile, faculty/settings, faculty/students_subject_view
   - No clear logic for which value is used

7. **Logout button inconsistency within student portal**
   - 3 variants of logout button (color + icon combinations) across 6 sidebar pages

8. **`auth/verify-otp.html` uses hardcoded logo path**
   - `/static/images/logo.png` instead of `{{ url_for('serve_logo') }}`
   - Will break if the logo serving route changes

9. **`faculty/dashboard.html` has duplicate CSS blocks**
   - `progress-bar` and `@media` blocks appear twice (copy-paste artifact)

### 🟢 Severity: Low

10. **Menu divider implementation varies**
    - Some files use `.menu-divider` CSS class, others use inline `style` attribute
    - Functionally identical but inconsistent implementation

11. **Events notification badge inconsistent**
    - Student portal: badge present on dashboard, events, profile, settings; absent on enroll-subjects, schedule
    - Some badges show "2" (hardcoded), others just show a dot

12. **OTP input sizes differ**
    - Forgot password pages: 48×56px, font-size 1.3rem
    - verify-otp.html: 52×62px, font-size 1.5rem

13. **Faculty forgot password department list incomplete**
    - `faculty-forgot.html` is missing "Robotics & Automation" and "Instrumentation & Control" from its department dropdown

14. **Scrollbar styling varies**
    - Gen A faculty files + most student files: full scrollbar (track + thumb)
    - Gen B faculty files: thumb only, no track styling

---

## 10. Recommendations Summary

| Priority | Action | Impact |
|----------|--------|--------|
| 🔴 Critical | Redesign `student/attendance.html` to match the portal design system (sidebar, glass-cards, CSS vars) | Visual consistency |
| 🔴 Critical | Add sidebar to `faculty/students_subject_view.html` or establish it as an intentional standalone page | Navigation consistency |
| 🔴 Critical | Extract shared CSS into `static/css/portal-base.css` to eliminate per-file duplication | Maintainability |
| 🔴 Critical | Add missing "Announcements" nav link to `faculty/enrollments.html` and `faculty/manage-subjects.html` | Navigation completeness |
| 🟡 Medium | Standardize `margin-left` to `300px` across all sidebar pages | Layout alignment |
| 🟡 Medium | Standardize glass-card opacity to one value (recommend `0.95`) | Visual consistency |
| 🟡 Medium | Standardize card hover effects (recommend `translateY(-2px)` for all) | Animation consistency |
| 🟡 Medium | Standardize logout button (one color + one icon across all pages) | UI consistency |
| 🟡 Medium | Fix `faculty/dashboard.html` sidebar header to say "Faculty Portal" | Branding consistency |
| 🟡 Medium | Update all Gen B faculty files to use `::before` hover and full scrollbar | Interaction consistency |
| 🟡 Medium | Fix `auth/verify-otp.html` to use `{{ url_for('serve_logo') }}` | Route safety |
| 🟡 Medium | Add missing departments to `faculty-forgot.html` dropdown | Data completeness |
| 🟢 Low | Standardize menu dividers to CSS class everywhere | Code consistency |
| 🟢 Low | Standardize OTP input sizes across forgot + verify pages | Visual consistency |
| 🟢 Low | Remove duplicate CSS blocks from `faculty/dashboard.html` | Code cleanliness |
| 🟢 Low | Standardize Font Awesome version (6.5.1) on `faculty/students_subject_view.html` | Dependency alignment |

---

*End of report. Total files analyzed: 27. Total lines of template code: ~14,387.*
