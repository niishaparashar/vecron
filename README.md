# vecron
A Hybrid Opportunity Recommendation System Using Vectorisation &amp; Filtering Techniques
# Vecron – ML-Powered Job Opportunity Aggregation System

Vecron is a machine-learning–powered job opportunity aggregation system designed to collect, clean, structure, and analyze job listings from multiple sources. Instead of functioning as a user-facing recommendation engine (at least for now), Vecron focuses on building a high-quality opportunity dataset using ML-assisted logic for classification, filtering, and scoring.

The long-term vision is to evolve Vecron into a full recommendation platform, but in its current form it acts as an intelligent data pipeline for job opportunity discovery.

---

## Project Motivation

Finding relevant job opportunities across different platforms is time-consuming and inconsistent due to:

* Unstructured job descriptions
* Duplicate listings
* Inconsistent skill and role naming
* No standardized scoring or ranking

Vecron was built to solve these issues by:

* Automatically fetching job listings
* Cleaning and normalizing raw job data
* Applying ML techniques to analyze job relevance
* Storing structured opportunities in a centralized CSV dataset

---

## Core Features

* Job data ingestion from online sources
* Text preprocessing and normalization
* Skill and role extraction from job descriptions
* ML-assisted classification and filtering
* Opportunity scoring and ranking logic
* Structured dataset generation (opportunity.csv)
* Modular pipeline design for future automation

---

## System Architecture

Vecron is organized into modular components:

1. Data Ingestion Layer

   * Responsible for fetching raw job data
   * Supports API-based and scraper-based sources

2. Data Processing Layer

   * Cleans raw text (removes noise, formatting issues)
   * Normalizes role titles and skill keywords
   * Handles duplicate detection and removal

3. ML Layer

   * Uses TF-IDF vectorization for text representation
   * Applies cosine similarity for relevance matching
   * Classifies jobs into categories and domains
   * Computes relevance scores based on skill overlap

4. Storage Layer

   * Stores processed jobs in opportunity.csv
   * Maintains structured fields for downstream use

---

## Machine Learning Approach

Vecron does not currently use a recommendation model. Instead, ML is used for intelligent filtering, classification, and scoring.

### Techniques Used

* TF-IDF (Term Frequency–Inverse Document Frequency)
  Converts job descriptions and skill lists into numerical vectors.

* Cosine Similarity
  Measures similarity between job descriptions and target skill profiles.

* Keyword Weighting
  Assigns higher weights to critical skills and roles.

* Rule-Based Heuristics
  Complements ML with deterministic rules for:

  * Experience level filtering
  * Employment type filtering
  * Location matching

---

## Dataset Structure

The main output of Vecron is a structured dataset stored as:

```
opportunity.csv
```

Each record contains:

* opportunity_id
* company_name
* title
* employment_type
* experience_level
* skills_required
* department
* category
* location
* workplace_type
* posted_on

This dataset is designed to be ML-ready and analytics-friendly.

---

## Workflow

1. Fetch raw job data from selected sources
2. Clean and normalize job text
3. Extract skills and metadata
4. Apply ML-based scoring and classification
5. Remove duplicates
6. Append processed records to opportunity.csv

---

## Automation (Planned)

Vecron is designed to support workflow automation using n8n.

Current status:

* n8n integration is under development
* Initial workflows failed due to node configuration issues
* Manual execution is currently used for data ingestion

Future plan:

* Automate periodic job scraping
* Trigger ML pipelines on new data
* Enable scheduled dataset refresh

---

## Tech Stack

* Python
* Pandas
* NumPy
* Scikit-learn
* TF-IDF
* Cosine Similarity
* CSV-based data pipelines

---

## Installation

```bash
git clone https://github.com/niishaparashar/vecron.git
cd vecron
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

This will:

* Fetch job data
* Process and score listings
* Update opportunity.csv

---

## Project Status

Active development.

Planned enhancements:

* Robust n8n automation
* Collaborative filtering
* User profile modeling
* API layer for external integration

---

## Author

Nisha Parashar

---

## License

This project is intended for educational and portfolio purposes.

