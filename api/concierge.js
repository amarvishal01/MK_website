export default async function handler(req, res) {
  // ✅ CORS FIX
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  // handle preflight
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
      return res.status(500).json({ error: "Missing OPENAI_API_KEY in Vercel environment variables" });
    }

    const openaiResponse = await fetch("https://api.openai.com/v1/responses", {
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

    const data = await openaiResponse.json();

    if (!openaiResponse.ok) {
      console.error("OpenAI API error:", data);
      return res.status(openaiResponse.status).json({
        error: data?.error?.message || "OpenAI API request failed"
      });
    }

    const reply =
      data.output_text ||
      data.output?.[0]?.content?.[0]?.text ||
      null;

    if (!reply) {
      console.error("Unexpected OpenAI response:", data);
      return res.status(500).json({ error: "No reply text returned from OpenAI" });
    }

    return res.status(200).json({ reply });
  } catch (error) {
    console.error("Server error:", error);
    return res.status(500).json({ error: "Server error" });
  }
}
