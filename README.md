# Economic Indicators World View

An automated, modular Python analytics engine designed to collect, transform, and visualize global macroeconomic indicators across the US and Europe. Built to bridge complex data engineering with dynamic financial analysis, this tool standardizes multi-source data to rapidly test market hypotheses and identify statistical outliers.

### Architecture Overview

* **Part 1: Core Library & Modules**
  * Houses modular Python functions and base configurations for streamlined data processing and custom calculations.
* **Part 2: Data Ingestion & Transformation**
  * Programmatically pulls 95% of live data from multiple financial API vendors (including FRED and financial modeling endpoints).
  * Integrates a targeted manual Excel reference file to map specific auxiliary data points.
  * Automatically transforms raw series into percentage changes and year-over-year (YoY) metrics, consolidating everything into a unified, month-indexed master Df per region (USA and Europe and UK).
* **Part 3: Advanced Analytics & Visualization**
  * Calculates market breadth, yield curves.
  * Employs standard deviation calculations to automatically flag and display market outliers.
  * Renders interactive, multi-layered dual-axis charts and custom data bars using Plotly.

### Tech Stack
* **Language:** Python
* **Data Manipulation:** pandas, NumPy, SciPy, scikit-learn
* **Visualization:** Plotly, Matplotlib, Seaborn
* **APIs & Data Sources:** FRED API (primary 95% data stream), Yahoo Finance, custom endpoints, manual Excel reference mapping
