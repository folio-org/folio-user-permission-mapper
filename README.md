# FOLIO User Permission Mapper

`folio-user-permission-mapper` is a CLI tool designed to collect and analyze user permissions in a
FOLIO environment. It integrates with various services to fetch, process, and store permission data
for further analysis.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Configuration](#configuration)
- [Development](#development)
- [License](#license)

---

## Installation

### Prerequisites

- Python 3.12 or higher
- Poetry for dependency management (if installed from source)
  https://python-poetry.org/docs/

### Installation Options

#### Option 1: Install Using `pip` and the Wheel File

You can install the tool directly using `pip` with the provided `.whl` file:

```bash
pip install <.whi-file>
```

This will install the CLI tool globally, and you can run it using the `folio-permission-mapper`
command.

### Prerequisites

- Python 3.12 or higher
- Poetry for dependency management

### Steps

1. Clone the repository:
   ```bash
   git clone git@github.com:folio-org/folio-user-permission-mapper.git
   cd folio-user-permission-mapper
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

---

## Usage

The CLI tool provides a single command to collect and process permissions. Run the following command
to execute the tool:

```bash
poetry run folio-permission-mapper <command>
```

> **_NOTE:_** If it's installed via wheel file:
> ```bash
> folio-permission-mapper <command>
> ```

---

## Commands

### `collect-permissions`

**Description**:

This command will:

1. Fetch permissions defined in the Okapi module descriptors.
2. Load all mutable permissions and their associated users.
3. Enrich the permissions with user data.
4. Save the results to an S3 bucket in JSON format.

**Output**:

- A JSON file named `okapi-permissions.json.gz` is saved to the S3 bucket under the path
  `<tenant_id>/<tenant_id>-okapi-permissions.json.gz`. JSON is archived using gzip for compression.

### `generate-report`

**Description**:

This command will:

1. Fetch file from s3 storage generated using `collect-permissions` command.
2. Generate an Excel file from the JSON data.

**Output**:

- A JSON file named `analysis-result.xlsx` is saved to the S3 bucket under the path
  `<tenant_id>/<tenant_id>-analysis-result.xlsx`.

---

## Configuration

The tool relies on environment variables for configuration. Ensure the following environment
variables are set:

| Env Variable                  | Default Value | Required | Description                                               |
|-------------------------------|---------------|----------|-----------------------------------------------------------|
| AWS_ACCESS_KEY_ID             |               | true     | Your AWS access key                                       |
| AWS_SECRET_ACCESS_KEY         |               | true     | Your AWS secret key                                       |
| AWS_REGION                    | `us-east-1`   | false    | AWS S3 Region                                             |
| AWS_S3_ENDPOINT               |               | false    | Custom AWS S3 Endpoint (if MinIO is used for example)     |
| OKAPI_URL                     |               | true     | Okapi URL                                                 |
| TENANT_ID                     |               | true     | The tenant ID for the FOLIO environment                   |
| ADMIN_USERNAME                |               | true     | The username for the admin user in Okapi                  |
| ADMIN_PASSWORD                |               | true     | The password for the admin user in Okapi                  |
| PERMISSION_IDS_PARTITION_SIZE | 50            | false    | Amount of user permissions pulled by ids at a single call |
| DOTENV                        | .env          | false    | Custom `.env` file                                        |

You can use a `.env` file to manage these variables. For example:

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

OKAPI_URL=http://okapi:9130
TENANT_ID=my-tenant
ADMIN_USERNAME=my-username
ADMIN_PASSWORD=my-password
```

### Development

This command is used to normalize the project (applies import sorting, code formatting, and linting):


```bash
 poetry run isort . && poetry run black . && poetry run flake8 
```
---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
