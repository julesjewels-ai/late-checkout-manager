# Late Checkout

A hospitality management platform designed to automate and monetize late checkout requests for hotels and short-term rentals. It allows guests to request extended stay hours via a mobile web interface, automatically calculates dynamic fees based on occupancy and demand, processes payments, and instantly updates housekeeping schedules to ensure smooth turnover.

## Tech Stack

- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL
- **Integrations:** Stripe API, Twilio API

## Features

- Self-service guest portal for requesting checkout extensions
- Dynamic pricing engine based on time and demand
- Real-time integration with Property Management Systems (PMS)
- Automated SMS/Email notifications for housekeeping staff
- Instant payment processing for upsells

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/late-checkout.git
    cd late-checkout
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    uvicorn src.late_checkout.main:app --reload
    ```
