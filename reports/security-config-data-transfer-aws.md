# Security Configuration: Data Repository Transfer to AWS

**Document Type:** Security Configuration Specification  
**Date:** 2026-03-29  
**Target Region:** AWS ap-southeast-1 (Singapore)  
**Classification:** Internal Use Only

---

## 1. Encryption Configuration Block

### 1.1 Data at Rest (AES-256)

```yaml
# S3 Bucket Encryption Configuration
# File: s3-encryption-config.yaml

EncryptionConfiguration:
  Rule:
    - ApplyServerSideEncryptionByDefault:
        SSEAlgorithm: AES256
        BucketKeyEnabled: true
  
  # S3 Bucket Policy for mandatory encryption
  BucketPolicy:
    Version: "2012-10-17"
    Statement:
      - Sid: DenyUnencryptedObjectUploads
        Effect: Deny
        Principal: "*"
        Action: s3:PutObject
        Resource: "arn:aws:s3:::data-repository-ap-southeast-1/*"
        Condition:
          StringNotEquals:
            s3:x-amz-server-side-encryption: "AES256"
      
      - Sid: DenyUnencryptedObjectDownloads
        Effect: Deny
        Principal: "*"
        Action: s3:GetObject
        Resource: "arn:aws:s3:::data-repository-ap-southeast-1/*"
        Condition:
          StringNotEquals:
            s3:x-amz-server-side-encryption: "AES256"
```

### 1.2 Data in Transit (TLS 1.3)

```yaml
# TLS Configuration for Data Transfer
# File: tls-transfer-config.yaml

TransferSecurityPolicy:
  MinimumTLSVersion: "TLSv1.3"
  TLSPolicy: "TLS-1-3-2021-06-01"
  
  # S3 Bucket Policy for TLS enforcement
  BucketPolicy:
    Version: "2012-10-17"
    Statement:
      - Sid: EnforceTLS13
        Effect: Deny
        Principal: "*"
        Action: s3:*
        Resource:
          - "arn:aws:s3:::data-repository-ap-southeast-1"
          - "arn:aws:s3:::data-repository-ap-southeast-1/*"
        Condition:
          Bool:
            aws:SecureTransport: "false"
  
  # AWS CLI Configuration
  AWS_CLI_Config:
    Section: default
    Settings:
      - region = ap-southeast-1
      - output = json
      - cli_follow_urlparam = true
      - s3 =
        - max_concurrent_requests = 10
        - max_queue_size = 1000
        - multipart_threshold = 64MB
        - multipart_chunksize = 16MB
        - addressing_style = path
```

### 1.3 Terraform Configuration (Infrastructure as Code)

```hcl
# File: main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_s3_bucket" "data_repository" {
  bucket = "data-repository-ap-southeast-1"
  
  tags = {
    Name        = "Secure Data Repository"
    Environment = "Production"
    Encryption  = "AES-256"
    Region      = "ap-southeast-1"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.data_repository.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_policy" "security_policy" {
  bucket = aws_s3_bucket.data_repository.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyUnencryptedUploads"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.data_repository.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption" = "AES256"
          }
        }
      },
      {
        Sid       = "EnforceTLS13"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [
          aws_s3_bucket.data_repository.arn,
          "${aws_s3_bucket.data_repository.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.data_repository.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

---

## 2. Metadata Integrity Verification Checklist

### Pre-Upload Verification

**Complete all items before initiating transfer:**

#### 2.1 File-Level Integrity

- [ ] **Generate SHA-256 checksums** for all data files
  ```bash
  find ./data-repository -type f -exec sha256sum {} \; > checksums-sha256.txt
  ```

- [ ] **Verify checksum manifest exists** and is readable
  ```bash
  cat checksums-sha256.txt | wc -l  # Count matches expected file count
  ```

- [ ] **Cross-reference file count** between source and manifest
  ```bash
  find ./data-repository -type f | wc -l
  ```

#### 2.2 Metadata Schema Validation

- [ ] **Validate JSON/YAML metadata files** against schema
  ```bash
  # Example using ajv for JSON Schema validation
  ajv validate -s metadata-schema.json -d metadata/*.json
  ```

- [ ] **Confirm required fields present** in all metadata records:
  - [ ] `document_id` (UUID format)
  - [ ] `created_at` (ISO 8601 timestamp)
  - [ ] `modified_at` (ISO 8601 timestamp)
  - [ ] `checksum_sha256` (64-character hex)
  - [ ] `file_size_bytes` (integer)
  - [ ] `content_type` (MIME type)
  - [ ] `classification_level` (enum: public/internal/confidential/restricted)

- [ ] **Verify no orphaned metadata** (metadata without corresponding data file)

- [ ] **Verify no orphaned data files** (data file without metadata record)

#### 2.3 Data Quality Checks

- [ ] **Scan for corrupted files** (zero-byte, incomplete writes)
  ```bash
  find ./data-repository -type f -size 0
  ```

- [ ] **Validate file encoding** (UTF-8 for text files)
  ```bash
  file --mime-encoding ./data-repository/**/*.txt
  ```

- [ ] **Check for special characters** in filenames that may cause upload issues
  ```bash
  find ./data-repository -type f -name '*[<>:"|?*]*'
  ```

#### 2.4 Security Classification Review

- [ ] **Confirm all files have classification labels** assigned

- [ ] **Verify sensitive data handling** matches classification level:
  - [ ] Confidential/Restricted files encrypted before transfer
  - [ ] PII flagged for additional compliance review

- [ ] **Audit access control lists** (ACLs) are documented

#### 2.5 Pre-Transfer Validation Script

```bash
#!/bin/bash
# File: scripts/validate-before-transfer.sh

