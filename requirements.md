# Product Requirements Document: TunisHome Pro

**Version:** 1.0
**Status:** In Development
**Date:** November 2025

---

## 1. Executive Summary
**TunisHome Pro** is a high-performance real estate intelligence platform designed for the Tunisian market. It aggregates fragmented listings from legacy platforms (starting with *Tunisie Annonce*), normalizes the data, and uses Artificial Intelligence to provide "Investment-Grade" insights.

Unlike existing competitors that function merely as digital bulletin boards, TunisHome Pro acts as an **analytical engine**, offering features like price prediction, AI-driven renovation grading, and semantic search.

**Core Value Prop:** "The Bloomberg Terminal for Tunisian Real Estate."

---

## 2. Target Audience
1.  **The Investor/Expat:** Wants to see market trends, heatmaps, and ROI potential without sifting through spam.
2.  **The High-End Renter:** Wants a modern, map-based interface to find luxury properties quickly.
3.  **The Recruiter/Client (Meta-Audience):** The platform serves as a portfolio piece demonstrating Senior-level Full Stack & AI Engineering capabilities.

---

## 3. System Architecture

### 3.1 High-Level Overview
*   **Frontend (The "Showroom"):** A Next.js 14 application hosted on Vercel. It is responsible for the UI, Map visualization, and on-demand AI interactions (User Uploads).
*   **Backend (The "Data Factory"):** A local Python processing unit. It runs offline/scheduled tasks to scrape data, run local AI models (Ollama), and populate the database.
*   **Database:** Supabase (PostgreSQL) storing listings, images, and vector embeddings.
*   **AI Services:**
    *   **Local:** Ollama (Llama 3.2 Vision) for batch processing scraped images.
    *   **Cloud:** Google Gemini 1.5 Flash (via Vercel Actions) for real-time user uploads.

---

## 4. Functional Requirements

### 4.1 Data Acquisition (The Scraper)
*   **FR-01:** System must scrape `Tunisie Annonce` (Real Estate / Rent & Sale sections).
*   **FR-02:** System must handle legacy character encoding (`Windows-1252`) to ensure Arabic/French text is legible.
*   **FR-03:** System must normalize listing data:
    *   Extract "S+2", "S+3" -> `rooms: 2`, `rooms: 3`.
    *   Extract Price -> Integer (Remove "DT", handle "Prix sur demande").
    *   Geocode "Location Text" (e.g., "L'Aouina") -> Latitude/Longitude coordinates.

### 4.2 AI Intelligence Layer
*   **FR-04 (Computer Vision):** System must analyze property images to output a "Renovation Score" (0-10) and tags (e.g., "Marble," "Unfinished," "Old Kitchen").
*   **FR-05 (Price Prediction):** System must calculate a "Fair Market Value" based on the average price/m² of the neighborhood and flag listings as "Underpriced" (Green Deal) or "Overpriced" (Red Warning).
*   **FR-06 (Semantic Search):** Users must be able to search via natural language (e.g., *"Modern apartment near a gym in a quiet area"*) using Vector Embeddings.
*   **FR-07 (Smart Auto-Fill):** Users uploading a photo of their own property will have the form fields (Renovation status, flooring type, description) auto-filled by Gemini Flash.

### 4.3 User Interface (Frontend)
*   **FR-08 (Map Interface):** A split-screen view.
    *   **Left:** Scrollable list of property cards (Bento-grid style).
    *   **Right:** Interactive Mapbox GL map with clustering.
*   **FR-09 (Visualization):** The map must support a "Heatmap Mode" visualizing price density (3D extrusion of expensive neighborhoods).
*   **FR-10 (Performance):** The site must use smooth scrolling (`Lenis`) and optimistic UI updates for a "Premium App" feel.

---

## 5. Technical Stack

| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Frontend Framework** | Next.js 14 (App Router) | Standard for modern web; server-side rendering for SEO. |
| **Styling** | plain CSS + Framer Motion | unique UI development + high-end animations. |
| **Maps** | Mapbox GL JS | Best-in-class performance for dark mode & 3D visualization. |
| **Database** | Supabase (Postgres) | Free tier includes PostGIS (Maps) and pgvector (AI). |
| **Scraper** | Python (Requests/BS4) | Robust, handles encoding issues well. |
| **Local AI** | Ollama (Llama 3.2 Vision) | Free, unlimited batch processing on local GPU. |
| **Cloud AI** | Google Gemini 1.5 Flash | Fast, free tier for real-time user interaction. |

---

## 6. Data Models (Core Schema)

**Property Entity:**
*   `id`: UUID
*   `title`: String
*   `price`: Float
*   `location_coords`: Lat/Lng
*   `renovation_score`: Float (AI Generated)
*   `embedding`: Vector (768 dimensions)
*   `source`: "Tunisie Annonce" | "User Upload"
*   `status`: Active | Sold

---

## 7. Implementation Roadmap (The "Sprint")

### Phase 1: The Skeleton (Hours 0-24)
*   Set up Supabase (Enable PostGIS & Vector).
*   Build Python Scraper (Tunisie Annonce).
*   **Milestone:** 50 clean rows in the database with Lat/Lng coordinates.

### Phase 2: The Visuals (Hours 24-48)
*   Initialize Next.js.
*   Integrate Mapbox.
*   Render the 50 rows as pins on the map.
*   **Milestone:** A working map displaying real data.

### Phase 3: The Intelligence (Hours 48-72)
*   Connect Python scraper to Ollama (Local AI).
*   Process images to get "Renovation Scores."
*   Update database with AI tags.
*   **Milestone:** UI displays "AI Analysis" badges on listings.

### Phase 4: The Interaction (Final Polish)
*   Build the "Add Listing" button with Gemini Flash.
*   Implement Semantic Search (Vector query).
*   Deploy to Vercel.

---

## 8. Success Metrics
*   **Latency:** Map loads 100+ pins in under 1.5 seconds.
*   **Accuracy:** Geocoding places the pin in the correct neighborhood 90% of the time.
*   **AI Value:** The Price Prediction successfully identifies outliers (obviously cheap vs expensive listings).