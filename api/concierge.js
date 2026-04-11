export default async function handler(req, res) {
  try {
    const { message, lang } = req.body;

    const systemPrompts = {
      de: "Du bist der Concierge für MS Cosmetics in Düsseldorf...",
      en: "You are the concierge for MS Cosmetics in Düsseldorf...",
      fa: "تو کانسیرج MS Cosmetics هستی..."
    };

    const response = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: "gpt-4.1-mini",
        input: [
          {
            role: "system",
            content: systemPrompts[lang] || systemPrompts.en
          },
          {
            role: "user",
            content: message
          }
        ]
      })
    });

    const data = await response.json();

    const reply =
      data.output_text ||
      data.output?.[0]?.content?.[0]?.text ||
      "No response";

    res.status(200).json({ reply });

  } catch (err) {
    res.status(500).json({ error: "Server error" });
  }
}