REPO_PATH="./data-repository"
MANIFEST="checksums-sha256.txt"
ERRORS=0

echo "=== Pre-Transfer Validation ==="
echo "Repository: $REPO_PATH"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Check 1: File count match
FILE_COUNT=$(find "$REPO_PATH" -type f | wc -l)
MANIFEST_COUNT=$(wc -l < "$MANIFEST")
if [ "$FILE_COUNT" -ne "$MANIFEST_COUNT" ]; then
    echo "❌ FAIL: File count ($FILE_COUNT) != manifest entries ($MANIFEST_COUNT)"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: File count matches manifest ($FILE_COUNT files)"
fi

# Check 2: Zero-byte files
ZERO_BYTES=$(find "$REPO_PATH" -type f -size 0 | wc -l)
if [ "$ZERO_BYTES" -gt 0 ]; then
    echo "❌ FAIL: Found $ZERO_BYTES zero-byte files"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No zero-byte files found"
fi

# Check 3: Verify checksums
echo "Verifying SHA-256 checksums..."
if sha256sum -c "$MANIFEST" --quiet 2>/dev/null; then
    echo "✅ PASS: All checksums verified"
else
    echo "❌ FAIL: Checksum verification failed"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Metadata schema validation
echo "Validating metadata schema..."
if command -v ajv &> /dev/null; then
    if ajv validate -s metadata-schema.json -d metadata/*.json --errors=text 2>/dev/null; then
        echo "✅ PASS: Metadata schema validation passed"
    else
        echo "❌ FAIL: Metadata schema validation failed"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "⚠️  SKIP: ajv not installed, schema validation skipped"
fi

echo ""
echo "=== Validation Complete ==="
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ All checks passed. Ready for transfer."
    exit 0
else
    echo "❌ $ERRORS check(s) failed. Do not proceed with transfer."
    exit 1
fi
```

---

## 3. Post-Upload Verification

### After Transfer Completion

- [ ] **Re-verify checksums** on AWS S3
  ```bash
  aws s3 cp s3://data-repository-ap-southeast-1/ ./downloaded/ --recursive
  sha256sum -c checksums-sha256.txt
  ```

- [ ] **Confirm encryption status** via AWS CLI
  ```bash
  aws s3api head-object --bucket data-repository-ap-southeast-1 --key <file-key> \
    --query 'ServerSideEncryption' --output text
  # Expected output: AES256
  ```

- [ ] **Verify TLS in transit** via CloudTrail logs
  ```bash
  aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=PutObject \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
  ```

- [ ] **Enable S3 Access Logging** for audit trail

- [ ] **Configure S3 Object Lock** (if retention policy required)

---

## 4. AWS Region Configuration Summary

| Setting | Value |
|---------|-------|
| **Region** | ap-southeast-1 |
| **Region Name** | Asia Pacific (Singapore) |
| **Encryption at Rest** | AES-256 (SSE-S3) |
| **Encryption in Transit** | TLS 1.3 |
| **Bucket Versioning** | Enabled |
| **Access Logging** | Recommended |
| **Compliance** | SOC 2, ISO 27001 |

---

## 5. Approval Signatures

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Security Reviewer | | | |
| Data Owner | | | |
| Operations Lead | | | |

---

*Document generated for secure data repository transfer to AWS ap-southeast-1*
