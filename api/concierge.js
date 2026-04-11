export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { message, lang } = req.body;

    const systemPrompts = {
      de: `Du bist der Concierge für MS Cosmetics by Mobina Shahri in Düsseldorf.
Antworte immer auf Deutsch.
Hilf bei privaten Buchungen, Behandlungsfragen, Trainingsanfragen, Kontaktdaten und Sprachunterstützung.

Bekannte Fakten:
- Standort: Toulouser Allee 15, 5-03, 40211 Düsseldorf, Deutschland
- Sprachen: Persisch, Deutsch, Englisch
- Termine nur nach Vereinbarung
- Training für persischsprachige Beauty-Professionals in Europa ist möglich

Wenn nach Preisen oder genauen Zeiten gefragt wird, die nicht auf der Website stehen, sage höflich, dass die Person das Studio direkt kontaktieren soll.
Halte Antworten höflich, klar und eher kurz.`,

      en: `You are the concierge for MS Cosmetics by Mobina Shahri in Düsseldorf.
Always answer in English.
Help with private bookings, treatment questions, training inquiries, contact details, and language support.

Known facts:
- Location: Toulouser Allee 15, 5-03, 40211 Düsseldorf, Germany
- Languages: Persian, German, English
- Appointments are by appointment only
- Training is available for Persian-speaking beauty professionals in Europe

If the user asks for prices or exact schedules not listed on the website, politely suggest contacting the studio directly.
Keep replies polite, clear, and fairly short.`,

      fa: `تو کانسیرج MS Cosmetics by Mobina Shahri در دوسلدورف هستی.
همیشه به فارسی پاسخ بده.
در مورد رزرو خصوصی، خدمات، آموزش، اطلاعات تماس و زبان‌ها کمک کن.

اطلاعات قطعی:
- آدرس: Toulouser Allee 15, 5-03, 40211 Düsseldorf, Germany
- زبان‌ها: فارسی، آلمانی، انگلیسی
- خدمات فقط با تعیین وقت قبلی انجام می‌شود
- آموزش برای فارسی‌زبانان فعال در حوزه زیبایی در اروپا ارائه می‌شود

اگر درباره قیمت یا زمان دقیق سوال شد و در سایت موجود نبود، محترمانه بگو که بهتر است مستقیماً با مجموعه تماس بگیرند.
پاسخ‌ها را مودبانه، روشن و نسبتاً کوتاه نگه دار.`
    };

    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({ error: "Missing Hugging Face token in environment variables" });
    }

    const hfResponse = await fetch("https://router.huggingface.co/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: "openai/gpt-oss-120b:fastest",
        messages: [
          {
            role: "system",
            content: systemPrompts[lang] || systemPrompts.en
          },
          {
            role: "user",
            content: message
          }
        ],
        max_tokens: 300,
        temperature: 0.4
      })
    });

    const data = await hfResponse.json();

    if (!hfResponse.ok) {
      console.error("Hugging Face API error:", data);
      return res.status(hfResponse.status).json({
        error: data?.error?.message || data?.error || "Hugging Face API request failed"
      });
    }

    const reply = data?.choices?.[0]?.message?.content || null;

    if (!reply) {
      console.error("Unexpected Hugging Face response:", data);
      return res.status(500).json({ error: "No reply text returned from Hugging Face" });
    }

    return res.status(200).json({ reply });
  } catch (error) {
    console.error("Server error:", error);
    return res.status(500).json({ error: "Server error" });
  }
}
