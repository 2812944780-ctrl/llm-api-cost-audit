const apiKey = process.env.OPENAI_API_KEY;
const baseUrl = (process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1').replace(/\/$/, '');
const model = process.env.OPENAI_MODEL;

if (!apiKey) throw new Error('Set OPENAI_API_KEY first.');
if (!model) throw new Error('Set OPENAI_MODEL to a model shown by your endpoint.');

const response = await fetch(`${baseUrl}/chat/completions`, {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model,
    messages: [{ role: 'user', content: 'Reply with one short sentence: what is a token?' }],
  }),
});

const body = await response.json();
if (!response.ok) {
  console.error(JSON.stringify(body, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({
  status: response.status,
  model: body.model,
  usage: body.usage,
  finish_reason: body.choices?.[0]?.finish_reason,
  text: body.choices?.[0]?.message?.content,
}, null, 2));
