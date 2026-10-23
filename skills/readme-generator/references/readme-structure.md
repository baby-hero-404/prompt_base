# README Structure

Full README template (section 4 of `SKILL.md`). Loaded on demand.

## 4. README Structure

Generate the `README.md` using the structure and headings below. If a section is not applicable or unverifiable, omit it — do not pad it with guesses.

```markdown
# [Project Name]

[Short description of the project and its primary purpose, derived from source code and docs. Make it compelling and clear.]

[Preserved badges / screenshots, if updating an existing README]

## Quick Start

*The shortest VERIFIED path to running the project, using only commands that actually exist in this repository (npm script, Makefile target, compose file, etc.). Do not assume a default like `docker compose up` — derive it from what you discovered.*
```bash
[verified minimal command sequence: clone → configure → run]
```

## Features
- [List key capabilities verified in the source code]
- [Highlight important functionality]
- [Be concise but descriptive]

## Tech Stack
*List the verified technologies used in the project:*
- **Language:** [e.g., Go, TypeScript, Python]
- **Framework:** [e.g., Next.js, FastAPI, Gin]
- **Database:** [e.g., PostgreSQL, MongoDB, Redis]
- **Infrastructure:** [e.g., Docker, Kubernetes, AWS]
- **Libraries/Tools:** [List critical architectural libraries]

## Architecture Overview
*Go beyond a one-paragraph summary when the repository supports it. Describe:*
- Module responsibilities (what each main package/folder owns)
- Request flow (entry point → routing → business logic → persistence)
- Dependency relationships between modules
- External services and integrations
- Authentication/authorization approach
- Background jobs, queues, and caching (if present)

*Only include details supported by the repository. Preserve existing architecture diagrams.*

## Project Structure
*Explain the important folders and files you discovered during analysis:*
```text
/cmd         # Application entry points
/internal    # Private application and library code
/pkg         # Library code ok to use by external applications
/config      # Configuration files
/scripts     # Build, install, analysis scripts
```

## Prerequisites

*List software required to run the project. Specify versions if known:*
- [e.g., Docker & Docker Compose]
- [e.g., Node.js v18+]
- [e.g., Go 1.21+]
- [e.g., PostgreSQL 15+]

## Installation

*Provide step-by-step setup instructions. Assume the user is starting from scratch.*

1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd <project_name>
   ```

2. [Install dependencies command, e.g., `npm install` or `go mod download`]

3. [Any necessary setup steps like migrations or build processes]

## Configuration

*Document ONLY environment variables actually referenced in the project (from `.env.example`, docker-compose, CI workflows, or source code).*

| Variable | Description | Example / Default |
|----------|-------------|-------------------|
| `PORT`   | Port the server binds to | `8080` |
| `DB_URL` | Connection string for the database | `postgres://user:pass@localhost:5432/db` |

## Running the Project

### Development
*Command(s) to run the application locally or in watch mode, verified against package scripts or Makefile.*

### Production
*Instructions for running in production, based on discovered infrastructure files.*

## Testing

*Explain how to run the automated tests (verify commands against package scripts or CI workflows).*

## API Documentation

*Describe how to interact with the system or link to available documentation:*
- Location of Swagger/OpenAPI schemas (if found).
- Example of a core REST endpoint or GraphQL query taken from actual route definitions.

## Deployment

*Provide instructions based on discovered infrastructure files and CI/CD workflows — never invent a deployment target:*
- Docker procedures
- Kubernetes manifests usage
- CI/CD pipeline behavior (what the workflows actually build and publish)
- Cloud-specific setups (Vercel, AWS, GCP) only if evidenced by config

## Troubleshooting

*Include common issues discoverable from the project setup, for example:*
- Port already in use (which port the app binds to and how to change it)
- Missing environment variables (which ones are required and what fails without them)
- Database connection errors (expected DB host/port from compose or config)

## Security

*If the repository contains `SECURITY.md`, summarize it here (supported versions, how to report vulnerabilities) and link to it.*

## Contributing

*Follow `CONTRIBUTING.md` if present; otherwise the standard fork → feature branch → PR workflow.*

## License
*State the project license exactly as found in the repository, or state that none is specified.*
```

