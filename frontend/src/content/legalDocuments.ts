export type LegalDocumentKey = 'privacy' | 'terms' | 'disclaimer'

export interface LegalSection {
  heading: string
  paragraphs?: string[]
  bullets?: string[]
}

export interface LegalDocument {
  title: string
  intro: string
  sections: LegalSection[]
}

export const LEGAL_DOCUMENTS: Record<LegalDocumentKey, LegalDocument> = {
  privacy: {
    title: 'Privacy Policy',
    intro:
      "StudyAssistant AI is built and run by Alvin Kipng'eno Langat, an independent developer based in Kenya. This page explains what the app collects, who it passes your content to, and how to get it deleted. I've kept it short on purpose.",
    sections: [
      {
        heading: 'What I collect',
        bullets: [
          'Your account: your email address and a password, which is stored only as a one-way hash, never in plain text.',
          'Your profile, if you fill it in: name, academic level, institution, programme, subjects and goals.',
          'Your study content: subjects and topics, the documents you upload (PDF, TXT or MD) and the text pulled out of them, tutor chats, quizzes and your answers, flashcards and review progress, and planner goals, sessions and deadlines.',
          'Security data: failed sign-in counts, short-lived verification codes (stored hashed, expiring after 10 minutes), and server logs that can include your email address when you sign in or request a code. Your IP address is used briefly to limit repeated sign-in attempts, and my hosting providers keep standard request logs.',
        ],
      },
      {
        heading: 'How I use it',
        paragraphs: [
          "Only to run the features you ask for: signing you in, answering questions about your notes, generating quizzes and flashcards, suggesting a study plan and showing your progress. I don't sell your data and there are no ads.",
        ],
      },
      {
        heading: 'Who else sees your content',
        paragraphs: ['The app relies on a few outside services, so some of your content leaves my server:'],
        bullets: [
          'AI replies, quizzes, flashcards and plan suggestions: your message, recent chat history, subject details and the few note excerpts relevant to your question are sent to Google (Gemini), or to Groq if Gemini is unavailable. Google\'s terms for its free Gemini tier allow it to review and use prompts to improve its products, so please keep sensitive material out of your notes and chats.',
          'Storage: your data lives in a Neon database and uploaded files are kept in Supabase Storage. The website itself is served by Vercel and the API runs on a separate hosting provider.',
          "Email: verification and password codes are sent through Gmail's SMTP service.",
          "Searching your notes by meaning uses a small model that runs on my own server, so that step doesn't send your text to anyone.",
        ],
      },
      {
        heading: 'Cookies and local storage',
        paragraphs: [
          "There are no advertising or analytics cookies. Your browser's local storage holds your sign-in token, your theme choices and whether the side menu is open. Signing out clears the token.",
        ],
      },
      {
        heading: 'How long I keep it',
        paragraphs: [
          "Until you delete it. Chats, documents, quizzes and the rest stay in your account until you remove them or delete the account. Verification codes expire within minutes. If an admin acts on an account, a record of that action, including the email involved, is kept in an audit log for security.",
        ],
      },
      {
        heading: 'Deleting your data',
        bullets: [
          'You can delete individual documents, conversations, quizzes and flashcard decks at any time. Deleting a document also removes its stored file.',
          'To delete everything, go to Profile and choose Delete Account. A code is emailed to confirm it, and your account and its content are then permanently removed from the database.',
          'Delete your documents first if you want the original files gone too. If you delete the whole account without doing that, email me and I will clear the remaining files from storage.',
        ],
      },
      {
        heading: 'Your rights',
        paragraphs: [
          "I'm based in Kenya, so the Kenya Data Protection Act, 2019 applies to how I handle your data. You can ask me for a copy of it, ask me to correct it, or ask me to delete it. Write to me from the email address on your account.",
        ],
      },
      {
        heading: 'Keeping it safe',
        paragraphs: [
          "Passwords are hashed, sign-in attempts are rate limited, accounts lock after repeated failures and traffic is encrypted over HTTPS. The admin dashboard shows account details and usage counts, not your notes or chats, and I don't browse user content. No online service is perfectly secure, so please don't upload anything highly sensitive such as ID documents or medical and financial records.",
        ],
      },
      {
        heading: 'Younger users',
        paragraphs: ["If you're under 18, please make sure a parent or guardian is happy for you to use StudyAssistant AI."],
      },
      {
        heading: 'Changes',
        paragraphs: ["If this policy changes in a way that matters, I'll update the date at the top of the page."],
      },
    ],
  },
  terms: {
    title: 'Terms of Use',
    intro:
      "By creating an account or using StudyAssistant AI you agree to these terms. They're short, so please read them.",
    sections: [
      {
        heading: 'Who runs this',
        paragraphs: ["StudyAssistant AI is an independent project built and owned by Alvin Kipng'eno Langat (\"I\" or \"me\")."],
      },
      {
        heading: 'Your account',
        bullets: [
          'Use an email address you control and verify it with the code we send.',
          'Keep your password private. You are responsible for what happens under your account.',
          "If you're under 18, make sure a parent or guardian is happy for you to use the app.",
          'To protect accounts, sign-ins are rate limited and an account is locked for a while after repeated failed attempts.',
        ],
      },
      {
        heading: 'Your content',
        paragraphs: [
          "Your notes, documents, chats and anything else you add stay yours. You give me permission to store and process them only to run the app for you, including sending the relevant parts to the AI providers named in the Privacy Policy.",
          "Only upload material you have the right to use, such as your own notes or study material you're allowed to copy. Please don't upload whole copyrighted books or confidential information that isn't yours.",
        ],
      },
      {
        heading: 'Using it fairly',
        paragraphs: ["Please don't:"],
        bullets: [
          'break the law, or upload malware or harmful, abusive or explicit content;',
          "try to get into other people's accounts or data, probe the service for weaknesses, or overload it;",
          'get around rate limits, lockouts or usage limits, or scrape and resell the service;',
          "use the AI to cheat where your school, college or exam body forbids it. Use it to learn, and follow your institution's academic integrity rules.",
        ],
      },
      {
        heading: 'AI features',
        paragraphs: [
          "Tutor replies, quizzes, flashcards and study plans are generated by AI and can be wrong. Check anything important against your course materials. The AI Disclaimer page covers this in more detail.",
        ],
      },
      {
        heading: 'Availability',
        paragraphs: [
          "StudyAssistant AI runs on small-scale hosting and third-party AI services. It may be slow, hit usage limits, change, or go down, and I can't promise it will always be available. Keep your own copies of anything you can't afford to lose.",
        ],
      },
      {
        heading: 'Ending your account',
        paragraphs: [
          'You can delete your account at any time from your Profile page. I may suspend or remove accounts that break these terms or put the service or other users at risk.',
        ],
      },
      {
        heading: 'Liability',
        paragraphs: [
          "The service is provided as it is. As far as the law allows, I'm not responsible for lost data, missed deadlines, exam results or other losses from using it. Nothing here limits any rights you have under Kenyan law.",
        ],
      },
      {
        heading: 'Governing law and changes',
        paragraphs: [
          'These terms are governed by the laws of Kenya. If I change them, I will update the date at the top of the page, and carrying on using the app after that means you accept the new version.',
        ],
      },
    ],
  },
  disclaimer: {
    title: 'AI Disclaimer',
    intro:
      "StudyAssistant AI uses AI to help you study. It's a helper, not a teacher, and it doesn't replace your own judgement or your course materials.",
    sections: [
      {
        heading: 'AI can be wrong',
        paragraphs: [
          "The tutor, quizzes, flashcards and study-plan suggestions come from large language models (currently Google Gemini, with Groq as a backup). They can sound confident and still be wrong, out of date or incomplete. Quiz answer keys and explanations are generated too, so an answer marked correct can occasionally be incorrect.",
        ],
      },
      {
        heading: 'About your notes',
        paragraphs: [
          "When you've uploaded notes, the tutor tries to use the relevant parts and name the document it used. It can still miss something, misread tables or formulas, or fall back on general knowledge. Scanned PDFs without selectable text can't be read at all.",
        ],
      },
      {
        heading: 'Not professional advice',
        paragraphs: [
          'Nothing here replaces your lecturer, your textbook or your official syllabus, or legal, medical, financial or other professional advice.',
        ],
      },
      {
        heading: 'Scores and analytics',
        paragraphs: [
          "Practice scores and progress charts are for self-study and don't predict exam results. Short-answer questions are marked by comparing your text with the expected answer, so a correct answer worded differently may be marked wrong.",
        ],
      },
      {
        heading: 'Planner and reminders',
        paragraphs: [
          "Study-plan suggestions are general. Always check official deadlines yourself. Reminders appear when you use the app and are not guaranteed alerts.",
        ],
      },
      {
        heading: 'Academic integrity',
        paragraphs: [
          "Follow your institution's rules on using AI. You are responsible for how you use anything the app produces in assessed work.",
        ],
      },
      {
        heading: 'Sensitive information',
        paragraphs: [
          'Parts of your chats and notes are sent to AI providers to produce answers. Please keep personal, medical, financial and confidential details out of them.',
        ],
      },
    ],
  },
}