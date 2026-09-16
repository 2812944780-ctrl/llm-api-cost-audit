$ErrorActionPreference = 'Stop'

if (-not $env:OPENAI_API_KEY) { throw 'Set OPENAI_API_KEY first.' }
if (-not $env:OPENAI_MODEL) { throw 'Set OPENAI_MODEL to a model shown by your endpoint.' }
$baseUrl = if ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL.TrimEnd('/') } else { 'https://api.openai.com/v1' }
$body = @{
  model = $env:OPENAI_MODEL
  messages = @(@{ role = 'user'; content = 'Reply with one short sentence: what is a token?' })
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri "$baseUrl/chat/completions" `
  -Headers @{ Authorization = "Bearer $env:OPENAI_API_KEY" } `
  -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 10
