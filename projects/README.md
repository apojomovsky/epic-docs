# Alias shims

Each file here is a `mkdocs-monorepo-plugin` alias: `site_name` fixes
the section's URL prefix, `docs_dir` is the section's page tree,
`nav` lists the section's rows. The hub includes them with
`'!include projects/<name>.yml'`.

Skeleton phase: `docs_dir` points at the hub-owned stub tree next to
the shim, because the owning repositories ship no user-facing pages
yet and their current `docs/` are internal notes that must stay out
of the public hub. When a repository ships its owned pages (the
generators phase), repoint that shim's `docs_dir` at the sibling
checkout, for example `../../epic-cc/docs`, and replace its `nav`
with the repository's owned rows. The sibling layout is locked by
`make check-siblings` and the CI checkout step.
