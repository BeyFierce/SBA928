# Production Deployment Plan

## Target architecture

Package AccountLens AI with the included Dockerfile and deploy the same image
through development, staging, and production. Put the Streamlit service behind
TLS termination and an authenticated reverse proxy. Store `OPENAI_API_KEY` in a
managed secret store and inject it only at runtime.

The request flow is:

1. authenticated user submits bounded text, documents, and public URLs;
2. the service validates inputs and outbound destinations;
3. a research worker retrieves allowed public evidence;
4. the specialist and synthesis agents run with request and token limits;
5. the app records redacted operational metrics and returns a reviewable brief.

## Scalability and reliability

- Run multiple stateless containers behind a load balancer.
- Move webpage retrieval and LLM calls to a queue for long-running production
  requests; return job status to the UI instead of holding a web connection.
- Apply per-user concurrency and rate limits to protect both cost and uptime.
- Cache approved public pages by normalized URL with a short expiration time.
- Use request timeouts, bounded context, retry with exponential backoff for
  transient failures, and a dead-letter queue for repeated failures.
- Define availability, latency, failure-rate, and cost-per-brief service-level
  indicators. Alert when any threshold is exceeded.

## Security and privacy

- Keep API keys in a managed secret store; never commit `.env` or log keys.
- Require organization sign-in and role-based access for saved account history.
- Enforce HTTPS, secure cookies, dependency scanning, and image scanning.
- Restrict outbound requests to public HTTP(S) destinations and strengthen the
  prototype validator with DNS/IP checks and an allow/deny policy before launch.
- Revalidate redirect destinations to prevent server-side request forgery.
- Limit uploaded files by extension and size, scan them for malware, extract
  text in an isolated worker, and delete temporary files after processing.
- Encrypt saved briefs and audit logs at rest. Redact product documents,
  customer names, prompts, and model responses from ordinary application logs.
- Treat webpage and document content as untrusted evidence; do not execute or
  obey embedded instructions.

## Observability and cost control

Record request ID, agent stage, model name, latency, token use, source count,
quality warnings, and success/failure status. Do not record raw uploaded files
or secrets. Set per-user and organization budgets, cap context length, and send
an operational alert before the monthly model budget is exhausted.

## Maintenance and release process

- Run tests and dependency/security scans for every pull request.
- Build an immutable container tagged with the Git commit SHA.
- Promote the same image from staging after a smoke test and sample-brief review.
- Keep the previous image available for immediate rollback.
- Review prompts, schemas, supported model versions, and source policies monthly.
- Patch critical dependencies promptly and document any model migration.

## Recovery and retention

Because the service is stateless, a failed release rolls back to the previous
container image. If saved account history is added, back up the encrypted data
store, test restoration quarterly, and define a short retention policy with a
user-controlled delete path. Never retain uploaded documents by default.

## Prototype-to-production gaps

The repository supplies the container, health check, bounded uploads, URL
validation, structured outputs, and deterministic tests. Production launch must
still add identity, queueing, managed storage/secrets, malware scanning, stronger
egress enforcement, centralized monitoring, and an organizational privacy
review.
