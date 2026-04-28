---
name: readme
description: When given project details, generate a high-quality README.md file following a specific structure and style.
model: Gemini 3.1 Pro (Preview)
---

<!-- Tip: Use /create-prompt in chat to generate content with agent assistance -->

# README Generation Prompt (SaaS-Style)

Generate a high-quality, developer-focused `README.md` for a project.

Follow this EXACT structure and style:

---

## 1. Title Section

- Project name with an emoji
- One-line tagline
- Centered badges (tech stack, versions, etc.)

---

## 🚀 Overview

- Clear paragraph explaining what the project does
- Mention the problem it solves and why it matters

---

## ✨ Key Highlights

- 4–6 concise bullet points of standout features
- Focus on value and uniqueness

---

## 📋 Features

### Frontend Features (if applicable)

- 📝 Short, one-line descriptions
- Focus on UI/UX and user interactions

### Backend Features (if applicable)

- 🔐 Auth, APIs, security, scalability
- Keep each point crisp and technical

---

## 🛠️ Tech Stack

### Frontend

- List frameworks/libraries with links

### Backend

- APIs, databases, services

### DevOps / Tools

- Deployment, containerization, package managers

---

## 📦 Installation

### Prerequisites

- Required tools, versions

### Setup Steps

1. Clone repo
2. Install dependencies
3. Setup environment variables (`.env` example required)
4. Run project locally

---

## 📖 Usage Guide

Include real workflows:

- How to use core features step-by-step
- Example user flows (not generic text)

---

## 📁 Project Structure

Provide a clean folder tree with short explanations:
project-root/
├── src/ # core logic
├── components/ # UI components
├── utils/ # helper functions
└── ...

---

## 🧪 Development

- Run tests
- Build project
- Local development commands
- Docker (if applicable)

---

## 📄 License

- Clearly specify license

---

## STYLE RULES

- Use clean, modern markdown
- Keep it scannable (no long paragraphs)
- Use emojis sparingly but effectively
- Avoid vague marketing language
- Write like a senior developer documenting a real product
- Maintain consistent spacing and formatting
