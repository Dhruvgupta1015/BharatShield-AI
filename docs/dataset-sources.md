# BharatShield AI: Dataset Sources

This document strictly tracks the provenance and usage licenses of the data ingested by BharatShield AI. Unverified or privately scraped data is strictly prohibited.

## 1. UCI SMS Spam Collection
*   **Source Name:** UCI Machine Learning Repository
*   **Source URL:** [archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection)
*   **Status:** APPROVED AND INGESTED
*   **Dataset Type:** Public Academic
*   **Language Scope:** Primarily English
*   **Label Semantics:** Labeled strictly as `ham` (legitimate) and `spam` (unsolicited). 
*   **MVP Caveat:** For BharatShield AI `dataset_v1`, `spam` is mapped as a pragmatic proxy to `phishing`. This is a known semantic limitation.

## 2. Regional Data Sources (Hindi/Hinglish)
*   **Status:** GAP IDENTIFIED
*   **Notes:** While some GitHub repositories and Kaggle collections (e.g. "India Spam SMS Classification") exist, they often require authenticated access, lack clear data provenance, or contain crowdsourced private messages without explicit consent. In adherence to our strict ethical data collection rules, no Hindi/Hinglish datasets have been ingested in `dataset_v1`. We will rely entirely on our Deterministic Engine's hardcoded rules for regional detection until verified, clean data is acquired.
