"""Verify the immutable study CSV without fitting models."""
from research_validation import audit

if __name__ == '__main__':
    audit(record_run_metadata=False)
    print('Dataset hash, counts, IDs, groups and archived partitions verified.')
