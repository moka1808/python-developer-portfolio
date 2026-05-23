# Modern Python Developer Portfolio

This repository contains production-ready projects demonstrating backend software engineering and data pipeline automation workflows. Both systems are fully functional, modularized, and built locally using industry-standard libraries.

---

## 🚀 Folder 1: task_management_api
A high-performance RESTful API built to handle relational user-task workflows with complete asynchronous database transactions and gatekeeper data validation.

* **Tech Stack:** FastAPI, Pydantic, SQLite, AioSQLite
* **Key Architecture & Features:**
  * **Asynchronous Runtime:** Leverages `async/await` paradigms to process non-blocking database and network operations efficiently.
  * **Data Validation Layer:** Implements strict data schema verification using Pydantic models to catch invalid data formats before reaching storage.
  * **Relational Persistence:** Uses a structured local database using clean entity relationships.
  * **Interactive Docs:** Built-in auto-generation of interactive OpenAPI documentation (accessible via the `/docs` Swagger UI endpoint).

---

## 📊 Folder 2: data_pipeline
An automated ETL (Extract, Transform, Load) data engineering pipeline that programmatically extracts unstructured web matrix fields and processes them into standardized, analytics-ready formats.

* **Tech Stack:** Python Requests, BeautifulSoup4, Pandas
* **Key Architecture & Features:**
  * **Extraction Layer:** Rebuilds programmatic HTML retrieval using custom spoofing headers to smoothly access web elements.
  * **Transformation Layer:** A robust, multi-stage Pandas processing engine that systematically targets missing data fields, executes strict log deduplication, and flushes broken rows.
  * **Mathematical Casting:** Converts unstructured string texts into exact mathematical decimal floats.
  * **Automated Load Layer:** A storage file writer that preserves historical database states by dynamically assigning real-time timestamps (`YYYYMMDD-HHMMSS`) to CSV exports.
