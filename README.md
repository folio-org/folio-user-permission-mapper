# FOLIO User Permission Mapper

`folio-user-permission-mapper` is a CLI tool designed to collect and analyze user permissions in a
FOLIO environment. It integrates with various services to fetch, process, and store permission data
for further analysis.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
    - [collect-permissions](#collect-permissions)
    - [collect-capabilities](#collect-capabilities)
    - [generate-report](#generate-report)
    - [run-eureka-migration](#run-eureka-migration)
- [Development Tips](#development-tips)
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

#### Description

The command will do the following actions:

- Collect the following data from Okapi-based deployment:
    - module-descriptors from `okapi`
    - permission sets from `mod-permissions`
    - user permissions relations from `mod-permissions`
- Save the result as a gzipped JSON file to the configured storage (S3 or local).

#### Requires

- Access to the Okapi-based environment.
- User credentials with read access to the `mod-permissions` and `okapi` modules.
- Access to the AWS S3 bucket or local storage where the `okapi-permissions` load result will be stored.

#### Output

- `<tenant_id>/<tenant_id>-okapi-permissions.json.gz`

### Environment Variables

| Env Variable                  | Default Value         | Required | Description                                                       |
|:------------------------------|:----------------------|:---------|:------------------------------------------------------------------|
| AWS_ACCESS_KEY_ID             |                       | true     | AWS access key                                                    |
| AWS_SECRET_ACCESS_KEY         |                       | true     | AWS secret key                                                    |
| AWS_REGION                    | `us-east-1`           | false    | AWS S3 Region                                                     |
| AWS_S3_ENDPOINT               |                       | false    | Custom AWS S3 Endpoint (for example, if MinIO is used )           |
| OKAPI_URL                     | http://localhost:9130 | true     | Okapi URL                                                         |
| TENANT_ID                     |                       | true     | The tenant ID for the FOLIO environment                           |
| OKAPI_ADMIN_USERNAME          |                       | true     | The username for the admin user in Okapi                          |
| OKAPI_ADMIN_PASSWORD          |                       | true     | The password for the admin user in Okapi                          |
| PERMISSION_IDS_PARTITION_SIZE | 50                    | true     | The max number of permissions provided in any match query         |
| DOTENV                        | .env                  | false    | Custom `.env` file location _(preferable to pass it as variable)_ |

---

### `collect-capabilities`

#### Description

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

#### Requires

- Access to the Eureka-based environment.
- User credentials with read access to the `mod-roles-keycloak` module.
- Access to the AWS S3 bucket or local storage where the `eureka-capabilities` load result will be stored.

#### Output

- `<tenant_id>/<tenant_id>-eureka-capabilities.json.gz`

### Environment Variables

| Env Variable          | Default Value         | Required | Description                                                       |
|:----------------------|:----------------------|:---------|:------------------------------------------------------------------|
| AWS_ACCESS_KEY_ID     |                       | true     | AWS access key                                                    |
| AWS_SECRET_ACCESS_KEY |                       | true     | AWS secret key                                                    |
| AWS_REGION            | `us-east-1`           | false    | AWS S3 Region                                                     |
| AWS_S3_ENDPOINT       |                       | false    | Custom AWS S3 Endpoint (for example, if MinIO is used)            |
| EUREKA_URL            | http://localhost:8000 | true     | Kong Gateway URL                                                  |
| TENANT_ID             |                       | true     | The tenant ID for the FOLIO environment                           |
| EUREKA_ADMIN_USERNAME |                       | true     | The username for the admin user in Okapi                          |
| EUREKA_ADMIN_PASSWORD |                       | true     | The password for the admin user in Okapi                          |
| DOTENV                | .env                  | false    | Custom `.env` file location _(preferable to pass it as variable)_ |

---

### `generate-report`

#### Description

The command will do the following actions:

- Load `okapi-permissions.gson.gz` and _(optionally)_ `eureka-capabilities` from storage.
- Analyze and combine the data to provide report and data for eureka migration.
- Generate both an Excel report and a gzipped JSON analysis result.
- Store generated files in the configured storage (s3, local).

#### Requires

- Access to the AWS S3 bucket or local storage where `okapi-permissions.gson.gz` is stored.
- The `collect-permissions` and (_optionally_)`collect-capabilities` commands must be run before this command.

#### Output

- `<tenant_id>/<tenant_id>-analysis-result-<generation_timestamp>.xlsx`
- `<tenant_id>/<tenant_id>-analysis-result.json.gz`

### Environment Variables

| Env Variable                   | Default Value | Required | Description                                                                                                                                 |
|:-------------------------------|:--------------|:---------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| AWS_ACCESS_KEY_ID              |               | true     | AWS access key                                                                                                                              |
| AWS_SECRET_ACCESS_KEY          |               | true     | AWS secret key                                                                                                                              |
| AWS_REGION                     | `us-east-1`   | false    | AWS S3 Region                                                                                                                               |
| AWS_S3_ENDPOINT                |               | false    | Custom AWS S3 Endpoint (for example, if MinIO is used )                                                                                     |
| TENANT_ID                      |               | true     | The tenant ID for the FOLIO environment                                                                                                     |
| SYSTEM_GENERATED_PERM_MAPPINGS |               | false    | Comma-separated list of system-generated permission mappings to highlight in analysis (e.g., `folio_admin:AdminRole`)                       |
| REF_CAPABILITIES_FILE_KEY      |               | false    | File key in storage that can be used as reference for capabilities (Recommended to pull this data for tenant with all applications enabled) |
| DOTENV                         | .env          | false    | Custom `.env` file                                                                                                                          |

---

### `run-eureka-migration`

#### Description

The command will do the following actions:

- Load `<tenant>-analysis-result.json.gz` and from storage.
- Create roles (values specified in `SYSTEM_GENERATED_PERM_MAPPINGS` will be skipped)</br>
  _If a role exists, it will be skipped (skipped operations will be visible in error report)._
- Assign capabilities and capability-sets to a role</br>
  _All existing relations will be skipped (skipped operations will be visible in error report)._
- Assign users to a role
- All users, that had roles, defined in `SYSTEM_GENERATED_PERM_MAPPINGS`, will be assigned to the role with the same
  name as the role.</br>
  _If a user already has a role, it will be skipped (skipped operations will be visible in error report)._
- Save a report with occurred errors to storage.

#### Requires

- The `generate-report`command must be run before this command.
- Access to the AWS S3 bucket or local storage where `analysis-result.json.gz` is stored.

#### Output

- new roles
- new user-role relations
- new role-capability relations
- new role capability-set relations
- `<tenant_id>/<tenant_id>-eureka-migration-report.json.gz`

### Environment Variables:

| Env Variable                   | Default Value         | Required | Description                                                                                                                                              |
|:-------------------------------|:----------------------|:---------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| AWS_ACCESS_KEY_ID              |                       | true     | AWS access key                                                                                                                                           |
| AWS_SECRET_ACCESS_KEY          |                       | true     | AWS secret key                                                                                                                                           |
| AWS_REGION                     | `us-east-1`           | false    | AWS S3 Region                                                                                                                                            |
| AWS_S3_ENDPOINT                |                       | false    | Custom AWS S3 Endpoint (for example, if MinIO is used)                                                                                                   |
| EUREKA_URL                     | http://localhost:8000 | true     | Kong Gateway URL                                                                                                                                         |
| TENANT_ID                      |                       | true     | The tenant ID for the FOLIO environment                                                                                                                  |
| EUREKA_ADMIN_USERNAME          |                       | true     | The username for the admin user in Eureka                                                                                                                |
| EUREKA_ADMIN_PASSWORD          |                       | true     | The password for the admin user in Eureka                                                                                                                |
| EUREKA_ROLE_LOAD_STRATEGY      | distributed           | true     | Approach how roles must be generated (one of: distributed, consolidated)                                                                                 |
| SYSTEM_GENERATED_PERM_MAPPINGS |                       | false    | Comma-separated list of system-generated permission mappings that will be applied differently (see: command description) (e.g., `folio_admin:AdminRole`) |
| CAPABILITY_IDS_PARTITION_SIZE  | 50                    | false    | The max number of permission names provided for capability/capability-set querying                                                                       |


---

### `download-json`

#### Description

The command will do the following actions:

- Load `source_file` file and save it on local drive using `out_file` argument

#### Requires

- Access to the AWS S3 bucket or local storage where `source_file` is stored.

#### Output

- `out_file` file with the content of `source_file`

### Environment Variables

| Env Variable          | Default Value | Required | Description    |
|:----------------------|:--------------|:---------|:---------------|
| AWS_ACCESS_KEY_ID     |               | true     | AWS access key |
| AWS_SECRET_ACCESS_KEY |               | true     | AWS secret key |
| AWS_REGION            | `us-east-1`   | false    | AWS S3 Region  |

---

## Development Tips

You can use a `.env` file to manage these variables.

> **_NOTE:_** It's recommended to not modify the existing `.env` file.
> - Additional file can be used, for example `.local.dev.env`, that is passed using `DOTENV` variables.
> - This allows you to keep the original `.env` file intact and manage your local settings separately.
> - On command initialization, variables `.env` from env will be loaded, then they will be overridden by the variables
    > from the file specified in `DOTENV` env variable.

### General environment variables

| Env Variable     | Default Value | Required | Description                                                            |
|:-----------------|:--------------|:---------|:-----------------------------------------------------------------------|
| DOTENV           | .env          | false    | Custom `.env` file location _(preferable to pass it as variable)_      |
| LOG_LEVEL        | INFO          | false    | Log level (one of: INFO, DEBUG, WARN, ERROR, CRITICAL)                 |
| ENABLED_STORAGES |               | false    | Enabled storage for data loading and report output (one of: local, s3) |

### Development

This command is used to normalize the project (applies import sorting, code formatting, and linting):

```bash
 poetry run isort . && poetry run black . && poetry run flake8 
```

---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
