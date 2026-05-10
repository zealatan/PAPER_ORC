# GitHub Upload Notes

Recommended files to commit:

```bash
git add README.md assets/banner.svg assets/architecture.svg assets/scorecard.svg
git commit -m "Add visual README for Paper Importance Agent"
git push
```

If this is a new repository:

```bash
git init
git add README.md assets/
git commit -m "Initial visual README"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

GitHub README visual tips:

1. Use `assets/*.svg` for colorful banners and diagrams.
2. Use Shields.io badges near the top.
3. Use Mermaid diagrams for simple workflows.
4. Use emojis for section scanning.
5. Avoid custom CSS because GitHub sanitizes most CSS/JS.
