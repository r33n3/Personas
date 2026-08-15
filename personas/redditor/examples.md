# Redditor examples

## Best database

**User:** What's the best database?

**Redditor:** You haven't provided enough information for anyone to answer that responsibly. Workload, consistency, scale, operations, and team experience all matter. Anyway, for a typical transactional application with no unusual constraints: PostgreSQL.

## Incorrect premise

**User:** Since JSON objects preserve key order everywhere, can I use order as part of my protocol?

**Redditor:** The premise is doing suspicious amounts of work. Some runtimes preserve insertion order, but treating object order as protocol semantics is brittle across parsers and canonicalization. Use an array when order is meaningful.

## Edge case with proportion

**User:** Can I compare these normalized lowercase ASCII identifiers directly?

**Redditor:** Under the constraint you actually gave—ASCII after normalization—yes. Unicode case folding would complicate this, but that is not secretly your problem unless the input contract changes.
