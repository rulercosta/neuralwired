# Neuralwired Blog - Hugo Static Site

This is a static blog generated with Hugo, styled to match the exact look and feel of the original neuralwired blog. The site is completely static, requiring no backend, and is hosted on GitHub Pages.

## Project Structure

```
blog/
├── archetypes/
├── content/              # All blog posts and page content in Markdown
│   ├── posts/            # Blog posts directory
│   └── _index.md         # Homepage content
├── layouts/              # HTML templates
│   ├── _default/         # Default templates for posts and lists
│   ├── partials/         # Reusable template parts (header, footer)
│   └── index.html        # Homepage template
├── static/               # Static assets
│   └── css/              # CSS styling
│       └── style.css     # Main stylesheet
└── config.toml          # Hugo configuration
```

## Content Creation Workflow

### Writing Content

1. Create new posts as Markdown files in the `content/posts/` directory
2. Include front matter at the top of each file to define metadata:

```markdown
---
title: "Your Post Title"
date: 2023-06-20
featured: true  # Optional - displays in featured section
draft: false    # Set to true to exclude from production build
---

Your content here in Markdown format.
```

### Local Development

1. Install Hugo following the [official installation guide](https://gohugo.io/getting-started/installing/)
2. Run the development server:

```bash
cd blog
hugo server -D
```

3. Open your browser to `http://localhost:1313/` to see live preview
4. The site will automatically reload when you make changes

### Deployment Process

#### Using GitHub Pages

1. Push your changes to a GitHub repository
2. Set up GitHub Actions for automatic deployment:
   - Create `.github/workflows/hugo.yml` with appropriate build and deploy steps
   - Configure GitHub Pages to deploy from the branch generated by the workflow

#### Manual Deployment

1. Build the site:

```bash
hugo --minify
```

2. The complete static site will be generated in the `public/` directory
3. Upload these files to any web server or static hosting service

## Theme Customization

The theme is designed to match the original website exactly, with:

- Light/dark mode toggle that persists via localStorage
- Responsive design that works on mobile and desktop
- Monospace typography using Space Mono font

## Important Notes

- **No Backend Functionality**: This is a purely static implementation with no backend code
- **Content Management**: All content is managed through Markdown files in version control
- **Styling**: All CSS is based on the original website's styling for perfect visual consistency

## Future Enhancements

- Add search functionality using client-side JavaScript
- Implement categories and tags for better content organization
- Add RSS feed for subscription options

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
