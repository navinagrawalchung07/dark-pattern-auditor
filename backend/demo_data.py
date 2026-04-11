"""
Demo data — instant mock audit result for UI demos.
"""

DEMO_FINDINGS = [
    {
        "pattern_type": "roach_motel",
        "severity": "high",
        "description": "Amazon Prime makes cancellation deliberately multi-step and hard to find. Users must navigate through at least 6 pages and are presented with multiple 'keep my benefits' screens before cancellation is confirmed.",
        "quoted_ui_text": "Keep my benefits — Your Prime membership helps you get more done. Are you sure you want to cancel?",
        "statute_name": "FTC Act § 5(a) — Unfair or Deceptive Acts or Practices",
        "statute_excerpt": "Unfair methods of competition in or affecting commerce, and unfair or deceptive acts or practices in or affecting commerce, are hereby declared unlawful.",
        "statutory_url": "https://www.ftc.gov/legal-library/browse/statutes/federal-trade-commission-act",
        "step_name": "cancellation_flow",
        "screenshot_b64": None,
    },
    {
        "pattern_type": "confirmshaming",
        "severity": "medium",
        "description": "The Prime upsell modal uses guilt-tripping language on the decline button, framing non-subscription as a negative personal choice rather than a neutral option.",
        "quoted_ui_text": "No thanks, I don't want fast, free delivery",
        "statute_name": "EU UCPD Annex I Item 6 — Aggressive Commercial Practices",
        "statute_excerpt": "Using language or behaviour that implies the consumer has already purchased or agreed to purchase a product or service, when they have not.",
        "statutory_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029",
        "step_name": "signup_flow",
        "screenshot_b64": None,
    },
    {
        "pattern_type": "forced_continuity",
        "severity": "high",
        "description": "Amazon Prime free trial automatically converts to a paid subscription without a clear pre-conversion warning. The transition date is disclosed only in fine print during signup, not via a reminder email before billing.",
        "quoted_ui_text": "Start your 30-day free trial. After trial, $14.99/month. Cancel anytime.",
        "statute_name": "FTC Negative Option Rule (16 CFR Part 425)",
        "statute_excerpt": "A seller must clearly and conspicuously disclose all material terms of the negative option feature before obtaining the consumer's billing information.",
        "statutory_url": "https://www.ftc.gov/legal-library/browse/rules/negative-option-rule",
        "step_name": "signup_flow",
        "screenshot_b64": None,
    },
    {
        "pattern_type": "hidden_costs",
        "severity": "medium",
        "description": "Import fees and shipping surcharges for third-party marketplace items are not shown on product pages or in the cart — they appear only at the final checkout step after the user has already committed to a purchase.",
        "quoted_ui_text": "Import fees deposit: $12.49 — This amount may change based on the selected shipping option and quantity.",
        "statute_name": "FTC Enforcement Policy Statement on Deceptively Formatted Advertising",
        "statute_excerpt": "Advertisers must disclose all material conditions of an offer before consumers agree to purchase.",
        "statutory_url": "https://www.ftc.gov/system/files/documents/public_statements/896923/151222deceptiveenforcement.pdf",
        "step_name": "homepage",
        "screenshot_b64": None,
    },
    {
        "pattern_type": "misdirection",
        "severity": "low",
        "description": "The cookie consent banner uses a large, prominent 'Accept All' button in brand orange while the 'Manage Preferences' option is rendered in low-contrast grey text, steering users toward maximum data collection.",
        "quoted_ui_text": "Accept All Cookies — Manage Preferences",
        "statute_name": "EU ePrivacy Directive (2002/58/EC) Art. 5(3)",
        "statute_excerpt": "Member States shall ensure that the use of electronic communications networks to store information or to gain access to information stored in the terminal equipment of a subscriber or user is only allowed on condition that the subscriber or user concerned is provided with clear and comprehensive information.",
        "statutory_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32002L0058",
        "step_name": "cookie_consent",
        "screenshot_b64": None,
    },
]

