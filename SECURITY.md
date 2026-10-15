# Security boundaries

Evidence RAG v1 is a loopback demonstration over owned fictional material. Its launch-code sessions are not a production identity system. Bind only to 127.0.0.1, keep one API process, and use the exact web origin on port 5115. Do not expose these servers through a public tunnel or use them for private customer documents.

Reader/maintainer roles live on the server. Opaque session cookies, CSRF tokens, origin/Host checks and server-side filtering protect the demo routes. Access is checked before retrieval and again when the complete answer is published. Role-specific FTS tables avoid private corpus statistics changing reader scores. Source text is escaped; retrieved instructions cannot execute tools or grant permissions. See the tested disclosure and lifecycle matrix in [VERIFICATION.md](docs/VERIFICATION.md).

Replacement swaps the active source and indexes in one transaction. Deletion logically removes stored bodies, chunks, vectors, cache payloads and queued replacement payloads before returning success. It does not promise forensic erasure of disk/WAL pages, backups or information a user already saw. Superseded history is maintainer-only and deleted history is unavailable.

Local models use pinned safetensors snapshots, no remote code, local-only loading and bounded supervised workers. A valid citation checks identity/version/offsets; it does not prove a generated claim is entailed. Invalid model JSON or citation IDs cause abstention.

Application logs contain route templates, status, request ID and duration. They omit questions, source bodies, cookies, codes and raw URLs. The app disables Uvicorn's raw access logger. Browser acceptance traces and videos are disabled because authentication steps carry ephemeral codes.

For a vulnerability, contact the repository maintainer through a private channel they provide. Do not put credentials, private source text or exploitable details into a public issue. No public disclosure endpoint or hosted service has been configured in this local project.
