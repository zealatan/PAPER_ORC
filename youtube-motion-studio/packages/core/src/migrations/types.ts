/**
 * Versioned migration contract (spec §29.3). Migrations are ordered, tested, non-destructive
 * where possible, and idempotent when practical.
 */
export interface ProjectMigration {
  /** Source schema version this migration upgrades from, e.g. "0.9.0". */
  from: string;
  /** Target schema version this migration upgrades to, e.g. "1.0.0". */
  to: string;
  /** Optional human description for the migration report. */
  description?: string;
  /** Transform pre-validation project data from `from` to `to`. Must not mutate its input. */
  migrate(project: unknown): unknown;
}

/** Result of running the migration chain. */
export interface MigrationRunResult {
  project: unknown;
  /** Ordered list of `from→to` steps that were applied (empty when already current). */
  applied: string[];
}
