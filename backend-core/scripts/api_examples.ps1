# API Examples для BrandPulse (PowerShell)
# Використання: .\scripts\api_examples.ps1

$API_URL = "http://localhost:8000"

Write-Host "🚀 BrandPulse API Examples" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n1️⃣ Health Check" -ForegroundColor Yellow
Invoke-RestMethod -Uri "$API_URL/" -Method Get | ConvertTo-Json

# 2. Get Statistics
Write-Host "`n2️⃣ Get Statistics" -ForegroundColor Yellow
$stats = Invoke-RestMethod -Uri "$API_URL/api/statistics" -Method Get
Write-Host "Total Mentions: $($stats.total_mentions)"
Write-Host "Reputation Score: $($stats.reputation_score.overall_score)/100"
Write-Host "Trend: $($stats.reputation_score.trend)"

# 3. Get Reputation Score
Write-Host "`n3️⃣ Reputation Score" -ForegroundColor Yellow
Invoke-RestMethod -Uri "$API_URL/api/reputation-score" -Method Get | ConvertTo-Json

# 4. Check Crisis
Write-Host "`n4️⃣ Crisis Detection" -ForegroundColor Yellow
$crisis = Invoke-RestMethod -Uri "$API_URL/api/crisis/check" -Method Get
if ($crisis.crisis_detected) {
    Write-Host "⚠️ CRISIS DETECTED!" -ForegroundColor Red
    Write-Host "Level: $($crisis.alert.crisis_level)"
    Write-Host "Affected: $($crisis.alert.affected_count)"
} else {
    Write-Host "✅ No crisis detected" -ForegroundColor Green
}

# 5. Add Comment
Write-Host "`n5️⃣ Add Comment" -ForegroundColor Yellow
$comment = @{
    body = "Чудова якість продукту!"
    timestamp = "2025-10-04T15:00:00"
    rating = 5.0
    platform = "trustpilot"
    sentiment = "positive"
    category = "quality"
    llm_description = "Користувач хвалить якість"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "$API_URL/api/comments" -Method Post -Body $comment -ContentType "application/json"
Write-Host "Comment added: $($result.comment_id)"

# 6. Search Comments
Write-Host "`n6️⃣ Search Comments" -ForegroundColor Yellow
$search = Invoke-RestMethod -Uri "$API_URL/api/search/comments?query=якість&limit=5" -Method Get
Write-Host "Found: $($search.results.Count) comments"

# 7. Chat Query
Write-Host "`n7️⃣ Chat with AI" -ForegroundColor Yellow
$chatQuery = @{
    message = "Які найпоширеніші проблеми з брендом?"
} | ConvertTo-Json

$chatResponse = Invoke-RestMethod -Uri "$API_URL/api/chat" -Method Post -Body $chatQuery -ContentType "application/json"
Write-Host "`nAI Response:"
Write-Host $chatResponse.answer

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✅ All examples completed!" -ForegroundColor Green
