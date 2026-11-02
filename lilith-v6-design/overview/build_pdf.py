#!/usr/bin/env python3
"""Builds lilith-for-everyone.pdf: the plain-words overview of Lilith for non-technical readers.

Needs reportlab (``pip install reportlab``) and the DejaVu Sans fonts.  Run from anywhere:

    python3 lilith-v6-design/overview/build_pdf.py

The text below is the single source of the document.  Every claim in it is tagged by where it
sits: "Works today" = built, merged and exercised in the developer's own dogfood; "Decided" = in
the build plan, not built yet; "Later" = recorded idea, no date.  When the build moves, edit the
text here and rebuild; do not edit the PDF.  Privacy wording obeys the design's claim ceiling
(standards.html): say less than the design guarantees, never more.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "lilith-for-everyone.pdf"
FONTS = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("Sans", str(FONTS / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", str(FONTS / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans", boldItalic="Sans-Bold")

INK = colors.HexColor("#1b2430")
MUTED = colors.HexColor("#5b6675")
TEAL = colors.HexColor("#17868d")
TEAL_SOFT = colors.HexColor("#e6f4f5")
GREEN = colors.HexColor("#1f8a5b")
AMBER = colors.HexColor("#b86e00")
PURPLE = colors.HexColor("#6a54c4")
LINE = colors.HexColor("#d7dde3")
PAPER = colors.HexColor("#f6f8fa")

W, H = A4
MARGIN = 20 * mm
BODY_W = W - 2 * MARGIN


def style(name: str, **kw) -> ParagraphStyle:
    base = dict(fontName="Sans", fontSize=10.2, leading=15.2, textColor=INK, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)


BODY = style("body", spaceAfter=7)
LEAD = style("lead", fontSize=12.2, leading=18.4, spaceAfter=10, textColor=INK)
SMALL = style("small", fontSize=8.6, leading=12.4, textColor=MUTED)
H1 = style("h1", fontName="Sans-Bold", fontSize=21, leading=26, textColor=TEAL, spaceBefore=2, spaceAfter=8)
H2 = style("h2", fontName="Sans-Bold", fontSize=12.4, leading=16, textColor=INK, spaceBefore=10, spaceAfter=4)
KICK = style("kick", fontName="Sans-Bold", fontSize=8.4, leading=11, textColor=MUTED, spaceAfter=2)
CELL = style("cell", fontSize=9.2, leading=13)
CELLB = style("cellb", fontName="Sans-Bold", fontSize=9.2, leading=13)
BUL = style("bul", leftIndent=14, bulletIndent=2, spaceAfter=3.5)
QUOTE = style("quote", fontSize=10, leading=15, textColor=TEAL, leftIndent=0, spaceAfter=4)


def P(text: str, s: ParagraphStyle = BODY) -> Paragraph:
    return Paragraph(text, s)


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph(t, BUL, bulletText="•") for t in items]


def tag(label: str, color: colors.Color) -> str:
    return f'<font name="Sans-Bold" color="{color.hexval()}" size="8">{label.upper()}</font>'


WORKS = tag("Works today", GREEN)
DECIDED = tag("Decided, being built", AMBER)
LATER = tag("Later, an idea", PURPLE)


def card_table(rows: list[list], widths: list[float], header: bool = True) -> Table:
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), TEAL_SOFT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, TEAL)]
    t.setStyle(TableStyle(cmds))
    return t


def callout(text: str, accent: colors.Color = TEAL) -> Table:
    t = Table([[Paragraph(text, style("co", fontSize=9.6, leading=14.2))]], colWidths=[BODY_W])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def box(d: Drawing, x, y, w, h, label, fill, stroke, size=9, sub=None, bold=True):
    d.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=fill, strokeColor=stroke, strokeWidth=1))
    font = "Sans-Bold" if bold else "Sans"
    if sub:
        d.add(String(x + w / 2, y + h / 2 + 3, label, textAnchor="middle", fontName=font, fontSize=size, fillColor=INK))
        d.add(String(x + w / 2, y + h / 2 - 9, sub, textAnchor="middle", fontName="Sans", fontSize=7.4, fillColor=MUTED))
    else:
        d.add(String(x + w / 2, y + h / 2 - size / 3, label, textAnchor="middle", fontName=font, fontSize=size, fillColor=INK))


def arrow(d: Drawing, x1, y1, x2, y2, color=MUTED):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.4))
    # arrow head along the line
    import math

    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (2.55, -2.55):
        d.add(Line(x2, y2, x2 + 6 * math.cos(ang + da), y2 + 6 * math.sin(ang + da), strokeColor=color, strokeWidth=1.4))


def privacy_diagram() -> Drawing:
    d = Drawing(BODY_W, 150)
    d.add(Rect(0, 8, BODY_W * 0.64, 134, rx=10, ry=10, fillColor=colors.HexColor("#eef7f2"), strokeColor=GREEN, strokeWidth=1.2))
    d.add(String(10, 126, "YOUR COMPUTER", fontName="Sans-Bold", fontSize=8, fillColor=GREEN))
    box(d, 12, 66, 82, 44, "You", colors.white, LINE, 10, "type or speak")
    box(d, 118, 66, 104, 44, "Lilith", colors.white, TEAL, 10, "decides what is needed")
    box(d, 118, 18, 104, 34, "Your memory", colors.white, LINE, 8.6, "locked with your passphrase")
    arrow(d, 94, 88, 118, 88)
    arrow(d, 170, 66, 170, 52)
    # placeholder step
    box(d, 244, 66, 86, 44, "Swap details", colors.white, AMBER, 8.6, "placeholders")
    arrow(d, 222, 88, 244, 88)
    cloud_x = BODY_W * 0.64 + 26
    d.add(Rect(cloud_x, 8, BODY_W - cloud_x, 134, rx=10, ry=10, fillColor=colors.HexColor("#fbf3e6"), strokeColor=AMBER, strokeWidth=1.2))
    d.add(String(cloud_x + 10, 126, "THE INTERNET (OPTIONAL)", fontName="Sans-Bold", fontSize=8, fillColor=AMBER))
    box(d, cloud_x + 12, 66, BODY_W - cloud_x - 24, 44, "Cloud model", colors.white, AMBER, 9, "sees only what it needs")
    arrow(d, 330, 88, cloud_x + 12, 88, AMBER)
    d.add(String(cloud_x + 12, 40, "Skip this side entirely", fontName="Sans", fontSize=8, fillColor=MUTED))
    d.add(String(cloud_x + 12, 29, "by using the local model.", fontName="Sans", fontSize=8, fillColor=MUTED))
    return d


def nexus_diagram() -> Drawing:
    import math

    d = Drawing(BODY_W, 150)
    cx, cy = BODY_W / 2, 75
    spokes = [
        ("Lights", PURPLE),
        ("Heating", PURPLE),
        ("Door locks", PURPLE),
        ("Cameras", PURPLE),
        ("Your files", PURPLE),
        ("Appliances", PURPLE),
        ("Work tools", PURPLE),
        ("Car", PURPLE),
    ]
    r = 58
    for i, (name, col) in enumerate(spokes):
        a = math.radians(90 - i * 360 / len(spokes) - 22.5)
        x, y = cx + 1.55 * r * math.cos(a), cy + r * math.sin(a)
        d.add(Line(cx, cy, x, y, strokeColor=col, strokeWidth=1.1, strokeDashArray=[3, 3]))
        d.add(Rect(x - 36, y - 11, 72, 22, rx=11, ry=11, fillColor=colors.white, strokeColor=col, strokeWidth=1))
        d.add(String(x, y - 3, name, textAnchor="middle", fontName="Sans", fontSize=8.2, fillColor=INK))
    d.add(Circle(cx, cy, 36, fillColor=TEAL_SOFT, strokeColor=TEAL, strokeWidth=1.6))
    d.add(String(cx, cy + 2, "Nexus", textAnchor="middle", fontName="Sans-Bold", fontSize=11, fillColor=TEAL))
    d.add(String(cx, cy - 10, "with Lilith", textAnchor="middle", fontName="Sans", fontSize=7.6, fillColor=MUTED))
    return d


def build_story() -> list:
    s: list = []

    # ---------------- cover ----------------
    s += [Spacer(1, 38 * mm)]
    s += [P("LILITH", style("cov0", fontName="Sans-Bold", fontSize=12, leading=14, textColor=MUTED))]
    s += [P("An assistant that works for you, and keeps your life on your own computer.", style("cov1", fontName="Sans-Bold", fontSize=26, leading=33, textColor=TEAL, spaceAfter=14))]
    s += [P("A plain-words guide to what Lilith does today, what is already decided for her, and why she is built to cost less and keep more of your information private.", LEAD)]
    s += [Spacer(1, 10)]
    s += [
        card_table(
            [
                [P(WORKS, CELL), P("Built and in use by the developer today.", CELL)],
                [P(DECIDED, CELL), P("Agreed and written into the build plan. Not finished.", CELL)],
                [P(LATER, CELL), P("A real intention with no date. Described honestly, not promised.", CELL)],
            ],
            [42 * mm, BODY_W - 42 * mm],
            header=False,
        )
    ]
    s += [Spacer(1, 10)]
    s += [P("Every page marks which of these three a feature belongs to. Lilith is still being built: this guide does not describe a finished product, and it will be revised as she changes.", SMALL)]
    s += [PageBreak()]

    # ---------------- 1. what she is ----------------
    s += [P("1 · THE IDEA", KICK), P("One assistant, who actually knows your day", H1)]
    s += [
        P(
            "Most of us run our lives across a dozen apps: a calendar here, a contact list there, notes in a third place, reminders in a fourth. None of them talk to each other, and none of them know you. "
            "Lilith is one assistant that sits in front of all of it. You talk to her, by voice or by typing, the way you would talk to a capable person who works for you.",
            LEAD,
        )
    ]
    s += bullets(
        [
            "<b>She remembers, so you do not repeat yourself.</b> What you tell her is kept, and she can find it again when you ask.",
            "<b>She lives on your computer.</b> Her memory is stored there, locked with a passphrase only you know. It is not a profile on someone else's server.",
            "<b>She tells you what she can and cannot do.</b> If she cannot do something yet, she says so plainly instead of pretending.",
            "<b>You stay in charge.</b> She asks before she forgets anything, she can undo what she just did, and features that reach out to the internet stay off until you ask for them.",
        ]
    )
    s += [Spacer(1, 6)]
    s += [
        callout(
            "<b>The plain version.</b> Think of a very organised personal assistant who keeps your diary, your address book and your notes in a locked drawer in your own house, "
            "and who only phones out for help when a question is too big for her to answer alone."
        )
    ]
    s += [Spacer(1, 10)]
    s += [P("What “smart” means here", H2)]
    s += [
        P(
            "Lilith uses an AI language model to understand you and to write her answers. You can use a cloud model (you supply your own key, so you pay the provider directly, with no subscription on top) "
            "or, on a computer powerful enough, a model that runs entirely on your machine. The rest of this guide is mostly about how she avoids using the model when she does not need to, "
            "and how she protects your information when she does."
        )
    ]
    s += [PageBreak()]

    # ---------------- 2. today ----------------
    s += [P("2 · WHAT SHE DOES TODAY", KICK), P("Ask her, in your own words", H1)]
    s += [P(f"{WORKS} &nbsp; These all work now. You do not need special commands; you ask the way you would ask a person.", BODY)]
    rows = [
        [P("You can…", CELLB), P("For example you might say", CELLB), P("What happens", CELLB)],
        [P("<b>Keep a calendar</b>", CELL), P("“Add a dentist visit tomorrow at 3pm.” “Move it to Friday.” “Cancel it.”", CELL), P("She makes the change in her own calendar and tells you exactly what she did. “Undo” puts it back.", CELL)],
        [P("<b>See your Google calendar and contacts</b>", CELL), P("“What is on this afternoon?” “Who is Maria?”", CELL), P("She keeps a private copy, read-only. She never changes anything in your Google account.", CELL)],
        [P("<b>Take notes</b>", CELL), P("“Note that the boiler service is due in March.”", CELL), P("Saved, and findable later by asking. Mistakes can be undone.", CELL)],
        [P("<b>Set reminders and timers</b>", CELL), P("“Remind me at 5 to ring the bank.” “Timer for 10 minutes.”", CELL), P("She tells you in the chat and as a desktop notification while she is running. If a time is vague (“tonight”), she says what she decided, or asks.", CELL)],
        [P("<b>Check the weather</b>", CELL), P("“Turn on weather.” Then “What is the weather tomorrow?”", CELL), P("Off until you say so. She asks a weather service about the place you mean, and nothing else.", CELL)],
        [P("<b>Do sums and tell the time</b>", CELL), P("“What is 18% of 240?” “What time is it in Sydney?”", CELL), P("Worked out on your computer, exactly, with no model needed.", CELL)],
        [P("<b>Help with writing</b>", CELL), P("“Draft a polite reply declining this invitation.”", CELL), P("This is where the language model does its job: drafting, summarising, rewording, translating.", CELL)],
        [P("<b>Remember and forget on your terms</b>", CELL), P("“What did I say about the boiler?” “Forget that.”", CELL), P("She finds it. To forget, she asks, and nothing is erased until you say yes.", CELL)],
        [P("<b>Use your voice</b>", CELL), P("Talk to her; she talks back.", CELL), P("Speech is turned to text on your own computer, so your voice recording is not sent to a cloud service.", CELL)],
    ]
    s += [card_table(rows, [34 * mm, 58 * mm, BODY_W - 92 * mm])]
    s += [Spacer(1, 8)]
    s += [P("Also working: moving to a new computer from a backup, subscribing a calendar app on your own network to her calendar (read-only), and a quiet icon in your system tray.", SMALL)]
    s += [PageBreak()]

    # ---------------- 3. next ----------------
    s += [P("3 · WHAT IS ALREADY DECIDED", KICK), P("What she is being built into next", H1)]
    s += [P(f"{DECIDED} &nbsp; These are agreed in the build plan. They are not finished, and the order may change.", BODY)]
    rows = [
        [P("Coming", CELLB), P("What it means for you", CELLB)],
        [P("<b>Opening your apps</b>", CELL), P("“Open my spreadsheet.” You decide which apps she may open by dragging their icons into a list. Anything not on the list, she cannot open. You can remove one at any time.", CELL)],
        [P("<b>Weather for any place you name</b>", CELL), P("“What is the weather at the Clovis job?” You save places once; you choose metric or imperial in plain words.", CELL)],
        [P("<b>Searching the web</b>", CELL), P("She will ask before she goes online, show what she found, and summarise it in a separate, protected step so a malicious web page cannot give her orders. The search provider is not chosen yet.", CELL)],
        [P("<b>A first conversation that teaches her about you</b>", CELL), P("A few questions, one at a time and never nagging, so she learns when your evening starts and how you like things said.", CELL)],
        [P("<b>“What can you do?” that is always true</b>", CELL), P("A list of her abilities that is built from what she can really do, shown in her settings and available by asking.", CELL)],
        [P("<b>“What do you know about me?”</b>", CELL), P("A page showing every fact she has stored about you, where it came from, and a button to remove it.", CELL)],
        [P("<b>A visible Undo button</b>", CELL), P("Today you undo by saying “undo”. A button will sit in the chat as well.", CELL)],
        [P("<b>Picking up where you left off</b>", CELL), P("After you restart her, the last conversation will reappear.", CELL)],
    ]
    s += [card_table(rows, [50 * mm, BODY_W - 50 * mm])]
    s += [Spacer(1, 10)]
    s += [P(f"{LATER} &nbsp; Relationship cards", H2)]
    s += [
        P(
            "Before a conversation with someone, a short card of what you have already stored about them: the last time you spoke, what you promised, a note about their family. "
            "Only facts you gave her, with their source, and nothing guessed. Recorded as an intention; not scheduled."
        )
    ]
    s += [PageBreak()]

    # ---------------- 4. cost ----------------
    s += [P("4 · WHY SHE COSTS LESS", KICK), P("She does not ask the expensive brain unless she has to", H1)]
    s += [
        P(
            "AI language models charge by the amount of text they read and write, in small units called tokens. A token is roughly three-quarters of a word. "
            "Every message, every reminder of earlier context, every long answer adds to the bill. Many assistants send a lot of text on every turn, "
            "and ask the model to handle even trivial jobs. Lilith is designed around the opposite habit.",
            LEAD,
        )
    ]
    s += [P("Six habits that keep the bill small", H2)]
    habits = [
        ("1", "Simple jobs never reach the model", "The time, sums, notes, reminders, calendar changes and the weather are handled by Lilith herself, and she writes the answer sentence in her own code. No model is asked, so no tokens are spent."),
        ("2", "Short answers by design", "In everyday conversation she is limited to short replies, around 100 tokens, and she hands the model no more than about 1,200 tokens of background. These are targets she is being tested against, not guarantees."),
        ("3", "She sends only what is relevant", "Instead of replaying your whole history, she assembles a small, fresh brief for the question at hand: a few facts about you, and only the calendar or contact details that this question needs."),
        ("4", "Her working results stay home", "What she looks up for you (your calendar entries, your contacts) is shown to you and is not sent back to the model afterwards. That protects your privacy and avoids paying for the same text again."),
        ("5", "No extra model to decide what to do", "Working out what you asked for is done by fixed rules on your computer, not by a second paid model call."),
        ("6", "Reuse what has not changed", "The standing instructions that are identical every time are marked so the provider can reuse them at a lower price, rather than reading them fresh each turn."),
    ]
    rows = [[P(f"<b>{n}</b>", style("n", fontName="Sans-Bold", fontSize=15, leading=18, textColor=TEAL)), P(f"<b>{t}</b><br/>{b}", CELL)] for n, t, b in habits]
    s += [card_table(rows, [11 * mm, BODY_W - 11 * mm], header=False)]
    s += [Spacer(1, 8)]
    s += [
        callout(
            "<b>You can spend nothing per message.</b> On a computer that is powerful enough, Lilith can use a language model that runs entirely on your machine. "
            "There is then no per-word charge and nothing leaves your computer. She offers this at setup and asks before installing anything."
        )
    ]
    s += [Spacer(1, 6)]
    s += [
        callout(
            "<b>What has not been measured yet.</b> We have not published a figure for how much cheaper this is than another assistant. The habits above are real design decisions and most are built; "
            "the savings are the aim, and a spending tracker that shows you each day's cost is planned for later.",
            AMBER,
        )
    ]
    s += [PageBreak()]

    # ---------------- 5. security ----------------
    s += [P("5 · WHY YOUR INFORMATION IS SAFER", KICK), P("Your life stays at home. The internet is the exception.", H1)]
    s += [P("Where your information goes", H2)]
    s += [privacy_diagram()]
    s += [Spacer(1, 4)]
    s += [P("Anything that does leave your computer goes through the middle step first. If you choose the local model, nothing leaves at all.", SMALL)]
    s += [Spacer(1, 6)]
    rows = [
        [P("What Lilith does", CELLB), P("In plain terms", CELLB)],
        [P("<b>Locks her memory</b>", CELL), P("Her six databases (calendar, contacts, memory, conversation and so on) are encrypted on your disk. A stolen laptop or a copied folder is unreadable without your passphrase.", CELL)],
        [P("<b>Keeps the key under your control</b>", CELL), P("Your passphrase is at least 12 characters. You choose whether your computer's keychain unlocks her automatically, or whether you type it each time. There is no back door and no recovery: if it is lost, nobody can recover your data, including you.", CELL)],
        [P("<b>Swaps personal details before the cloud sees them</b>", CELL), P("Before text goes to a cloud model, names, email addresses and phone numbers are replaced with placeholders such as “contact 1”, and swapped back when the answer returns. Email addresses and phone numbers are reliably caught; names are caught on a best-effort basis.", CELL)],
        [P("<b>Keeps her lookups off the cloud</b>", CELL), P("Your calendar and contact details she retrieves are shown to you, not handed back to the model.", CELL)],
        [P("<b>Reads Google, never writes to it</b>", CELL), P("Her Google connection is read-only by design. Disconnecting removes her permission.", CELL)],
        [P("<b>Asks before reaching out</b>", CELL), P("Weather, and later web search, stay off until you ask for them in your own words.", CELL)],
        [P("<b>Asks before forgetting, and can undo</b>", CELL), P("Nothing is erased until you say yes. Her changes are recorded so they can be reversed.", CELL)],
        [P("<b>Does not copy your files</b>", CELL), P("She reads your documents where they are. If you uninstall her, your own files are untouched.", CELL)],
        [P("<b>Locks the doors on add-ons</b>", CELL), P("Extra skills are added only by a deliberate command, not by clicking a button by accident.", CELL)],
    ]
    s += [card_table(rows, [48 * mm, BODY_W - 48 * mm])]
    s += [PageBreak()]

    # ---------------- 6. honest ----------------
    s += [P("6 · THE HONEST PART", KICK), P("What she does not promise", H1)]
    s += [P("A privacy claim you cannot check is worth little. These are the limits, stated up front.", LEAD)]
    s += bullets(
        [
            "<b>A cloud model still sees your question.</b> Placeholders cover names, emails and phone numbers. They do <b>not</b> cover amounts of money, shop names, health or relationship details, free-text notes, or addresses outside your calendar. Those are sent as written when a cloud model is used. Choose the local model if that matters to you.",
            "<b>Name detection is not perfect.</b> Unusual names, nicknames and names inside quoted text can be missed.",
            "<b>Her protection is strongest against loss and theft, not against another program on your own account.</b> A program that is already running as you may be able to read what you can read. On Linux, with automatic unlock, any program you run could read the saved passphrase. Typing the passphrase each time avoids that.",
            "<b>Reminders fire only while she is running.</b> If she is closed when a reminder is due, she tells you once, with its original time, the next time she opens.",
            "<b>Backups are your job.</b> Her memory lives on your computer. Uninstalling her, or deleting her folder, deletes it. She nudges you to make a backup; the backup and your passphrase are the only way back.",
            "<b>She is not finished.</b> She has so far been used only by her builder, on a Linux computer and a MacBook. She has not yet been tested by the public.",
        ]
    )
    s += [Spacer(1, 8)]
    s += [P("Why you can hold this to account", H2)]
    s += [
        P(
            "Every change she makes is written to a private activity log on your computer. When something goes wrong, the answer is in that log, not in anyone's memory. "
            "The full design, every decision and every correction is published on the design site, so a claim made here can be checked against the rules the build must obey. "
            "Where the public wording and the design disagree, the design is stricter: this guide is allowed to say less than the design promises, never more."
        )
    ]
    s += [PageBreak()]

    # ---------------- 7. nexus ----------------
    s += [P("7 · BEYOND ONE ASSISTANT", KICK), P("Nexus: one coordinator for your whole setup", H1)]
    s += [P(f"{LATER} &nbsp; This page is a plan, not a product. Nexus is not built, and nothing here is promised for a date.", BODY)]
    s += [
        P(
            "Lilith on her own is a capable assistant for your calendar, your people, your notes and your day. Nexus is the next idea: let her connect to the other tools in your life, "
            "so that they stop being a pile of separate things and become one working system.",
            LEAD,
        )
    ]
    s += [nexus_diagram()]
    s += [P("A smart home, not a pile of smart devices", H2)]
    s += [
        P(
            "Today a house with smart bulbs, a thermostat, door locks and cameras is usually four apps and four accounts, each clever and none aware of the others. "
            "With a coordinator, you say “I’m heading to bed” once. The lights dim, the doors lock, the heating drops, and the morning reminder is set, because something knows all of them and knows you."
        )
    ]
    s += [P("How it would work, in plain terms", H2)]
    s += bullets(
        [
            "Each device or service keeps doing its own job. Nexus does not replace your thermostat. It <b>uses</b> it, on your behalf.",
            "A shared standard for connecting tools (MCP, the Model Context Protocol) is how outside tools would plug in. One connection method means a new tool is a new plug, not a new project.",
            "Lilith stays the face you talk to. Nexus is what lets what you say reach the right tool.",
            "The same house rules apply to every new tool: it asks permission first, it is listed so you can see and remove it, and what it returns is treated as untrusted until checked.",
        ]
    )
    s += [Spacer(1, 6)]
    s += [
        callout(
            "<b>Why it is not built yet.</b> A single assistant that holds your private data, reads outside content and can act in the world is exactly the combination that security researchers warn about. "
            "The design deliberately learns to keep your information safe on one computer first, and treats the connected version as its own careful design step.",
            PURPLE,
        )
    ]
    s += [Spacer(1, 6)]
    s += [P("Also on the longer list, each its own future decision: Lilith reaching out to you when something needs attention (instead of only answering when asked); a running cost display; the same Lilith across several of your computers.", SMALL)]

    return s


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 7.8)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(MARGIN, 11 * mm, "Lilith · a plain-words guide · describes the build as of November 2026")
        canvas.drawRightString(W - MARGIN, 11 * mm, f"{doc.page}")
        canvas.setStrokeColor(LINE)
        canvas.line(MARGIN, 15 * mm, W - MARGIN, 15 * mm)
    else:
        canvas.setFillColor(TEAL)
        canvas.rect(0, H - 9 * mm, W, 9 * mm, stroke=0, fill=1)
    canvas.restoreState()


def main() -> None:
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
        title="Lilith: a plain-words guide",
        author="Squirrelthug",
        subject="What Lilith does today, what is decided, and why she costs less and keeps your information safer",
    )
    frame = Frame(MARGIN, 22 * mm, BODY_W, H - 40 * mm, id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])
    doc.build(build_story())
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
