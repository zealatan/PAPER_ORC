# How to Add the Roadmap Images to README.md

Copy these files into your repository:

```bash
mkdir -p assets
cp assets/papernav_project_roadmap_overview.png ./assets/
cp assets/milestone_1_citation_extraction_workflow.png ./assets/
```

Then copy the content of:

```text
README_ROADMAP_SECTION.md
```

into your repository `README.md`.

Commit:

```bash
git add README.md assets/papernav_project_roadmap_overview.png assets/milestone_1_citation_extraction_workflow.png
git commit -m "Add PaperNav roadmap diagrams to README"
git push
```
