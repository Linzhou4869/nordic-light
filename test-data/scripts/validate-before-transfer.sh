#!/bin/bash
# File: validate-before-transfer.sh
# Pre-Transfer Validation Script for Data Repository

REPO_PATH="./data-repository"
MANIFEST="checksums-sha256.txt"
ERRORS=0

echo "=== Pre-Transfer Validation ==="
echo "Repository: $REPO_PATH"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Check 1: File count match
FILE_COUNT=$(find "$REPO_PATH" -type f ! -path "$REPO_PATH/metadata/*" ! -name "checksums-sha256.txt" | wc -l)
MANIFEST_COUNT=$(wc -l < "$REPO_PATH/$MANIFEST")
if [ "$FILE_COUNT" -ne "$MANIFEST_COUNT" ]; then
    echo "❌ FAIL: File count ($FILE_COUNT) != manifest entries ($MANIFEST_COUNT)"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: File count matches manifest ($FILE_COUNT files)"
fi

# Check 2: Zero-byte files
ZERO_BYTES=$(find "$REPO_PATH" -type f ! -path "$REPO_PATH/metadata/*" -size 0 | wc -l)
if [ "$ZERO_BYTES" -gt 0 ]; then
    echo "❌ FAIL: Found $ZERO_BYTES zero-byte files"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No zero-byte files found"
fi

# Check 3: Verify checksums
echo "Verifying SHA-256 checksums..."
cd "$REPO_PATH"
if sha256sum -c "$MANIFEST" --quiet 2>/dev/null; then
    echo "✅ PASS: All checksums verified"
else
    echo "❌ FAIL: Checksum verification failed"
    ERRORS=$((ERRORS + 1))
fi
cd - > /dev/null

# Check 4: Metadata file count
METADATA_COUNT=$(find "$REPO_PATH/metadata" -type f -name "*.json" 2>/dev/null | wc -l)
if [ "$METADATA_COUNT" -ge "$FILE_COUNT" ]; then
    echo "✅ PASS: Metadata records present ($METADATA_COUNT files)"
else
    echo "⚠️  WARNING: Metadata count ($METADATA_COUNT) < data file count ($FILE_COUNT)"
fi

# Check 5: Required fields in metadata
echo "Validating metadata required fields..."
MISSING_FIELDS=0
for meta_file in "$REPO_PATH/metadata"/*.json; do
    if [ -f "$meta_file" ]; then
        for field in document_id created_at modified_at checksum_sha256 file_size_bytes content_type classification_level; do
            if ! grep -q "\"$field\"" "$meta_file"; then
                echo "  ⚠️  Missing field '$field' in $(basename $meta_file)"
                MISSING_FIELDS=$((MISSING_FIELDS + 1))
            fi
        done
    fi
done

if [ "$MISSING_FIELDS" -eq 0 ]; then
    echo "✅ PASS: All required metadata fields present"
else
    echo "⚠️  WARNING: $MISSING_FIELDS required field(s) missing"
fi

echo ""
echo "=== Validation Complete ==="
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ All critical checks passed. Ready for transfer."
    exit 0
else
    echo "❌ $ERRORS critical check(s) failed. Do not proceed with transfer."
    exit 1
fi
