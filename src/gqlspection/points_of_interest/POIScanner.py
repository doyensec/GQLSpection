# coding: utf-8
import re
from .keywords import DEFAULT_KEYWORDS, DEFAULT_CATEGORIES

# NOTE: This is a work in progress. Wishlist:
#
#  - Allow overwriting of keywords (not just appending)
#  - Aggregate results & deduplicate findings
#  - Generate minimal repros for findings
#  - Search descriptions for keywords (only field names are searched right now)
#    (this is tricky because descriptions can be in multiple languages, and
#     some keywords might generate too many false positives)
#  - Include field/type descriptions in results


class POIScanner(object):
    """Scan a GQLSchema for points of interest (POIs).

    This is a scanner that looks for keywords and patterns that might be of
    interest to a security researcher:

        * Sensitive information
        * Potential PII disclosure
        * Authentication endpoints
        * Custom scalar types
        * File upload
        * Database operations
        * Debug endpoints
        * Deprecated fields
    """
    def __init__(self, schema, categories=None, keywords=None):
        self.schema = schema
        self.examined_types = set()
        self.categories = categories or DEFAULT_CATEGORIES

        # Pre-compile regexes
        self.compiled_keywords = {}
        for keyword in DEFAULT_KEYWORDS:
            cat = keyword["id"]

            if cat not in self.categories:
                continue

            self.compiled_keywords[cat] = {
                "name": keyword["name"],
                # combine keywords into a single regex
                "regex": re.compile("|".join(keyword["keywords"]), re.IGNORECASE),
            }

        # Add custom keywords
        # ignore keywords if not list or ()
        if keywords and isinstance(keywords, (list, tuple)):
            keywords = [k for k in keywords if k]
            if keywords:
                self.compiled_keywords["custom"] = {
                    "name": "Custom",
                    "regex": re.compile("|".join(keywords), re.IGNORECASE),
                }

    def scan(self, depth=4):
        """Scan the schema for points of interest."""
        results = []

        # Scan both the query and mutation types (if present)
        initial_types = [self.schema.query]
        if self.schema.mutation:
            initial_types.append(self.schema.mutation)

        # Scan each field in each type
        for gql_type in initial_types:
            for field in gql_type.fields:
                if field.name == "__typename":
                    continue

                results.extend(self._scan_field(field, depth, path=gql_type.name))

        # Categorize results
        categorized = {}
        for result in results:
            category = result["type"]
            del result["type"]

            if category not in categorized:
                categorized[category] = []

            categorized[category].append(result)

        return categorized

    def _scan_field(self, field, depth, path):
        """Scan a GQLField for points of interest."""

        results = []
        path = "{}.{}".format(path, field.name)

        # 1. Process current field

        # Check deprecated status
        if "deprecated" in self.categories and field.is_deprecated:
            results.append({
                "type": "Deprecated",
                "path": path,
                "description": field.description or field.type.description
            })

        # Check if the field is custom scalar type
        if "custom_scalars" in self.categories:
            if field.type.kind.kind == "SCALAR" and not field.type.kind.is_builtin_scalar:
                results.append({
                    "type": "Custom Scalar",
                    "path": path,
                    "description": field.description or field.type.description
                })

        # Check for default keywords
        for cat in self.compiled_keywords:
            keyword = self.compiled_keywords[cat]

            if keyword["regex"].search(field.name):
                results.append({
                    "type": keyword["name"],
                    "path": path,
                    "description": field.description or field.type.description
                })
                break

        # 2. Recurse into subfields if not at max depth
        depth -= 1
        if depth < 0:
            return results

        for f in field.type.fields:
            if f.name == "__typename":
                continue

            # Deduplicate results
            if f.type.kind.kind == 'OBJECT' and f.type.name in self.examined_types:
                continue
            self.examined_types.add(f.type.name)

            results.extend(self._scan_field(f, depth, path=path))

        return results
