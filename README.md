# FOLIO User Permission Mapper

`folio-user-permission-mapper` is a CLI tool designed to collect and analyze user permissions in a
FOLIO environment. It integrates with various services to fetch, process, and store permission data
for further analysis.

# Table of Contents

<!-- TOC -->
* [FOLIO User Permission Mapper](#folio-user-permission-mapper)
* [Table of Contents](#table-of-contents)
    * [Script Migration Order](#script-migration-order)
* [Installation](#installation)
  * [Prerequisites](#prerequisites)
  * [Installation Options](#installation-options)
    * [Option 1: Install Using `pip` and the Wheel File](#option-1-install-using-pip-and-the-wheel-file)
  * [Prerequisites](#prerequisites-1)
  * [Steps](#steps)
* [Usage](#usage)
  * [Commands](#commands)
    * [`collect-permissions`](#collect-permissions)
    * [`collect-capabilities`](#collect-capabilities)
    * [`generate-report`](#generate-report)
    * [`run-eureka-migration`](#run-eureka-migration)
    * [`generate-migration-report`](#generate-migration-report)
    * [`analyze-hash-roles`](#analyze-hash-roles)
    * [`cleanup-hash-roles`](#cleanup-hash-roles)
    * [`generate-cleanup-report`](#generate-cleanup-report)
    * [`download-json`](#download-json)
    * [`explain-permissions`](#explain-permissions)
  * [Development Tips](#development-tips)
    * [General environment variables](#general-environment-variables)
    * [Environment Variables (S3 Storage)](#environment-variables-s3-storage)
    * [Environment Variables (Local Storage)](#environment-variables-local-storage)
    * [Pre-Commit Command](#pre-commit-command)
  * [License](#license)
<!-- TOC -->

---

### Script Migration Order

1. **Collect Permissions**</br>
   Use the `collect-permissions` command to gather permissions from an Okapi-based deployment.
2. **Collect Capabilities**</br>
   Use the `collect-capabilities` command to gather capabilities from Eureka-based deployment.
3. **Generate Report**</br>
   Use the `generate-report` command to analyze the collected permissions and capabilities.
4. **Run Eureka Migration**</br>
   Use the `run-eureka-migration` command to create roles and assign capabilities/capability-sets/users based on the generated roles.
5. **Generate Migration Report**</br>
   Use the `generate-migration-report` to generate a report of the Eureka migration process.
6. **Analyze Hash Roles**</br>
   Use the `analyze-hash-roles` command to analyze roles and prepare for cleanup.
7. **Cleanup Hash Roles**</br>
   Use the `cleanup-hash-roles` command to remove duplicated relations and clean up hash roles.
8. **Generate Cleanup Report**</br>
   Use the `generate-cleanup-report` to generate a report of the Eureka Hash-Role Cleanup process.

# Installation

## Prerequisites

- Python 3.12 or higher
- Poetry for dependency management (if installed from source)
  https://python-poetry.org/docs/

## Installation Options

### Option 1: Install Using `pip` and the Wheel File

You can install the tool directly using `pip` with the provided `.whl` file:

```bash
pip install <.whi-file>
```

This will install the CLI tool globally, and you can run it using the `folio-permission-mapper`
command.

## Prerequisites

- Python 3.12 or higher
- Poetry for dependency management

## Steps

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

# Usage

The CLI tool provides a single command to collect and process permissions. Run the following command
to execute the tool:

```bash
poetry run folio-permission-migration-cli <command>
```

> **_NOTE:_** If it's installed via wheel file:
> ```bash
> folio-permission-migration-cli <command>
> ```

---

## Commands

### `collect-permissions`

The command will do the following actions:

- Collect the following data from Okapi-based deployment:
    - module-descriptors from `okapi`
    - permission sets from `mod-permissions`
    - user permissions relations from `mod-permissions`
- Save the result as a gzipped JSON file to the configured storage (S3 or local).

**Requires:**
- Access to the Okapi-based environment.
- User credentials with read access to the `mod-permissions` and `okapi` modules.
- Access to the AWS S3 bucket or local storage where the `okapi-permissions` load result will be stored.

**Output:**
- `<tenant_id>/<tenant_id>-okapi-permissions-<timestamp>.json.gz`

**Environment Variables:**

| Env Variable                  | Default Value         | Required | Description                                               |
|:------------------------------|:----------------------|:---------|:----------------------------------------------------------|
| OKAPI_URL                     | http://localhost:9130 | true     | Okapi URL                                                 |
| TENANT_ID                     |                       | true     | The tenant ID for the FOLIO environment                   |
| OKAPI_ADMIN_USERNAME          |                       | true     | The username for the admin user in Okapi                  |
| OKAPI_ADMIN_PASSWORD          |                       | true     | The password for the admin user in Okapi                  |
| PERMISSION_IDS_PARTITION_SIZE | 50                    | true     | The max number of permissions provided in any match query |

---

### `collect-capabilities`

The command will do the following actions:

- Collect the following data from Eureka-based deployment:
    - capabilities
    - capability sets
    - roles
    - user roles
    - role capabilities relations
    - role capability-set relations
    - user capability relations
    - role capability-set relations
- Save them as a gzipped JSON file to the configured storage.

**Requires:**
- Access to the Eureka-based environment.
- User credentials with read access to the `mod-roles-keycloak` module.
- Access to the AWS S3 bucket or local storage where the `eureka-capabilities` load result will be stored.

**Output:**
- `<tenant_id>/<tenant_id>-eureka-capabilities-<timestamp>.json.gz`

**Environment Variables:**

| Env Variable          | Default Value         | Required | Description                                            |
|:----------------------|:----------------------|:---------|:-------------------------------------------------------|
| EUREKA_URL            | http://localhost:8000 | true     | Kong Gateway URL                                       |
| TENANT_ID             |                       | true     | The tenant ID for the FOLIO environment                |
| EUREKA_ADMIN_USERNAME |                       | true     | The username for the admin user in Okapi               |
| EUREKA_ADMIN_PASSWORD |                       | true     | The password for the admin user in Okapi               |

---

### `generate-report`

The command will do the following actions:

- Load latest `okapi-permissions-<timestamp>.json.gz` and _(optionally)_ latest
  `eureka-capabilities-<timestamp>.json.gz` from storage.
- Analyze and combine the data to provide report and data for eureka migration.
- Generate both an Excel report and a gzipped JSON analysis result.
- Store generated files in the configured storage (s3, local).

**Requires:**
- Access to the AWS S3 bucket or local storage where `okapi-permissions-<timestamp>.json.gz` is stored.
- The `collect-permissions` and (_optionally_) `collect-capabilities` commands must be run before this command.

**Output:**
- `<tenant_id>/<tenant_id>-okapi-analysis-result-<strategy>-<timestamp>.xlsx`
- `<tenant_id>/<tenant_id>-eureka-migration-data-<strategy>-<timestamp>.json.gz`

**Environment Variables:**

| Env Variable                   | Default Value | Required | Description                                                                                                                                 |
|:-------------------------------|:--------------|:---------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| TENANT_ID                      |               | true     | The tenant ID for the FOLIO environment                                                                                                     |
| SYSTEM_GENERATED_PERM_MAPPINGS |               | false    | Comma-separated list of system-generated permission mappings to highlight in analysis (e.g., `folio_admin:AdminRole`)                       |
| REF_CAPABILITIES_FILE_KEY      |               | false    | File key in storage that can be used as reference for capabilities (Recommended to pull this data for tenant with all applications enabled) |
| EUREKA_ROLE_LOAD_STRATEGY      | distributed   | true     | Approach how roles must be generated (one of: distributed, consolidated)                                                                    |

---

### `run-eureka-migration`

The command will do the following actions:

- Load latest `<tenant_id>-eureka-migration-data-<strategy>-<timestamp>.json.gz` and from storage.
- Create roles (values specified in `SYSTEM_GENERATED_PERM_MAPPINGS` will be skipped)</br>
  _If a role exists, it will be skipped (skipped operations will be visible in error report)._
- Assign capabilities and capability-sets to a role</br>
  _All existing relations will be skipped (skipped operations will be visible in error report)._
- Assign users to a role
- All users, that had roles, defined in `SYSTEM_GENERATED_PERM_MAPPINGS`, will be assigned to the role with the same
  name as the role.</br>
  _If a user already has a role, it will be skipped (skipped operations will be visible in error report)._
- Save a report with performed operations into storage (s3, local).

**Requires:**
- The `generate-report`command must be run before this command.
- Access to the AWS S3 bucket or local storage where `analysis-result.json.gz` is stored.

**Output:**
- new roles
- new user-role relations
- new role-capability relations
- new role capability-set relations
- `<tenant_id>/<tenant_id>-eureka-migration-report-<strategy>-<timestamp>.json.gz`

**Environment Variables:**

| Env Variable              | Default Value         | Required | Description                                                              |
|:--------------------------|:----------------------|:---------|:-------------------------------------------------------------------------|
| EUREKA_URL                | http://localhost:8000 | true     | Kong Gateway URL                                                         |
| TENANT_ID                 |                       | true     | The tenant ID for the FOLIO environment                                  |
| EUREKA_ADMIN_USERNAME     |                       | true     | The username for the admin user in Eureka                                |
| EUREKA_ADMIN_PASSWORD     |                       | true     | The password for the admin user in Eureka                                |
| EUREKA_ROLE_LOAD_STRATEGY | distributed           | true     | Approach how roles must be generated (one of: distributed, consolidated) |

---

### `generate-migration-report`

The command will do the following actions:

- Load the latest migration result file (`migration-report-<strategy>-<timestamp>.json.gz`) from storage.
- Parse the migration report data and generate a comprehensive Excel report.
- Store the generated Excel report in the configured storage (S3 or local).

**Requires:**
- The `run-eureka-migration` command must be run before this command.
- Access to the AWS S3 bucket or local storage where the migration report JSON file is stored.

**Output:**
- `<tenant_id>/<tenant_id>-migration-report-<strategy>-<timestamp>.xlsx`

**Environment Variables:**

| Env Variable                   | Default Value | Required | Description                                                                                                                                                    |
|:-------------------------------|:--------------|:---------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TENANT_ID                      |               | true     | The tenant ID for the FOLIO environment                                                                                                                        |
| EUREKA_ROLE_LOAD_STRATEGY      | distributed   | true     | Approach how roles were generated (one of: distributed, consolidated)                                                                                          |
| SKIP_USERS_WITH_TOO_MANY_ROLES | true          | false    | Defines if a users with too many roles should be skipped                                                                                                       |
| MAX_JWT_LENGTH                 | 4000          | false    | To validate maximum amount of roles, script tries to generate a keycloak-like JWT token to validate it's length and compare it with current env variable value |

---

### `analyze-hash-roles`

The command will do the following actions:

- (_if it wasn't executed before_) Collect the following data from Eureka-based deployment:
    - capabilities
    - capability sets
    - roles
    - user roles
    - role capabilities relations
    - role capability-set relations
    - user capability relations
    - role capability-set relations
- Save them as a gzipped JSON file to the configured storage.
- Analyze and combine the data to provide report and data for a hash-roles cleanup process.
- Generate both an Excel report and a gzipped JSON analysis result.
- Store generated files in the configured storage (s3, local).

**Requires:**
- The `run-eureka-migration` command must be run before this command.

**Output:**
- `<tenant_id>/<tenant_id>-hash-roles-analysis-result-<strategy>-<timestamp>.xlsx`
- `<tenant_id>/<tenant_id>-hash-roles-cleanup-data-<strategy>-<timestamp>.json.gz`

**Environment Variables:**

| Env Variable              | Default Value         | Required | Description                                                           |
|:--------------------------|:----------------------|:---------|:----------------------------------------------------------------------|
| TENANT_ID                 |                       | true     | The tenant ID for the FOLIO environment                               |
| EUREKA_URL                | http://localhost:8000 | true     | Kong Gateway URL                                                      |
| EUREKA_ADMIN_USERNAME     |                       | true     | The username for the admin user in Eureka                             |
| EUREKA_ADMIN_PASSWORD     |                       | true     | The password for the admin user in Eureka                             |
| EUREKA_ROLE_LOAD_STRATEGY | distributed           | true     | Approach how roles were generated (one of: distributed, consolidated) |


---

### `cleanup-hash-roles`

The command will do the following actions:

- Load latest `eureka-cleanup-data-<strategy>-<timestamp>.json.gz`
- Perform role-capabilities and role-capability-set update operations to remove duplicated relations
- Remove hash-roles with empty relations
- Save a report with performed operations into storage (s3, local).

**Requires:**
- The `analyze-hash-roles` command must be run before this command.

**Output:**
- clean hash-roles
- `<tenant_id>/<tenant_id>-hash-roles-cleanup-report-<strategy>-<timestamp>.json.gz`

**Environment Variables:**

| Env Variable              | Default Value         | Required | Description                                                           |
|:--------------------------|:----------------------|:---------|:----------------------------------------------------------------------|
| TENANT_ID                 |                       | true     | The tenant ID for the FOLIO environment                               |
| EUREKA_URL                | http://localhost:8000 | true     | Kong Gateway URL                                                      |
| EUREKA_ADMIN_USERNAME     |                       | true     | The username for the admin user in Eureka                             |
| EUREKA_ADMIN_PASSWORD     |                       | true     | The password for the admin user in Eureka                             |
| EUREKA_ROLE_LOAD_STRATEGY | distributed           | true     | Approach how roles were generated (one of: distributed, consolidated) |

---

### `generate-cleanup-report`

The command will do the following actions:

- Load the latest cleanup result file (`hash-roles-cleanup-report-<strategy>-<timestamp>.json.gz`) from storage.
- Parse the cleanup report data and generate a comprehensive Excel report.
- Store the generated Excel report in the configured storage (S3 or local).

**Requires:**
- The `cleanup-hash-roles` command must be run before this command.
- Access to the AWS S3 bucket or local storage where the cleanup report JSON file is stored.

**Output:**
- `<tenant_id>/<tenant_id>-hash-roles-cleanup-report-<strategy>-<timestamp>.xlsx`

**Environment Variables:**

| Env Variable              | Default Value | Required | Description                                                              |
|:--------------------------|:--------------|:---------|:-------------------------------------------------------------------------|
| TENANT_ID                 |               | true     | The tenant ID for the FOLIO environment                                  |
| EUREKA_ROLE_LOAD_STRATEGY | distributed   | true     | Approach how roles were generated (one of: distributed, consolidated)    |

---

### `download-json`

The command will do the following actions:
- Load `source_file` file and save it on local drive using `out_file` argument

**Requires:**
- Access to the AWS S3 bucket or local storage where `source_file` is stored.

**Output:**
- `out_file` file with the content of `source_file`

---

### `explain-permissions`

The command will do the following actions:

- Load the latest `okapi-permissions-<timestamp>.json.gz` file from storage.
- Explain a specific permission or a list of permissions from a file.
- Display detailed information about permission hierarchies and dependencies.

**Requires:**
- The `collect-permissions` command must be run before this command.
- Access to the AWS S3 bucket or local storage where the `okapi-permissions` file is stored.

**Usage:**

```bash
# Explain a single permission by name
folio-permission-migration-cli explain-permissions --name "permission.name"

# Explain multiple permissions from a file
folio-permission-migration-cli explain-permissions --file "permissions.txt"
```

**Options:**
- `--name, -n`: Name of the permission to explain
- `--file, -f`: File containing permission names to explain (one per line)

**Output:**
- Console output with detailed permission explanations

**Environment Variables:**

| Env Variable | Default Value | Required | Description                             |
|:-------------|:--------------|:---------|:----------------------------------------|
| TENANT_ID    |               | true     | The tenant ID for the FOLIO environment |

---

## Development Tips

You can use a `.env` file to manage these variables.

> **_NOTE:_** It's recommended to not modify the existing `.env` file.
> - Additional file can be used, for example `.local.dev.env`, that is passed using `DOTENV` variables.
> - This allows you to keep the original `.env` file intact and manage your local settings separately.
> - On command initialization, variables `.env` from env will be loaded, then they will be overridden by the variables
    > from the file specified in `DOTENV` env variable.

### General environment variables

| Env Variable           | Default Value | Required | Description                                                            |
|:-----------------------|:--------------|:---------|:-----------------------------------------------------------------------|
| DOTENV                 | .env          | false    | Custom `.env` file location _(preferable to pass it as variable)_      |
| LOG_LEVEL              | INFO          | false    | Log level (one of: INFO, DEBUG, WARN, ERROR, CRITICAL)                 |
| ENABLED_STORAGES       | s3            | false    | Enabled storage for data loading and report output (one of: local, s3) |
| ENABLE_REPORT_COLORING | false         | false    | Boolean value, defines if row colors will be applied for xlsx reports  |
| ACCESS_TOKEN_TTL       | 60            | false    | TTL for access token refresh                                           |


### Environment Variables (S3 Storage)

This environment variables are used to configure the connection to AWS S3 or a compatible storage service (like MinIO).

| Env Variable          | Default Value | Required | Description                                            |
|:----------------------|:--------------|:---------|:-------------------------------------------------------|
| AWS_ACCESS_KEY_ID     |               | true     | AWS Access Key                                         |
| AWS_SECRET_ACCESS_KEY |               | true     | AWS Secret Key                                         |
| AWS_SESSION_TOKEN     |               | false    | AWS Session Key                                        |
| AWS_REGION            | `us-east-1`   | false    | AWS S3 Region                                          |
| AWS_S3_BUCKET         |               | true     | S3 Bucket name (required)                              |
| AWS_S3_ENDPOINT       |               | false    | Custom AWS S3 Endpoint (for example, if MinIO is used) |


### Environment Variables (Local Storage)

This environment variables are used to configure the local storage for the CLI tool.

| Env Variable         | Default Value | Required | Description                                    |
|:---------------------|:--------------|:---------|:-----------------------------------------------|
| STORAGE_LOCAL_FOLDER | `./.temp`     | false    | Path to directory where results will be stored |

---

### Pre-Commit Command

This command is used to normalize the project (applies import sorting, code formatting, and linting):

```bash
poetry run pyrefly check --output-format min-text \
  && poetry run isort . \
  && poetry run black . \
  && poetry run flake8 \
  && poetry run pytest
```

---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