DEMO_PRECEDENTS = [
    {
        "pattern_type": "roach_motel",
        "cases": [
            {
                "case_name": "FTC v. Amazon.com, Inc.",
                "company": "Amazon",
                "year": 2023,
                "outcome": "FTC filed suit alleging Amazon enrolled consumers in Prime without consent and made cancellation intentionally difficult. Amazon agreed to a $25 million settlement and was required to simplify the cancellation process.",
                "source_url": "https://www.ftc.gov/news-events/news/press-releases/2023/06/ftc-takes-action-against-amazon-enrolling-consumers-amazon-prime-without-their-consent-making-it",
            },
            {
                "case_name": "European Commission v. Amazon (DSA Compliance Action)",
                "company": "Amazon",
                "year": 2024,
                "outcome": "European Commission opened formal proceedings under the Digital Services Act citing dark patterns including difficult subscription cancellation flows and asymmetric UI design.",
                "source_url": "https://ec.europa.eu/commission/presscorner/detail/en/ip_24_1138",
            },
        ],
    },
    {
        "pattern_type": "confirmshaming",
        "cases": [
            {
                "case_name": "Norwegian Consumer Authority v. Booking.com",
                "company": "Booking.com",
                "year": 2022,
                "outcome": "Norwegian Consumer Authority (Forbrukertilsynet) found Booking.com used confirmshaming and urgency dark patterns. Company ordered to remove guilt-tripping decline language under the EU UCPD.",
                "source_url": "https://www.forbrukertilsynet.no/english/booking-com-must-end-dark-patterns",
            },
            {
                "case_name": "FTC Workshop: Bringing Dark Patterns to Light — Confirmshaming Case Studies",
                "company": "Various",
                "year": 2021,
                "outcome": "FTC documented confirmshaming as a deceptive practice across e-commerce sectors in its dark patterns report, signalling enforcement intent under Section 5 of the FTC Act.",
                "source_url": "https://www.ftc.gov/reports/dark-patterns-report",
            },
        ],
    },
    {
        "pattern_type": "forced_continuity",
        "cases": [
            {
                "case_name": "FTC v. ABCMouse.com (Age of Learning)",
                "company": "Age of Learning",
                "year": 2020,
                "outcome": "FTC charged ABCMouse with making it extremely difficult to cancel subscriptions and failing to disclose automatic renewal clearly. $10 million settlement required, plus mandatory easy cancellation mechanism.",
                "source_url": "https://www.ftc.gov/news-events/news/press-releases/2020/09/ftc-returns-money-consumers-who-signed-abcmouse-subscriptions-they-couldnt-easily-cancel",
            },
            {
                "case_name": "FTC v. Vonage Holdings Corp.",
                "company": "Vonage",
                "year": 2022,
                "outcome": "FTC alleged Vonage trapped customers in subscriptions with hidden cancellation fees and an intentionally burdensome cancellation process. $100 million redress settlement.",
                "source_url": "https://www.ftc.gov/news-events/news/press-releases/2022/11/ftc-action-against-vonage-results-100-million-back-consumers-trapped-illegal-dark-patterns-junk-fees",
            },
        ],
    },
    {
        "pattern_type": "hidden_costs",
        "cases": [
            {
                "case_name": "FTC v. Jerk.com / Drip Pricing Sweep",
                "company": "Multiple retailers",
                "year": 2023,
                "outcome": "FTC sweep against drip pricing — undisclosed fees added at checkout. Multiple companies received warning letters and consent orders under FTC Act § 5.",
                "source_url": "https://www.ftc.gov/news-events/news/press-releases/2023/10/ftc-sends-warning-letters-companies-about-fake-reviews-inflated-prices",
            },
            {
                "case_name": "CMA v. Viagogo",
                "company": "Viagogo",
                "year": 2019,
                "outcome": "UK Competition and Markets Authority found Viagogo hid fees until final checkout step, inflating prices by up to 27%. Company required to show all-in prices upfront or face contempt proceedings.",
                "source_url": "https://www.gov.uk/government/news/viagogo-ordered-to-clean-up-its-act",
            },
        ],
    },
    {
        "pattern_type": "misdirection",
        "cases": [
            {
                "case_name": "CNIL v. Google LLC (Cookie Consent)",
                "company": "Google",
                "year": 2022,
                "outcome": "French DPA fined Google €150 million for making cookie refusal harder than acceptance — prominent 'Accept All' button vs. multi-step refusal. Found to violate ePrivacy Directive and GDPR.",
                "source_url": "https://www.cnil.fr/en/cookies-google-and-facebook-sanctioned",
            },
            {
                "case_name": "CNIL v. Facebook / Meta Platforms",
                "company": "Meta",
                "year": 2022,
                "outcome": "Meta fined €60 million by CNIL for asymmetric cookie consent UI where accepting was one click but refusing required multiple steps — a textbook misdirection dark pattern.",
                "source_url": "https://www.cnil.fr/en/cookies-google-and-facebook-sanctioned",
            },
        ],
    },
]
