export default async function handler(req, res) {
  // CORS
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
    const userMessage = (message || "").trim();
    const language = lang || "en";
    const lower = userMessage.toLowerCase();

    const CONTACT = {
      name: "MS Cosmetics by Mobina Shahri",
      email: "Mobina.shahri@web.de",
      instagram: "ms_cosmetics.de",
      languages: "Persian, German, English",
      appointments: "By appointment only"
    };

    // Hardcoded safe replies for sensitive factual contact/booking questions
    if (
      language === "de" &&
      (lower.includes("termin") ||
        lower.includes("buchen") ||
        lower.includes("buchung") ||
        lower.includes("kontakt") ||
        lower.includes("instagram") ||
        lower.includes("e-mail") ||
        lower.includes("email"))
    ) {
      return res.status(200).json({
        reply:
          `Gerne. Termine sind nur nach Vereinbarung möglich.\n\n` +
          `Sie können das Studio direkt kontaktieren:\n` +
          `E-Mail: ${CONTACT.email}\n` +
          `Instagram: ${CONTACT.instagram}`
      });
    }

    if (
      language === "en" &&
      (lower.includes("book") ||
        lower.includes("booking") ||
        lower.includes("appointment") ||
        lower.includes("contact") ||
        lower.includes("instagram") ||
        lower.includes("email"))
    ) {
      return res.status(200).json({
        reply:
          `Appointments are by appointment only.\n\n` +
          `You can contact the studio directly:\n` +
          `Email: ${CONTACT.email}\n` +
          `Instagram: ${CONTACT.instagram}`
      });
    }

    if (
      language === "fa" &&
      (lower.includes("رزرو") ||
        lower.includes("وقت") ||
        lower.includes("تماس") ||
        lower.includes("اینستاگرام") ||
        lower.includes("ایمیل"))
    ) {
      return res.status(200).json({
        reply:
          `وقت‌ها فقط با تعیین وقت قبلی انجام می‌شوند.\n\n` +
          `می‌توانید مستقیماً با مجموعه تماس بگیرید:\n` +
          `ایمیل: ${CONTACT.email}\n` +
          `اینستاگرام: ${CONTACT.instagram}`
      });
    }

    const systemPrompts = {
      de: `Du bist der Concierge für MS Cosmetics by Mobina Shahri in Düsseldorf.
Antworte immer auf Deutsch.

WICHTIG:
Verwende nur die folgenden bekannten Fakten.
Erfinde niemals Telefonnummern, E-Mail-Adressen, Preise, Zeiten oder andere Details.
Wenn Informationen nicht sicher bekannt sind, sage klar, dass die Person das Studio direkt kontaktieren soll.
Verwende nur diese Kontaktdaten:

- Name: MS Cosmetics by Mobina Shahri
- E-Mail: Mobina.shahri@web.de
- Instagram: ms_cosmetics.de
- Sprachen: Persisch, Deutsch, Englisch
- Termine: nur nach Vereinbarung

Weitere bekannte Fakten:
- Über 18 Jahre professionelle Erfahrung in Nail, Hair und Skin Care
- Über 800 ausgebildete Schüler:innen im Iran
- National Nail Instructor – Kinetics
- National Nail Instructor – Trosani GmbH
- Training für persischsprachige Beauty-Professionals in Europa ist möglich
- Aquafacial – SHR, Deutschland (Juli 2024)
- NiSV Akademie Ultraschall & elektromagnetische Felder, Deutschland (April 2023)
- Eyelash Extension Course – Iran (August 2019)
- Teilnahme an der International Nail Competition League in Rom, Italien (Juni 2019)
- Kinetics Competition Training in Riga, Lettland (April 2019)
- National Educator & Nail Extension Expert in Riga, Lettland (2017–2018)
- March 2024: registrierte Unterrichtslizenz in Deutschland und Beginn spezialisierter Nail-Schulungen für persischsprachige Menschen in Europa

Wenn jemand fragt, wie man einen Termin bucht, antworte mit den exakten Kontaktdaten oben.
Erfinde keine alternativen Telefonnummern oder E-Mails.
Wenn nach Preisen oder genauen Zeiten gefragt wird und diese nicht sicher bekannt sind, sage höflich, dass die Person das Studio direkt kontaktieren soll.
Halte Antworten höflich, klar und eher kurz.`,

      en: `You are the concierge for MS Cosmetics by Mobina Shahri in Düsseldorf.
Always answer in English.

IMPORTANT:
Use only the known facts below.
Never invent phone numbers, email addresses, prices, schedules, or business details.
If something is not explicitly known, clearly tell the visitor to contact the studio directly.
Use only these contact details:

- Name: MS Cosmetics by Mobina Shahri
- Email: Mobina.shahri@web.de
- Instagram: ms_cosmetics.de
- Languages: Persian, German, English
- Appointments: by appointment only

Other known facts:
- Over 18 years of professional experience in nail, hair, and skin care
- Over 800 students trained in Iran
- National Nail Instructor – Kinetics
- National Nail Instructor – Trosani GmbH
- Training is available for Persian-speaking beauty professionals in Europe
- Aquafacial – SHR, Germany (July 2024)
- NiSV Academy Ultrasound & Electromagnetic Fields, Germany (April 2023)
- Eyelash Extension Course – Iran (August 2019)
- International Nail Competition League, Rome, Italy (June 2019)
- Kinetics Competition Training, Riga, Latvia (April 2019)
- National Educator & Nail Extension Expert, Riga, Latvia (2017–2018)
- March 2024: registered teaching license in Germany and started specialized nail training for Persian-speaking residents in Europe

If someone asks how to book an appointment, reply with the exact contact details above.
Do not invent alternative phone numbers or emails.
If the user asks for prices or exact schedules not explicitly known, politely tell them to contact the studio directly.
Keep replies polite, clear, and fairly short.`,

      fa: `تو کانسیرج MS Cosmetics by Mobina Shahri در دوسلدورف هستی.
همیشه به فارسی پاسخ بده.

مهم:
فقط از اطلاعات قطعی زیر استفاده کن.
هرگز شماره تلفن، ایمیل، قیمت، زمان یا جزئیات دیگر را از خودت نساز.
اگر چیزی دقیقاً مشخص نیست، واضح بگو که کاربر باید مستقیماً با مجموعه تماس بگیرد.
فقط از این اطلاعات تماس استفاده کن:

- نام: MS Cosmetics by Mobina Shahri
- Instagram: ms_cosmetics.de
- ایمیل: Mobina.shahri@web.de
- زبان‌ها: فارسی، آلمانی، انگلیسی
- وقت‌ها: فقط با تعیین وقت قبلی

اطلاعات قطعی دیگر:
- بیش از ۱۸ سال سابقه حرفه‌ای در ناخن، مو و مراقبت از پوست
- آموزش بیش از ۸۰۰ هنرجو در ایران
- National Nail Instructor – Kinetics
- National Nail Instructor – Trosani GmbH
- آموزش برای فارسی‌زبانان فعال در حوزه زیبایی در اروپا ارائه می‌شود
- Aquafacial – SHR، آلمان (جولای ۲۰۲۴)
- NiSV Academy Ultrasound & Electromagnetic Fields، آلمان (آوریل ۲۰۲۳)
- دوره اکستنشن مژه – ایران (آگوست ۲۰۱۹)
- مسابقه بین‌المللی ناخن در رم، ایتالیا (ژوئن ۲۰۱۹)
- Kinetics Competition Training در ریگا، لتونی (آوریل ۲۰۱۹)
- National Educator & Nail Extension Expert در ریگا، لتونی (۲۰۱۷ تا ۲۰۱۸)
- مارس ۲۰۲۴: ثبت مجوز تدریس در آلمان و آغاز آموزش تخصصی ناخن برای فارسی‌زبانان ساکن اروپا

اگر کاربر پرسید چگونه وقت بگیرد، فقط با اطلاعات تماس دقیق بالا پاسخ بده.
هیچ شماره تلفن یا ایمیل دیگری نساز.
اگر درباره قیمت یا زمان دقیق سوال شد و اطلاعات قطعی وجود نداشت، محترمانه بگو که بهتر است مستقیماً با مجموعه تماس بگیرند.
پاسخ‌ها را مودبانه، روشن و نسبتاً کوتاه نگه دار.`
    };

    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({ error: "Missing OPENAI_API_KEY" });
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
            content: systemPrompts[language] || systemPrompts.en
          },
          {
            role: "user",
            content: `User question: ${userMessage}

Known contact details:
Email: ${CONTACT.email}
Instagram: ${CONTACT.instagram}`
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
      return res.status(500).json({ error: "No reply text returned from AI" });
    }

    return res.status(200).json({ reply });
  } catch (error) {
    console.error("Server error:", error);
    return res.status(500).json({ error: "Server error" });
  }
}
