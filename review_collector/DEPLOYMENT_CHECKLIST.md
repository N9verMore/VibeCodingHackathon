# ✅ Pre-Deployment Checklist

## 🔐 Prerequisites

- [ ] AWS CLI налаштований (`aws configure`)
- [ ] AWS CDK встановлений (`npm install -g aws-cdk`)
- [ ] Python 3.11 встановлений
- [ ] Region: `us-east-1` (або змінити в `cdk/app.py`)

---

## 🔑 Secrets Manager Setup

### Перевірте чи існує secret:
```bash
aws secretsmanager describe-secret \
  --secret-id review-collector/credentials \
  --region us-east-1
```

### Якщо не існує - створіть:
```bash
aws secretsmanager create-secret \
  --name review-collector/credentials \
  --secret-string '{
    "serpapi": {
      "api_key": "YOUR_SERPAPI_KEY_HERE"
    }
  }' \
  --region us-east-1
```

### Якщо існує - оновіть:
```bash
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {
      "api_key": "YOUR_SERPAPI_KEY_HERE"
    }
  }' \
  --region us-east-1
```

---

## 📦 CDK Bootstrap (one-time)

Якщо це перший deploy CDK в цей region:

```bash
cd /Users/myk/PycharmProjects/monitor/VibeCodingHackathon/review_collector/cdk

cdk bootstrap aws://ACCOUNT-NUMBER/us-east-1
```

---

## 🚀 Deployment Steps

### 1. Install CDK Dependencies
```bash
cd /Users/myk/PycharmProjects/monitor/VibeCodingHackathon/review_collector/cdk

pip install -r requirements.txt
```

### 2. Synthesize CloudFormation
```bash
cdk synth
```

**Перевірте output:**
- [ ] Немає помилок
- [ ] Template створений в `cdk.out/`
- [ ] Ресурси виглядають правильно

### 3. Show Diff (якщо updating існуючий stack)
```bash
cdk diff
```

### 4. Deploy
```bash
cdk deploy ReviewCollectorStack
```

**During deployment:**
- [ ] Перегляньте зміни
- [ ] Підтвердіть IAM changes (якщо потрібно)
- [ ] Дочекайтесь завершення (~5-10 хвилин)

### 5. Save Outputs
```bash
# Outputs автоматично збережуться в outputs.json
cat outputs.json
```

---

## ✅ Post-Deployment Verification

### 1. Check Stack Status
```bash
aws cloudformation describe-stacks \
  --stack-name ReviewCollectorStack \
  --query 'Stacks[0].StackStatus' \
  --region us-east-1
```

**Expected:** `CREATE_COMPLETE` або `UPDATE_COMPLETE`

---

### 2. Verify DynamoDB Table
```bash
aws dynamodb describe-table \
  --table-name ReviewsTableV2 \
  --region us-east-1
```

**Check:**
- [ ] Table exists
- [ ] Status: `ACTIVE`
- [ ] Primary Key: `pk` (HASH)
- [ ] GSI: `brand-created_at-index` exists
- [ ] Billing Mode: `PAY_PER_REQUEST`

---

### 3. Verify Lambda Function
```bash
aws lambda get-function \
  --function-name serpapi-collector-lambda \
  --region us-east-1
```

**Check:**
- [ ] Function exists
- [ ] Runtime: `python3.11`
- [ ] Handler: `handler.lambda_handler`
- [ ] Memory: `512 MB`
- [ ] Timeout: `120 seconds`
- [ ] Environment variables:
  - [ ] `TABLE_NAME=ReviewsTableV2`
  - [ ] `SECRET_NAME=review-collector/credentials`
  - [ ] `LOG_LEVEL=INFO`

---

### 4. Verify Lambda Layer
```bash
aws lambda list-layers \
  --region us-east-1 | grep review-collector-shared
```

**Check:**
- [ ] Layer `review-collector-shared` exists

---

### 5. Verify API Gateway
```bash
# Get API ID from outputs.json
API_URL=$(cat outputs.json | grep ApiUrl | cut -d'"' -f4)
echo "API URL: $API_URL"
```

**Check:**
- [ ] API exists
- [ ] Stage: `prod`
- [ ] Endpoint accessible

---

### 6. Test Lambda (Direct Invoke)
```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 5
  }' \
  --region us-east-1 \
  response.json

cat response.json
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": "{\"success\": true, \"message\": \"Reviews collected successfully\", ...}"
}
```

**Check:**
- [ ] statusCode: `200`
- [ ] success: `true`
- [ ] statistics.fetched > 0
- [ ] No errors

---

### 7. Test API Gateway
```bash
# Get API endpoint
API_ENDPOINT=$(cat outputs.json | grep ApiEndpoint | cut -d'"' -f4)

curl -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 5
  }' | jq .
```

**Expected:**
- [ ] HTTP 200 OK
- [ ] JSON response with statistics
- [ ] No errors

---

### 8. Verify Data in DynamoDB
```bash
aws dynamodb scan \
  --table-name ReviewsTableV2 \
  --limit 5 \
  --region us-east-1
```

