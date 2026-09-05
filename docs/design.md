# Design Specification — The Lenny Growth Assistant

## 1. Design principles

The interface should feel like a focused research workspace rather than a generic chatbot.

Principles:

- Evidence first.
- Minimal cognitive load.
- Clear distinction between answer and source.
- Persistent conversation context.
- Artifact output treated as a first-class result.
- Fast feedback during retrieval and generation.
- Responsive behavior without hiding essential controls.

## 2. Primary desktop layout

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Lenny Growth Assistant                         Model: Ollama ▼     │
├───────────────┬─────────────────────────────────┬───────────────────┤
│               │                                 │                   │
│  Sessions     │           Chat Pane             │ Artifact Preview  │
│               │                                 │                   │
│  + New Chat   │  User question                 │  [Markdown] [HTML]│
│               │                                 │                   │
│  Growth Q&A   │  Assistant answer               │  Rendered output  │
│  Retention    │  [sources]                      │                   │
│  PM strategy  │                                 │                   │
│               │  ─────────────────────────────  │                   │
│               │  Ask about product/growth...   │                   │
└───────────────┴─────────────────────────────────┴───────────────────┘
```

## 3. Main regions

### Session sidebar

Purpose:

- Create a session.
- Switch conversations.
- Display recent titles.

Components:

- New Chat button.
- Session list.
- Active-session indicator.
- Optional search/filter.

### Chat pane

Contains:

1. Header.
2. Conversation history.
3. Streaming status.
4. Composer.
5. Mode/provider controls.

### Artifact pane

Contains:

- Artifact title.
- Artifact type badge.
- Preview.
- Collapse button.
- Optional raw/source toggle.

The pane should be collapsible to give the chat more space.

## 4. Visual hierarchy

Priority order:

1. User's current question.
2. Assistant's answer.
3. Source attribution.
4. Actionable recommendations.
5. Artifact output.
6. Secondary metadata.

Avoid overwhelming the answer with technical retrieval scores. Scores may be shown in an expandable source detail view.

## 5. Chat message design

### User message

Use a visually distinct but compact bubble/card.

Show:

- User content.
- Timestamp if useful.

### Assistant message

Show:

- Streaming text.
- Markdown formatting.
- Source references.
- Optional "retrieved N sources" metadata.
- Artifact indicator when an artifact exists.

### Source card

Example:

```text
Brian Balfour
Retention Strategy
────────────────────────────
Relevant transcript excerpt
Episode / topic metadata

View source →
```

The source card should be clickable or expandable.

## 6. Composer

The composer should include:

```text
┌──────────────────────────────────────────────┐
│ Ask about product, growth, retention...      │
│                                              │
│ [Default] [Ship 30]                [Send →] │
└──────────────────────────────────────────────┘
```

Optional controls:

- Provider selector.
- Temperature/settings menu for advanced users.

The primary send action should remain obvious.

## 7. Provider selector

Example:

```text
Model
[ Ollama · llama3.2:3b ▼ ]
```

Provider status can be indicated by:

- Ready
- Connecting
- Unavailable

Do not imply that a provider is available solely because it is selected; health state should determine availability.

## 8. Retrieval state

While retrieval is happening:

```text
Searching transcript knowledge...
✓ Found 5 relevant passages
Generating grounded answer...
```

This provides feedback before tokens appear.

## 9. Empty state

Initial empty state:

```text
Lenny Growth Assistant

Turn podcast knowledge into practical product and growth decisions.

Try:
• How should I think about retention?
• What makes a growth loop work?
• What advice do guests give about product-market fit?

[ Start asking ]
```

## 10. Evidence-gap state

When retrieval does not meet the threshold:

```text
I don't have sufficient information in Lenny's
podcast archive to answer this reliably.

Try asking about a product or growth topic covered
by the transcript archive.
```

This should be calm and informative, not styled like a system failure.

## 11. Ship 30 mode

When selected, show a clear mode indicator:

```text
Ship 30 for 30
~1,250 words · Source grounded
```

The generated result should emphasize:

- Headline
- Hook
- H2/H3 structure
- Short paragraphs
- Bold anchors
- Practical framework
- Final checklist

## 12. Artifact pane behavior

### Closed

Chat uses full width.

### Open

Desktop layout becomes approximately:

```text
Chat:     60–65%
Artifact: 35–40%
```

The exact ratio should be responsive to viewport size.

### Mobile

Use a tab or drawer:

```text
[Chat] [Artifact]
```

The artifact pane should not force a permanent two-column layout on narrow screens.

## 13. Responsive breakpoints

Suggested behavior:

### Desktop

Two/three-region workspace.

### Tablet

Sidebar can collapse; chat and artifact remain manageable.

### Mobile

Single-column navigation:

```text
Header
Chat
Composer
Artifact drawer/tab
```

Keep the composer sticky near the bottom while respecting mobile browser viewport behavior.

## 14. Artifact security UX

The artifact header should visibly communicate:

```text
Sandboxed Preview
```

This builds user trust without exposing implementation details.

If content is blocked or malformed:

```text
Preview unavailable

The artifact could not be safely rendered.
```

Do not silently execute unsafe content.

## 15. Loading and error states

### Retrieval loading

Use a small status indicator.

### LLM loading

Use streaming cursor/typing indicator.

### Network error

Provide:

```text
Unable to reach the assistant.

Check the backend/provider status and try again.
```

### Provider unavailable

Offer the available provider if configured.

## 16. Accessibility

Requirements:

- Keyboard-accessible controls.
- Visible focus states.
- Semantic buttons.
- Proper form labels.
- Sufficient text contrast.
- `aria-live` for streaming status where appropriate.
- Artifact iframe has a meaningful title.
- Do not rely on color alone to communicate provider status.

## 17. Component map

```text
App
├── AppShell
│   ├── SessionSidebar
│   ├── ChatPane
│   │   ├── ChatHeader
│   │   ├── MessageList
│   │   │   └── MessageItem
│   │   ├── RetrievalStatus
│   │   └── ChatComposer
│   └── ArtifactPane
│       ├── ArtifactHeader
│       ├── MarkdownViewer
│       └── SandboxedIframe
```

## 18. State model

```text
idle
  │
  ▼
submitting
  │
  ▼
retrieving
  │
  ├── no evidence ──► evidence_gap
  │
  ▼
generating
  │
  ▼
complete
  │
  └── artifact detected ──► artifact_ready
```

Error transitions can occur from any network/model state:

```text
retrieving/generating ──► error
```

## 19. Design acceptance criteria

- A first-time user can identify where to ask a question immediately.
- Provider selection is visible but not distracting.
- Retrieval progress is understandable.
- Sources are visually separated from generated prose.
- Artifact output can be opened without leaving the conversation.
- Mobile users can access both chat and artifact views.
- Keyboard users can operate core actions.
- Unsafe artifact content is not presented as trusted application content.
