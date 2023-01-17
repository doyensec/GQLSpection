## Writing simple e2e tests

1. Create a minimal schema file with a descriptive name within the data directory, add `.json` extension.
2. Create a file with the same basename and extension `.queries.txt`, listing expected queries (should match
 `gqlspection -Q -f FILENAME` output).
3. Create a similar fine for mutations with an extension `.mutations.txt`.
4. Feel free to create only one of the files (only for queries or only for mutations).