**Check:**
- [ ] Items exist
- [ ] `pk` format: `{source}#{id}`
- [ ] All required fields present
- [ ] `content_hash` populated

**Query by Brand:**
```bash
aws dynamodb query \
  --table-name ReviewsTableV2 \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand":{"S":"telegram"}}' \
  --limit 5 \
  --region us-east-1
```

---

### 9. Check CloudWatch Logs
```bash
aws logs tail /aws/lambda/serpapi-collector-lambda --follow
```

**Check:**
- [ ] No errors
- [ ] Logs show successful execution
- [ ] Statistics logged

---

### 10. Check IAM Permissions
```bash
# Get Lambda execution role
ROLE_NAME=$(aws lambda get-function \
  --function-name serpapi-collector-lambda \
  --query 'Configuration.Role' \
  --output text | cut -d'/' -f2)

# Check attached policies
aws iam list-attached-role-policies --role-name $ROLE_NAME
aws iam list-role-policies --role-name $ROLE_NAME
```

**Check:**
- [ ] `AWSLambdaBasicExecutionRole` attached
- [ ] Inline policy with DynamoDB permissions
- [ ] Inline policy with Secrets Manager permissions

---

## 🧪 Integration Tests

### Test All Sources

#### 1. App Store
```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 10
  }' \
  test-appstore.json

cat test-appstore.json | jq '.body | fromjson'
```

#### 2. Google Play
```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "googleplay",
    "app_identifier": "org.telegram.messenger",
    "brand": "telegram",
    "limit": 10
  }' \
  test-googleplay.json

cat test-googleplay.json | jq '.body | fromjson'
```

#### 3. Trustpilot
```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "trustpilot",
    "app_identifier": "telegram.org",
    "brand": "telegram",
    "limit": 10
  }' \
  test-trustpilot.json

cat test-trustpilot.json | jq '.body | fromjson'
```

**For each source, check:**
- [ ] statusCode: 200
- [ ] success: true
- [ ] fetched > 0
- [ ] saved + skipped = fetched
- [ ] No errors

---

## 🎯 Performance Checks

### Lambda Metrics
```bash
# Get average duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=serpapi-collector-lambda \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum \
  --region us-east-1
```

**Check:**
- [ ] Average duration < 30 seconds
- [ ] No timeout errors (120s limit)

### DynamoDB Metrics
```bash
# Check consumed capacity
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=ReviewsTableV2 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region us-east-1
```

---

## 📊 Cost Estimation

**Expected monthly costs (for moderate usage):**
- Lambda: $0.20 - $5.00 (depends on invocations)
- DynamoDB: $1.25+ (on-demand, depends on reads/writes)
- API Gateway: $3.50 per million requests
- Secrets Manager: $0.40/month
- CloudWatch Logs: $0.50+

**Total: ~$5-15/month for moderate usage**

---

## 🐛 Troubleshooting

### Issue: Lambda timeout
**Solution:** Increase timeout in stack:
```python
timeout=Duration.seconds(180),  # Increase from 120
```

### Issue: Memory errors
**Solution:** Increase memory:
```python
memory_size=1024,  # Increase from 512
```

### Issue: SerpAPI rate limits
**Check SerpAPI account:**
- Visit: https://serpapi.com/dashboard
- Check remaining credits
- Check rate limits

### Issue: DynamoDB throttling
**Solution:** Check if PAY_PER_REQUEST is active:
```bash
aws dynamodb describe-table \
  --table-name ReviewsTableV2 \
  --query 'Table.BillingModeSummary'
```

---

## 🔄 Update Stack

To update after code changes:

```bash
cd /Users/myk/PycharmProjects/monitor/VibeCodingHackathon/review_collector/cdk

# 1. Show what will change
cdk diff

# 2. Deploy changes
cdk deploy

# 3. Verify
# Run tests from "Post-Deployment Verification" section
```

---

## 🗑️ Cleanup (if needed)

To destroy stack:

```bash
cdk destroy ReviewCollectorStack
```

**WARNING:** This will:
- ❌ Delete Lambda function
- ❌ Delete API Gateway
- ❌ Delete Lambda Layer
- ✅ KEEP DynamoDB table (RemovalPolicy: RETAIN)
- ✅ KEEP Secrets Manager secret

To delete table manually:
```bash
aws dynamodb delete-table --table-name ReviewsTableV2
```

---

## ✅ Final Checklist

- [ ] All tests passing
- [ ] No errors in CloudWatch Logs
- [ ] DynamoDB contains data
- [ ] API Gateway accessible
- [ ] Lambda executing successfully
- [ ] Secrets Manager accessible
- [ ] IAM permissions correct
- [ ] Costs within budget

---

**🎉 Deployment Complete!**

**Next Steps:**
1. Set up monitoring alerts
2. Configure scheduled collection (EventBridge)
3. Set up CI/CD pipeline
4. Add integration tests
5. Monitor costs and optimize

**Documentation:**
- Full fixes: `FIXES_APPLIED.md`
- Changes summary: `CHANGES_SUMMARY.md`
- This checklist: `DEPLOYMENT_CHECKLIST.md`

