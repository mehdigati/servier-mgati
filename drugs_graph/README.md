# Drugs Graph Application

## Overview
Python application that processes medical publications data to generate a graph of drug mentions across PubMed articles and clinical trials.

## Requirements
- Python >= 3.12.3
- Poetry for dependency management
- Docker for containerization

## Version
Current version: See [VERSION](VERSION) file

## Setup

### 1. Poetry Installation
```bash
# Install poetry if you haven't already
pip install poetry

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 2. Pre-commit Hooks
We use pre-commit to maintain code quality. Install the hooks:
```bash
# Install pre-commit if you haven't already
pip install pre-commit

# Install the git hooks
pre-commit install

# Run all pre-commit hooks manually (optional)
pre-commit run --all-files
```

Available hooks:
- black (code formatting)
- flake8 (code style)
- isort (import sorting)
- mypy (type checking)
- bandit (security checks)
- trailing-whitespace
- end-of-file-fixer

## Usage

### Data Processing
Files can be directly added to their respective folders for processing:

- Add drug data files to data/drugs/
- Add clinical trials data to data/clinical_trials/
- Add PubMed publications to data/pubmed/

The application will automatically process all files in these directories according to their format.

### Running with Poetry
```bash
# Activate virtual environment
poetry shell

# Set environment variables
cd app

# Generate drug mentions graph
python main.py --action=generate_graph

# Get journal with most drugs
python main.py --action=get_journal_with_most_drugs
```

### Running with Docker
```bash
# Build the image
docker build -t drugs-graph:latest .

# Run the container
docker run -i -t drugs-graph:latest

# Run specific commands
docker run drugs-graph:latest python main.py generate_graph
```

## Testing

### Unit Tests
The project uses Python's unittest framework. Run tests with:
```bash
cd app

# Run all tests
python -m unittest discover tests/unit

# Run specific test files
python -m unittest tests/unit/test_preprocess.py
python -m unittest tests/unit/test_files_processing.py
python -m unittest tests/unit/test_journal_mentions.py
python -m unittest tests/unit/test_json_processing.py
python -m unittest tests/unit/test_transform.py

# Run with coverage report
coverage run -m unittest discover tests/unit
coverage report
coverage html  # Generates HTML report
```

### End-to-End Tests (In Development)
E2E tests are currently under development in the `tests/e2e` directory. They will test:
- Complete data pipeline execution
- Input/output validation
- Error handling scenarios
- Performance benchmarks

To run available E2E tests:
```bash
python -m unittest discover tests/e2e
```

## Project Structure
```
drugs_graph/
├── app/
│   ├── data/                 # Input data files
│   │   ├── clinical_trials/
│   │   ├── drugs/
│   │   └── pubmed/
│   ├── outputs/              # Generated outputs
│   ├── src/                  # Source code
│   │   ├── ad_hoc/          # Ad-hoc analysis
│   │   ├── files_processing/ # File handling
│   │   ├── graph_link/   # Graph generation
│   │   └── data_processing/# Data processing
│   ├── tests/
│   │   ├── e2e/             # End-to-end tests
│   │   └── unit/            # Unit tests
│   └── main.py              # Application entry
├── Dockerfile               # Container definition
├── VERSION                  # Version file
├── poetry.lock             # Lock file
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Development Guidelines

### Version Management
- Version follows semantic versioning (MAJOR.MINOR.PATCH)
- Update VERSION file when making releases
- Tag releases in git matching VERSION file

### Code Style
All code must pass pre-commit hooks:
```bash
# Run hooks manually
pre-commit run --all-files

# Auto-fix some issues
black .
isort .
```

### Testing Requirements
- New features require unit tests
- Maintain >= 80% code coverage
- E2E tests for critical paths
- Run full test suite before PRs

## Troubleshooting

### Common Issues
1. Poetry environment issues:
```bash
# Reset poetry environment
poetry env remove python
poetry install
```

2. Pre-commit hook failures:
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Clean pre-commit cache
pre-commit clean
```

3. Docker build issues:
```bash
# Clean docker cache
docker system prune -a
```

## Contributing
1. Create a feature branch
2. Ensure pre-commit hooks pass
3. Add/update tests
4. Update VERSION file if needed
5. Submit pull request
