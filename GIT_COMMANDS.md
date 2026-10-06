# Exact Git Commands

Run these commands from the directory containing the VeriRAG files.

```bash
git init
git branch -M main
git add .
git commit -m "feat: launch VeriRAG evidence-first RAG reliability gateway"

gh auth status || gh auth login
gh repo create veritrag \
  --public \
  --source=. \
  --remote=origin \
  --description "Evidence-first reliability gateway for RAG/LLM apps with hybrid retrieval, claim auditing, provenance and CI risk gates."

git push -u origin main

gh repo edit \
  --add-topic rag \
  --add-topic llm \
  --add-topic ai-safety \
  --add-topic retrieval-augmented-generation \
  --add-topic hallucination-detection \
  --add-topic mlops \
  --add-topic fastapi \
  --add-topic information-retrieval \
  --add-topic ai-observability \
  --add-topic developer-tools
```

After the first push, replace `YOUR_GITHUB_USERNAME` in the README badge and clone URL with your actual GitHub username, then commit:

```bash
git add README.md
git commit -m "docs: point README links to public repository"
git push
```
