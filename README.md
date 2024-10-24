# Servier - Data Engineering Technical test - Mehdi GATI

## Overview
This repository contains a data engineering solution for analyzing drug mentions across scientific publications, including PubMed articles and clinical trials. The project processes multiple data sources to generate a comprehensive graph showing relationships between drugs, publications, and journals.

## Repository Structure
```
.
├── README.md                 # This file
├── .github/                  # GitHub Actions workflows
│   └── workflows/
│       ├── build-push.yml   # Build and push Docker image
│       └── deploy-dag.yml   # Deploy DAG to Cloud Composer
├── dags/                     # Airflow DAG definitions
│   └── dag_servier_drug_graph.py
├── drugs_graph/             # Main application package
│   ├── app/                 # Application source code
│   ├── Dockerfile          # Container definition
│   ├── poetry.lock        # Dependencies lock file
│   └── pyproject.toml     # Project configuration
└── sql/                     # SQL analysis queries
    ├── sales_by_day.sql
    └── sales_by_product_type.sql
```

## CI/CD Pipeline
The project uses GitHub Actions for automated CI/CD pipelines, integrating with Google Cloud Platform services.

GCP Workload Identity Federation is assumed to be already configured in the GCP projects
GitHub repository secrets are properly set up with the following variables:
```
GCP_PROJECT_ID               # Google Cloud Project ID
WORKLOAD_IDENTITY_PROVIDER   # GCP Workload Identity Provider
SERVICE_ACCOUNT_EMAIL        # GCP Service Account Email
COMPOSER_DAG_BUCKET         # Cloud Composer DAG Bucket
```

1. Build and Push to Artifact Registry
Trigger: Push to main branch (excluding .md files) or manual trigger

2. Deploy DAG to Cloud Composer
Trigger: Push to main branch (dags/** files) or manual trigger

## Production Deployment Strategy

### Environment Management
- Segregated environment configurations:
  - `.env_dev` for development
  - `.env_stg` for staging
  - `.env_prd` for production
- Each environment has isolated resources and configurations

### CI/CD Pipeline
Deployment strategies:

#### 1. Three-Branch Strategy
```
develop  → Development Environment
staging  → Staging Environment
prod     → Production Environment
```
- Merge Requests trigger deployments to respective environments
- Automated testing at each stage
- Manual validation gates between environments

#### 2. Single-Branch Strategy
```
main branch:
├── Merge Request → Dev Environment
├── Merge        → Staging Environment
└── Tag          → Production Environment
```
- Tags follow Semantic Versioning (MAJOR.MINOR.PATCH)
- Automated regression testing
- Security scanning at each stage

### Quality Assurance
- Automated test suites:
  - Unit tests
  - Integration tests
  - End-to-end tests
- Security scanning:
  - Dependency vulnerabilities
  - Code quality metrics
  - Container scanning
- Performance testing at scale

## Scaling for Big Data

### Approach 1: Distributed Computing with PySpark
Suitable for computation-intensive processing:

- Benefits:
  - Distributed data processing
  - Memory-efficient operations
  - Native scalability

- Implementation:
  - Convert pandas operations to PySpark
  - Deploy on high-capacity virtual machines
  - Configure resource allocation
  - Implement partitioning strategy

### Approach 2: Cloud-Native ETL with BigQuery
Ideal for large-scale data warehousing:

- Architecture:
  ```
  Google Cloud Storage
  └── Raw Data
      ├── Input Processing (BigQuery)
      ├── Transformation (dbt)
      └── Output Storage (GCS)
  ```

- Features:
  - Serverless processing
  - Cost-effective storage
  - Automated scaling
  - Built-in monitoring

### Quality Assurance for Big Data
- Extended test coverage:
  - Data quality validation
  - Schema evolution testing
  - Performance benchmarking
  - Scalability testing

- Monitoring:
  - Processing metrics
  - Resource utilization
  - Error rates
  - Data quality metrics

### Infrastructure Considerations
- Resource Management:
  - Dynamic scaling
  - Resource quotas
  - Cost optimization
  - Performance monitoring

- Data Lifecycle:
  - Retention policies
  - Archival strategy
  - Backup procedures
  - Disaster recovery

## Data Pipeline
See [drugs_graph/README.md](drugs_graph/README.md)
