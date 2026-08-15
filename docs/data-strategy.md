# BharatShield AI: Data Strategy

This document outlines the ethical collection and curation of regional-language phishing datasets.

## Principles
1. **No Personal Data:** We will not scrape or import real users' private messages.
2. **Provenance Tracking:** Every sample must record its original source, type, and transformation history.
3. **Regional Focus:** Hindi, English, and Hinglish.

## Sourcing Approach
1. **Public Datasets:** Utilizing open-source, permissively licensed datasets for English.
2. **Synthetic Generation:** For Hinglish and Hindi, we may synthetically translate or transliterate verified English phishing templates using LLMs, explicitly labeling them as `synthetic`.
3. **Manual Curation:** A small, high-quality test set of real-world Hindi/Hinglish phishing SMS messages collected voluntarily from team members, stripped of all identifiable info.

## Ethical Usage
No dataset used for training or evaluation will contain PII, API keys, or private communications without explicit consent and anonymization.
