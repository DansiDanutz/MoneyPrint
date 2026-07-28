# Accepted CodeQL findings

The adjacent JSON file is a fail-closed, exact-location allowlist for findings
that CodeQL cannot currently prove safe. A rule, path, or line change makes CI
fail and requires a new review. It is not a rule-wide exclusion.

- `app/utils/file_security.py:35` validates that a resolved path is an existing
  file only after `realpath` and `commonpath` prove containment in the allowed
  base directory.
- `app/controllers/v1/video.py:306` and `:310` operate on a task directory only
  after basename equality rejects separators, traversal, empty names, `.` and
  `..`. The route can delete only the server's matching completed task.
- `app/controllers/v1/video.py:449`, `:455`, and `:494` consume the value returned
  by the containment-and-existing-file validator above.
- `test/services/test_mpt_agent_skill.py:145` writes a synthetic placeholder to
  a temporary test configuration and verifies that it is never printed. It is
  neither a credential nor production data.

Do not broaden these entries to a whole rule or file. Prefer deleting an entry
when CodeQL learns the sanitizer or the code can express the invariant in a way
the analyzer recognizes.
